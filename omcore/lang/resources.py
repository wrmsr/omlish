import dataclasses as dc
import functools
import os.path
import typing as ta

from .imports.proxy import proxy_import


if ta.TYPE_CHECKING:
    import importlib.resources as importlib_resources
else:
    importlib_resources = proxy_import('importlib.resources')


##


@dc.dataclass(frozen=True)
class ReadableResource:
    name: str
    is_file: bool
    read_bytes: ta.Callable[[], bytes]

    def read_text(self, encoding: str = 'utf-8') -> str:
        return self.read_bytes().decode(encoding)


def get_package_resources(anchor: str) -> ta.Mapping[str, ReadableResource]:
    lst: list[ReadableResource] = []

    for pf in importlib_resources.files(anchor).iterdir():
        lst.append(ReadableResource(
            name=pf.name,
            is_file=pf.is_file(),
            read_bytes=pf.read_bytes if pf.is_file() else None,  # type: ignore
        ))

    return {r.name: r for r in lst}


def get_relative_resources(
        path: str = '',
        *,
        globals: ta.Mapping[str, ta.Any] | None = None,  # noqa
        package: str | None = None,
        file: str | None = None,
) -> ta.Mapping[str, ReadableResource]:
    if globals is not None:
        if not package:
            package = globals.get('__package__')
        if not file:
            file = globals.get('__file__')

    #

    if os.sep in path:
        raise ValueError(path)  # noqa

    if not path.startswith('.'):
        path = '.' + path
    if set(path) - {'.'}:
        dot_pos = next(i for i in range(len(path)) if path[i] != '.')
        num_up = dot_pos - 1
        path_parts = path[dot_pos:].split('.')
    else:
        num_up = len(path) - 1
        path_parts = []

    #

    lst: list[ReadableResource] = []

    if package:
        pkg_parts = package.split('.')
        if num_up:
            pkg_parts = pkg_parts[:-num_up]
        anchor = '.'.join([*pkg_parts, *path_parts])
        for pf in importlib_resources.files(anchor).iterdir():
            lst.append(ReadableResource(
                name=pf.name,
                is_file=pf.is_file(),
                read_bytes=pf.read_bytes if pf.is_file() else None,  # type: ignore
            ))

    elif file:
        base_dir = os.path.dirname(file)
        dst_dir = os.path.join(
            base_dir,
            *(['..'] * num_up),
            *path_parts,
        )

        def _read_file(fp: str) -> bytes:
            with open(fp, 'rb') as f:
                return f.read()

        for ff in os.listdir(dst_dir):
            ff = os.path.join(dst_dir, ff)
            lst.append(ReadableResource(
                name=os.path.basename(ff),
                is_file=os.path.isfile(ff),
                read_bytes=functools.partial(_read_file, ff),
            ))

    else:
        raise RuntimeError('no package or file specified')

    return {r.name: r for r in lst}
