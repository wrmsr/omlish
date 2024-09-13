"""
!!! manifests! get-manifest, _manifest.py
 - dumb dicts, root keys are 'types'
 - get put in _manifest.py, root level dict or smth
  - IMPORT files w comment
  - comment must immediately precede a global val setter
  - val is grabbed from imported module dict by name
  - value is repr'd somehow (roundtrip checked) (naw, json lol)
  - dumped in _manifest.py
 - # @omlish-manifest \n _CACHE_MANIFEST = {'cache': {'name': 'llm', …
 - also can do prechecks!

TODO:
 - subprocess interpreter
"""
# @omlish-lite
import collections
import dataclasses as dc
import inspect
import json
import os.path
import re
import shlex
import subprocess
import sys
import typing as ta

from omlish.lite.cached import cached_nullary
from omdev import findmagic


##


@dc.dataclass(frozen=True)
class Origin:
    module: str
    attr: str

    file: str
    line: int


@dc.dataclass(frozen=True)
class Manifest(Origin):
    value: ta.Any


MANIFEST_MAGIC = '# @omlish-manifest'

_MANIFEST_GLOBAL_PAT = re.compile(r'^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=.*')


def _dump_module_manifests(spec: str, *attrs: str) -> None:
    import importlib
    import json

    mod = importlib.import_module(spec)

    out = {}
    for attr in attrs:
        manifest = getattr(mod, attr)

        manifest_json = json.dumps(manifest)
        rt_manifest = json.loads(manifest_json)

        if rt_manifest != manifest:
            raise Exception(f'Manifest failed to roundtrip: {manifest} != {rt_manifest}')

        out[attr] = rt_manifest

    out_json = json.dumps(out, indent=None, separators=(',', ':'))
    print(out_json)


@cached_nullary
def _payload_src() -> str:
    return inspect.getsource(_dump_module_manifests)


def handle_one(
        file: str,
        base: str,
        *,
        shell_wrap: bool = True,
) -> ta.Sequence[Manifest]:
    print((file, base))

    if not file.endswith('.py'):
        raise Exception(file)

    mod_name = file.rpartition('.')[0].replace(os.sep, '.')

    with open(os.path.join(base, file)) as f:
        src = f.read()

    origins: list[Origin] = []
    lines = src.splitlines(keepends=True)
    for i, l in enumerate(lines):
        if l.startswith(MANIFEST_MAGIC):
            if (m := _MANIFEST_GLOBAL_PAT.match(nl := lines[i + 1])) is None:
                raise Exception(nl)

            origins.append(Origin(
                module=mod_name,
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

    subproc_out = subprocess.check_output(args)

    sp_lines = subproc_out.decode().strip().splitlines()
    if len(sp_lines) != 1:
        raise Exception('Unexpected subprocess output')

    dct = json.loads(sp_lines[0])
    if set(dct) != set(attrs):
        raise Exception('Unexpected subprocess output keys')

    out: list[Manifest] = []

    for o in origins:
        manifest = dct[o.attr]

        out.append(Manifest(
            **dc.asdict(o),
            value=manifest,
        ))

    return out


##


# @omlish-manifest
_FOO_CACHE_MANIFEST = {'cache': {
    'name': 'foo',
}}


def _main() -> None:
    here = os.path.abspath(os.path.dirname(__file__))
    base = os.path.abspath(os.path.join(here, '..'))
    for f in findmagic.find_magic(
        [here],
        [MANIFEST_MAGIC],
        ['py'],
    ):
        handle_one(os.path.relpath(f, base), base)


if __name__ == '__main__':
    _main()
