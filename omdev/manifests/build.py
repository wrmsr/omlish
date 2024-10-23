"""
TODO:
 - separate build from cli
 - verify classes instantiate

See (entry_points):
 - https://github.com/pytest-dev/pluggy/blob/main/src/pluggy/_manager.py#L405
 - https://docs.pytest.org/en/7.1.x/how-to/writing_plugins.html#setuptools-entry-points
 - https://packaging.python.org/en/latest/specifications/entry-points/
 - https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
 - [project.entry-points.omlish-manifests] \n omdev = omdev
"""
# ruff: noqa: UP006 UP007
import argparse
import asyncio
import collections
import dataclasses as dc
import inspect
import itertools
import json
import multiprocessing as mp
import os.path
import re
import shlex
import subprocess
import sys
import time
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.json import json_dumps_pretty
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log

from .. import findmagic
from .load import ManifestLoader
from .types import Manifest
from .types import ManifestOrigin


T = ta.TypeVar('T')


##


MANIFEST_MAGIC = '# @omlish-manifest'

_MANIFEST_GLOBAL_PAT = re.compile(r'^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=.*')


def _dump_module_manifests(spec: str, *attrs: str) -> None:
    import collections.abc
    import dataclasses as dc  # noqa
    import importlib
    import json

    mod = importlib.import_module(spec)

    out = {}
    for attr in attrs:
        manifest = getattr(mod, attr)

        if dc.is_dataclass(manifest):
            cls = type(manifest)
            manifest_json = json.dumps(dc.asdict(manifest))  # type: ignore
            manifest_dct = json.loads(manifest_json)

            rt_manifest = cls(**manifest_dct)  # type: ignore
            if rt_manifest != manifest:
                raise Exception(f'Manifest failed to roundtrip: {manifest} -> {manifest_dct} != {rt_manifest}')

            key = f'${cls.__module__}.{cls.__qualname__}'
            out[attr] = {key: manifest_dct}

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

            out[attr] = {key: manifest_dct}

        else:
            raise TypeError(f'Manifest must be dataclass or mapping: {manifest!r}')

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

        origins: ta.List[ManifestOrigin] = []
        lines = src.splitlines(keepends=True)
        for i, l in enumerate(lines):
            if l.startswith(MANIFEST_MAGIC):
                if (m := _MANIFEST_GLOBAL_PAT.match(nl := lines[i + 1])) is None:
                    raise Exception(nl)

                origins.append(ManifestOrigin(
                    module='.'.join(['', *mod_name.split('.')[1:]]),
                    attr=m.groupdict()['name'],

                    file=file,
                    line=i + 1,
                ))

        if not origins:
            raise Exception('no manifests found')

        if (dups := [k for k, v in collections.Counter(o.attr for o in origins).items() if v > 1]):
            raise Exception(f'Duplicate attrs: {dups}')

        attrs = [o.attr for o in origins]

        subproc_src = '\n\n'.join([
            _payload_src(),
            f'_dump_module_manifests({mod_name!r}, {", ".join(repr(a) for a in attrs)})\n',
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

        dct = json.loads(sp_lines[0])
        if set(dct) != set(attrs):
            raise Exception('Unexpected subprocess output keys')

        out: ta.List[Manifest] = []

        for o in origins:
            value = dct[o.attr]

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

            out.append(Manifest(
                **dc.asdict(o),
                value=value,
            ))

        return out

    async def build_package_manifests(
            self,
            name: str,
    ) -> ta.List[Manifest]:
        pkg_dir = os.path.join(self._base, name)
        if not os.path.isdir(pkg_dir) or not os.path.isfile(os.path.join(pkg_dir, '__init__.py')):
            raise Exception(pkg_dir)

        files = sorted(findmagic.find_magic(
            [pkg_dir],
            [MANIFEST_MAGIC],
            ['py'],
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

    ldr = ManifestLoader()
    for entry in manifests_json:
        manifest = Manifest(**entry)
        [(key, value_dct)] = manifest.value.items()
        if key.startswith('$.'):
            key = f'${name}{key[1:]}'
        cls = ldr.load_cls(key)
        value = cls(**value_dct)  # noqa


##


if __name__ == '__main__':
    def _get_base(args) -> str:
        if args.base is not None:
            base = args.base
        else:
            base = os.getcwd()
        base = os.path.abspath(base)
        if not os.path.isdir(base):
            raise RuntimeError(base)
        return base

    def _gen_cmd(args) -> None:
        base = _get_base(args)

        jobs = args.jobs or int(max(mp.cpu_count() // 1.5, 1))
        builder = ManifestBuilder(
            base,
            jobs,
            write=args.write or False,
        )

        async def do():
            return await asyncio.gather(*[
                builder.build_package_manifests(pkg)
                for pkg in args.package
            ])

        mss = asyncio.run(do())
        if not args.quiet:
            for ms in mss:
                print(json_dumps_pretty([dc.asdict(m) for m in ms]))

    def _check_cmd(args) -> None:
        base = _get_base(args)

        for pkg in args.package:
            check_package_manifests(
                pkg,
                base,
            )

    def _main(argv=None) -> None:
        configure_standard_logging('INFO')

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        parser_gen = subparsers.add_parser('gen')
        parser_gen.add_argument('-b', '--base')
        parser_gen.add_argument('-w', '--write', action='store_true')
        parser_gen.add_argument('-q', '--quiet', action='store_true')
        parser_gen.add_argument('-j', '--jobs', type=int)
        parser_gen.add_argument('package', nargs='*')
        parser_gen.set_defaults(func=_gen_cmd)

        parser_check = subparsers.add_parser('check')
        parser_check.add_argument('-b', '--base')
        parser_check.add_argument('package', nargs='*')
        parser_check.set_defaults(func=_check_cmd)

        args = parser.parse_args(argv)
        if not getattr(args, 'func', None):
            parser.print_help()
        else:
            args.func(args)

    _main()
