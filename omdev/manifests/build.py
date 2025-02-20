# ruff: noqa: UP006 UP007
"""
TODO:
 - verify classes instantiate
 - embed in pyproject
 - roundtrip flexibility regarding json-ness - tuples vs lists vs sets vs frozensets etc

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
from omlish.lite.logs import log
from omlish.manifests.base import ModAttrManifest
from omlish.manifests.load import MANIFEST_LOADER
from omlish.manifests.types import Manifest
from omlish.manifests.types import ManifestOrigin

from .. import magic


T = ta.TypeVar('T')


##


MANIFEST_MAGIC_KEY = '@omlish-manifest'


_MANIFEST_GLOBAL_PATS = tuple(re.compile(p) for p in [
    # _FOO_MANIFEST = FooManifest(...
    r'^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=.*',

    # class _FOO_MANIFEST(StaticFooManifest): ...
    r'^class (?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(\(|$)',
])


def extract_manifest_target_name(line: str) -> str:
    for pat in _MANIFEST_GLOBAL_PATS:
        if (m := pat.match(line)) is not None:
            return m.groupdict()['name']
    raise Exception(line)


_INLINE_MANIFEST_CLS_NAME_PAT = re.compile(r'^(?P<cls_name>[_a-zA-Z][_a-zA-Z0-9.]*)\s*(?P<cls_args>\()?')


##


def _dump_module_manifests(spec: str, *targets: dict) -> None:
    import collections.abc
    import dataclasses as dc  # noqa
    import importlib
    import json

    mod = importlib.import_module(spec)

    out = []
    for target in targets:
        origin = target['origin']

        if target['kind'] == 'attr':
            attr = target['attr']
            manifest = getattr(mod, attr)

            if dc.is_dataclass(manifest):
                # Support static dataclasses
                if isinstance(manifest, type):
                    manifest = manifest()

                cls = type(manifest)
                manifest_json = json.dumps(dc.asdict(manifest))
                manifest_dct = json.loads(manifest_json)

                rt_manifest = cls(**manifest_dct)
                if rt_manifest != manifest:
                    raise Exception(f'Manifest failed to roundtrip: {manifest} => {manifest_dct} != {rt_manifest}')

                key = f'${cls.__module__}.{cls.__qualname__}'
                out_value = {key: manifest_dct}

            elif isinstance(manifest, collections.abc.Mapping):
                [(key, manifest_dct)] = manifest.items()
                if not key.startswith('$'):  # noqa
                    raise Exception(f'Bad key: {key}')

                if not isinstance(manifest_dct, collections.abc.Mapping):
                    raise Exception(f'Bad value: {manifest_dct}')

                manifest_json = json.dumps(manifest_dct)
                rt_manifest_dct = json.loads(manifest_json)
                if manifest_dct != rt_manifest_dct:
                    raise Exception(f'Manifest failed to roundtrip: {manifest_dct} != {rt_manifest_dct}')

                out_value = {key: manifest_dct}

            else:
                raise TypeError(f'Manifest must be dataclass or mapping: {manifest!r}')

        else:
            raise ValueError(target)

        out.append({
            **origin,
            'value': out_value,
        })

    out_json = json.dumps(out, indent=None, separators=(',', ':'))
    print(out_json)


@cached_nullary
def _payload_src() -> str:
    return inspect.getsource(_dump_module_manifests)


class ManifestBuilder:
    def __init__(
            self,
            base: str,
            concurrency: int = 8,
            *,
            write: bool = False,
    ) -> None:
        super().__init__()

        self._base = base
        self._sem = asyncio.Semaphore(concurrency)
        self._write = write

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

    async def build_module_manifests(
            self,
            file: str,
            *,
            shell_wrap: bool = True,
            warn_threshold_s: ta.Optional[float] = 1.,
    ) -> ta.Sequence[Manifest]:
        log.info('Extracting manifests from file %s', file)

        if not file.endswith('.py'):
            raise Exception(file)

        mod_name = file.rpartition('.')[0].replace(os.sep, '.')
        mod_base = mod_name.split('.')[0]
        if mod_base != (first_dir := file.split(os.path.sep)[0]):
            raise Exception(f'Unexpected module base: {mod_base=} != {first_dir=}')

        with open(os.path.join(self._base, file)) as f:  # noqa
            src = f.read()

        lines = src.splitlines(keepends=True)

        magics = magic.find_magic(
            magic.PY_MAGIC_STYLE,
            lines,
            file=file,
            keys={MANIFEST_MAGIC_KEY},
        )

        origins: ta.List[ManifestOrigin] = []
        targets: ta.List[dict] = []
        for m in magics:
            if m.body:
                pat_match = check.not_none(_INLINE_MANIFEST_CLS_NAME_PAT.match(m.body))
                cls_name = check.non_empty_str(pat_match.groupdict()['cls_name'])
                has_cls_args = bool(pat_match.groupdict().get('cls_args'))  # Noqa
                cls = import_attr(cls_name)
                check.issubclass(cls, ModAttrManifest)
                attr_name = extract_manifest_target_name(lines[m.end_line])

                raise NotImplementedError(m.body)

            else:
                nl = lines[m.end_line]
                attr_name = extract_manifest_target_name(nl)

                origin = ManifestOrigin(
                    module='.'.join(['', *mod_name.split('.')[1:]]),
                    attr=attr_name,

                    file=file,
                    line=m.start_line,
                )

                origins.append(origin)
                targets.append({
                    'origin': dc.asdict(origin),
                    'kind': 'attr',
                    'attr': attr_name,
                })

        if not origins:
            raise Exception('no manifests found')

        if (dups := [k for k, v in collections.Counter(o.attr for o in origins).items() if v > 1]):
            raise Exception(f'Duplicate attrs: {dups}')

        subproc_src = '\n\n'.join([
            _payload_src(),
            f'_dump_module_manifests({mod_name!r}, {", ".join(repr(tgt) for tgt in targets)})\n',
        ])

        args = [
            sys.executable,
            '-c',
            subproc_src,
        ]

        if shell_wrap:
            args = ['sh', '-c', ' '.join(map(shlex.quote, args))]

        start_time = time.time()

        proc = await asyncio.create_subprocess_exec(*args, stdout=subprocess.PIPE)
        subproc_out, _ = await proc.communicate()
        if proc.returncode:
            raise Exception('Subprocess failed')

        end_time = time.time()

        if warn_threshold_s is not None and (elapsed_time := (end_time - start_time)) >= warn_threshold_s:
            log.warning('Manifest extraction took a long time: %s, %.2f s', file, elapsed_time)

        sp_lines = subproc_out.decode().strip().splitlines()
        if len(sp_lines) != 1:
            raise Exception('Unexpected subprocess output')

        sp_outs = json.loads(sp_lines[0])
        # FIXME:
        # if set(dct) != set(attrs):
        #     raise Exception('Unexpected subprocess output keys')

        out: ta.List[Manifest] = []
        for sp_out in sp_outs:
            value = sp_out['value']

            if not (
                    isinstance(value, ta.Mapping) and
                    len(value) == 1 and
                    all(isinstance(k, str) and k.startswith('$') and len(k) > 1 for k in value)
            ):
                raise TypeError(f'Manifests must be mappings of strings starting with $: {value!r}')

            [(key, value_dct)] = value.items()
            kb, _, kr = key[1:].partition('.')  # noqa
            if kb == mod_base:  # noqa
                key = f'$.{kr}'
                value = {key: value_dct}

            out.append(Manifest(**{
                **sp_out,
                **dict(value=value),
            }))

        return out

    async def build_package_manifests(
            self,
            name: str,
    ) -> ta.List[Manifest]:
        pkg_dir = os.path.join(self._base, name)
        if not os.path.isdir(pkg_dir) or not os.path.isfile(os.path.join(pkg_dir, '__init__.py')):
            raise Exception(pkg_dir)

        files = sorted(magic.find_magic_files(
            magic.PY_MAGIC_STYLE,
            [pkg_dir],
            keys=[MANIFEST_MAGIC_KEY],
        ))
        manifests: ta.List[Manifest] = list(itertools.chain.from_iterable(await asyncio.gather(*[
            self._spawn(
                self.build_module_manifests,
                os.path.relpath(file, self._base),
            )
            for file in files
        ])))

        if self._write:
            with open(os.path.join(pkg_dir, '.manifests.json'), 'w') as f:  # noqa
                f.write(json_dumps_pretty([dc.asdict(m) for m in manifests]))
                f.write('\n')

        return manifests


##


def check_package_manifests(
        name: str,
        base: str,
) -> None:
    pkg_dir = os.path.join(base, name)
    if not os.path.isdir(pkg_dir) or not os.path.isfile(os.path.join(pkg_dir, '__init__.py')):
        raise Exception(pkg_dir)

    manifests_file = os.path.join(pkg_dir, '.manifests.json')
    if not os.path.isfile(manifests_file):
        raise Exception(f'No manifests file: {manifests_file}')

    with open(manifests_file) as f:
        manifests_json = json.load(f)

    for entry in manifests_json:
        manifest = Manifest(**entry)
        [(key, value_dct)] = manifest.value.items()
        if key.startswith('$.'):
            key = f'${name}{key[1:]}'
        cls = MANIFEST_LOADER.load_cls(key)
        value = cls(**value_dct)  # noqa
