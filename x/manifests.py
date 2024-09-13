"""
!!! manifests! get-manifest, _manifest.py
 - dumb dicts, root keys are 'types'
 - get put in _manifest.py, root level dict or smth
  - IMPORT files w comment
  - comment must immediately precede a global val setter
  - val is grabbed from imported module dict by name
  - value is repr'd somehow (roundtrip checked)
  - dumped in _manifest.py
 - # @omlish-manifest \n _CACHE_MANIFEST = {'cache': {'name': 'llm', …
 - also can do prechecks!

TODO:
 - subprocess interpreter
"""
import os.path
import re
import typing as ta

from omdev import findmagic


##


MANIFEST_MAGIC = '# @omlish-manifest'

_MANIFEST_GLOBAL_PAT = re.compile(r'^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=.*')


def handle_one(file: str, base: str) -> None:
    print((file, base))

    if not file.endswith('.py'):
        raise Exception(file)

    with open(os.path.join(base, file)) as f:
        src = f.read()

    names = set()
    lines = src.splitlines(keepends=True)
    for i, l in enumerate(lines):
        if l.startswith(MANIFEST_MAGIC):
            if (m := _MANIFEST_GLOBAL_PAT.match(nl := lines[i + 1])) is None:
                raise Exception(nl)
            names.add(m.groupdict()['name'])

    if not names:
        raise Exception('no manifests found')

    mod_name = file.rpartition('.')[0].replace(os.sep, '.')

    raise NotImplementedError


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
