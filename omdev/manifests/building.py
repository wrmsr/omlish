"""
TODO:
 - verify classes instantiate
 - embed in pyproject
 - roundtrip flexibility regarding json-ness - tuples vs lists vs sets vs frozensets etc
 - kill _MANIFEST_GLOBAL_PATS lol, ast walk
  - garbage skip_pat doesn't handle multiline decos, etc
 - relative paths
 - is this lite? or not?
 - can this run externally? or not? what does it have to import?
  - has to import manifest classes, but not modules with manifest magics
 - !! can make lite / amalg / embeddable with 'manifest base class markers':
  - rather than issubclass(cls, ModAttrManifest), can do if cls.__omlish_manifest_class__ == 'mod_attr'
   - reject unknowns
   - can analyze statically

See (entry_points):
 - https://github.com/pytest-dev/pluggy/blob/main/src/pluggy/_manager.py#L405
 - https://docs.pytest.org/en/7.1.x/how-to/writing_plugins.html#setuptools-entry-points
 - https://packaging.python.org/en/latest/specifications/entry-points/
 - https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
 - [project.entry-points.omlish-manifests] \n omdev = omdev
"""
import asyncio
import collections
import dataclasses as dc
import inspect
import itertools
import json
import os.path
import re
import shlex
import subprocess
import sys
import time
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.imports import import_attr
from omlish.lite.json import json_dumps_pretty
from omlish.logs.modules import get_module_logger
from omlish.manifests.base import ModAttrManifest
from omlish.manifests.globals import GlobalManifestLoader
from omlish.manifests.types import Manifest
from omlish.manifests.types import ManifestOrigin

from .. import magic


T = ta.TypeVar('T')

ManifestDumperTarget = ta.Union['InlineManifestDumperTarget', 'AttrManifestDumperTarget']  # ta.TypeAlias


log = get_module_logger(globals())  # noqa


##


MANIFEST_MAGIC_KEY = '@omlish-manifest'


_IDENT_PAT_PART = r'[A-Za-z_][A-Za-z0-9_]*'
_NAME_PAT_PART = rf'(?P<name>{_IDENT_PAT_PART})'


@dc.dataclass(frozen=True)
class _ManifestGlobalPat:
    name_pat: re.Pattern
    skip_pat: re.Pattern | None = None


_MANIFEST_GLOBAL_PATS: ta.Sequence[_ManifestGlobalPat] = [
    _ManifestGlobalPat(re.compile(rf'^{_NAME_PAT_PART}\s*=.*')),
    _ManifestGlobalPat(re.compile(rf'^class {_NAME_PAT_PART}\s*(\(|:|$)'), re.compile(r'^[#@\s].*')),
    _ManifestGlobalPat(re.compile(rf'^{_NAME_PAT_PART}:\s+(ta\.|typing\.|)?TypeAlias\s+=.*')),
]


def extract_manifest_target_name(lines: ta.Sequence[str], start_idx: int) -> str:
    check.not_isinstance(lines, str)
    for mgp in _MANIFEST_GLOBAL_PATS:
        cur_idx = start_idx
        while cur_idx < len(lines):
            if (m := mgp.name_pat.match(lines[cur_idx])) is not None:
                return m.groupdict()['name']
            if mgp.skip_pat is None or not mgp.skip_pat.match(lines[cur_idx]):
                break
            cur_idx += 1
    raise Exception(lines[start_idx])


_INLINE_MANIFEST_CLS_NAME_PAT = re.compile(r'^(?P<cls_name>[_a-zA-Z][_a-zA-Z0-9.]*)\s*(?P<cls_args>\()?')


##


class InlineManifestDumperTarget(ta.TypedDict):
    origin: ta.Mapping[str, ta.Any]
    kind: ta.Literal['inline']
    cls_mod_name: str
    cls_qualname: str
    init_src: str
    kwargs: ta.Mapping[str, ta.Any]


class AttrManifestDumperTarget(ta.TypedDict):
    origin: ta.Mapping[str, ta.Any]
    kind: ta.Literal['attr']
    attr: str


##


@cached_nullary
def _module_manifest_dumper_payload_src() -> str:
    from . import _dumping
    return inspect.getsource(_dumping)


