# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - use ..text.mangle
"""


#


def mangle_path(path: str) -> str:
    if not path.startswith('/'):
        raise ValueError('Only absolute Unix paths are supported')
    return (
        path
        .replace('_', '__')
        .replace('/', '_')
    )


def unmangle_path(mangled: str) -> str:
    if '/' in mangled:
        raise ValueError("Mangled paths should not contain '/'")
    return (
        mangled
        .replace('_', '/')
        .replace('//', '_')
    )