class ManifestBuilder:
    def __init__(
            self,
            base_dir: str,
            concurrency: int = 8,
            *,
            subprocess_kwargs: ta.Mapping[str, ta.Any] | None = None,
            module_dumper_payload_src: str | None = None,
    ) -> None:
        super().__init__()

        self._base_dir = base_dir
        self._subprocess_kwargs = subprocess_kwargs
        self._module_dumper_payload_src = module_dumper_payload_src

        self._sem = asyncio.Semaphore(concurrency)

    #

    @dc.dataclass(frozen=True)
    class FileModule:
        file: str

        mod_name: str
        mod_base: str

    def build_file_module(self, file: str) -> FileModule:
        if not file.endswith('.py'):
            raise Exception(file)

        mod_name = file.rpartition('.')[0].replace(os.sep, '.')
        mod_base = mod_name.split('.')[0]
        if mod_base != (first_dir := file.split(os.path.sep)[0]):
            raise Exception(f'Unexpected module base: {mod_base=} != {first_dir=}')

        return ManifestBuilder.FileModule(
            file=file,

            mod_name=mod_name,
            mod_base=mod_base,
        )

    #

    def collect_module_manifest_targets(self, fm: FileModule) -> list[ManifestDumperTarget]:
        with open(os.path.join(self._base_dir, fm.file)) as f:  # noqa
            src = f.read()

        lines = src.splitlines(keepends=True)

        def prepare(s: str) -> ta.Any:
            if s.startswith('$.'):
                s = f'{fm.mod_base}.{s[2:]}'
            elif s.startswith('.'):
                # s = f'{fm.mod_base}.{s[2:]}'
                raise NotImplementedError
            return magic.py_compile_magic_preparer(s)

        magics = magic.find_magic(
            magic.PY_MAGIC_STYLE,
            lines,
            file=fm.file,
            keys={MANIFEST_MAGIC_KEY},
            preparer=prepare,
        )

        origins: list[ManifestOrigin] = []
        targets: list[ManifestDumperTarget] = []
        for m in magics:
            if m.body:
                body = m.body
                if body.startswith('$.'):
                    body = f'{fm.mod_base}.{body[2:]}'
                elif body.startswith('.'):
                    # body = f'{fm.mod_base}.{body[2:]}'
                    raise NotImplementedError

                pat_match = check.not_none(_INLINE_MANIFEST_CLS_NAME_PAT.match(body))
                cls_name = check.non_empty_str(pat_match.groupdict()['cls_name'])
                has_cls_args = bool(pat_match.groupdict().get('cls_args'))

                cls = check.isinstance(import_attr(cls_name), type)
                check.state(dc.is_dataclass(cls))

                cls_mod_name = cls.__module__
                cls_qualname = cls.__qualname__
                cls_reload = sys.modules[cls_mod_name]
                for p in cls_qualname.split('.'):
                    cls_reload = getattr(cls_reload, p)
                check.is_(cls_reload, cls)

                if has_cls_args:
                    inl_init_src = body[len(cls_name):]
                else:
                    inl_init_src = '()'

                inl_kw: dict = {}

                if issubclass(cls, ModAttrManifest):
                    attr_name = extract_manifest_target_name(lines, m.end_line)
                    inl_kw.update({
                        'module': fm.mod_name,
                        'attr': attr_name,
                    })

                origin = ManifestOrigin(
                    module='.'.join(['', *fm.mod_name.split('.')[1:]]),
                    attr=None,

                    file=fm.file,
                    line=m.start_line,
                )

                origins.append(origin)
                targets.append({
                    'origin': dc.asdict(origin),  # noqa
                    'kind': 'inline',
                    'cls_mod_name': cls_mod_name,
                    'cls_qualname': cls_qualname,
                    'init_src': inl_init_src,
                    'kwargs': inl_kw,
                })

            else:
                attr_name = extract_manifest_target_name(lines, m.end_line)

                origin = ManifestOrigin(
                    module='.'.join(['', *fm.mod_name.split('.')[1:]]),
                    attr=attr_name,

                    file=fm.file,
                    line=m.start_line,
                )

                origins.append(origin)
                targets.append({
                    'origin': dc.asdict(origin),  # noqa
                    'kind': 'attr',
                    'attr': attr_name,
                })

        if not origins:
            raise Exception('no manifests found')

        if (dups := [k for k, v in collections.Counter(o.attr for o in origins if o.attr is not None).items() if v > 1]):  # noqa
            raise Exception(f'Duplicate attrs: {dups}')

        return targets

    #

    async def _dump_module_manifests(
            self,
            fm: FileModule,
            targets: ta.Sequence[ManifestDumperTarget],
            *,
            shell_wrap: bool = True,
            warn_threshold_s: float | None = 1.,
    ):
        dumper_payload_src: str
        if self._module_dumper_payload_src is not None:
            dumper_payload_src = self._module_dumper_payload_src
        else:
            dumper_payload_src = _module_manifest_dumper_payload_src()

        subproc_src = '\n\n'.join([
            dumper_payload_src,
            f'_ModuleManifestDumper({fm.mod_name!r})({", ".join(repr(tgt) for tgt in targets)})\n',
        ])

        args = [
            sys.executable,
            '-c',
            subproc_src,
        ]

        if shell_wrap:
            args = ['sh', '-c', ' '.join(map(shlex.quote, args))]

        start_time = time.time()

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            **(self._subprocess_kwargs or {}),
        )

        subproc_out, _ = await proc.communicate()
        if proc.returncode:
            raise Exception('Subprocess failed')

        end_time = time.time()

        if warn_threshold_s is not None and (elapsed_time := (end_time - start_time)) >= warn_threshold_s:
            log.warning('Manifest extraction took a long time: %s, %.2f s', fm.file, elapsed_time)

        sp_lines = subproc_out.decode().strip().splitlines()
        if len(sp_lines) != 1:
            raise Exception('Unexpected subprocess output')

        sp_outs = json.loads(sp_lines[0])
        return sp_outs

    def _process_module_dump_output(
            self,
            fm: FileModule,
            sp_outs: ta.Sequence[ta.Mapping[str, ta.Any]],
    ) -> list[Manifest]:
        out: list[Manifest] = []
        for sp_out in sp_outs:
            value = sp_out['value']

            if not (
                    isinstance(value, ta.Mapping) and
                    len(value) == 1 and
                    all(isinstance(k, str) and k.startswith('!') and len(k) > 1 for k in value)
            ):
                raise TypeError(f'Manifest values must be mappings of strings starting with !: {value!r}')

            [(key, value_dct)] = value.items()
            kb, _, kr = key[1:].partition('.')  # noqa
            if kb == fm.mod_base:  # noqa
                key = f'!.{kr}'
                value = {key: value_dct}

            out.append(Manifest(**{
                **sp_out,
                **dict(value=value),
            }))

        return out

    #

    async def build_module_manifests(self, file: str) -> ta.Sequence[Manifest]:
        log.info('Extracting manifests from file %s', file)

        fm = self.build_file_module(file)

        targets = self.collect_module_manifest_targets(fm)

        sp_outs = await self._dump_module_manifests(fm, targets)

        # FIXME:
        # if set(dct) != set(attrs):
        #     raise Exception('Unexpected subprocess output keys')

        out = self._process_module_dump_output(fm, sp_outs)

        return out

    #

    async def _spawn(self, fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T:
        await self._sem.acquire()
        try:
            try:
                return await fn(*args, **kwargs)
            except Exception:  # noqa
                log.exception('Exception in task: %s, %r, %r', fn, args, kwargs)
                raise
        finally:
            self._sem.release()

    async def build_package_manifests(
            self,
            name: str,
            *,
            write: bool = False,
    ) -> list[Manifest]:
        pkg_dir = os.path.join(self._base_dir, name)
        if not os.path.isdir(pkg_dir) or not os.path.isfile(os.path.join(pkg_dir, '__init__.py')):
            raise Exception(pkg_dir)

        files = sorted(magic.find_magic_files(
            magic.PY_MAGIC_STYLE,
            [pkg_dir],
            keys=[MANIFEST_MAGIC_KEY],
        ))
        manifests: list[Manifest] = list(itertools.chain.from_iterable(await asyncio.gather(*[
            self._spawn(
                self.build_module_manifests,
                os.path.relpath(file, self._base_dir),
            )
            for file in files
        ])))

        if write:
            with open(os.path.join(pkg_dir, '.omlish-manifests.json'), 'w') as f:  # noqa
                f.write(json_dumps_pretty([dc.asdict(m) for m in manifests]))
                f.write('\n')

        return manifests


##


def check_package_manifests(
        name: str,
        base_dir: str,
) -> None:
    pkg_dir = os.path.join(base_dir, name)
    if not os.path.isdir(pkg_dir) or not os.path.isfile(os.path.join(pkg_dir, '__init__.py')):
        raise Exception(pkg_dir)

    manifests_file = os.path.join(pkg_dir, '.omlish-manifests.json')
    if not os.path.isfile(manifests_file):
        raise Exception(f'No manifests file: {manifests_file}')

    with open(manifests_file) as f:
        manifests_json = json.load(f)

    for entry in manifests_json:
        manifest = Manifest(**entry)
        [(key, value_dct)] = manifest.value.items()
        if key.startswith('!.'):
            key = f'!{name}{key[1:]}'
        cls = GlobalManifestLoader.instance()._load_class(key)  # noqa
        value = GlobalManifestLoader.instance()._instantiate_value(cls, **value_dct)  # noqa
