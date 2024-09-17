import functools
import importlib.resources
import os.path
import typing as ta


class RelativeResource(ta.NamedTuple):
    name: str
    is_file: bool
    read_bytes: ta.Callable[[], bytes]


def get_relative_resources(
        path: str = '',
        *,
        globals: ta.Mapping[str, ta.Any] | None = None,  # noqa
        package: str | None = None,
        file: str | None = None,
) -> ta.Mapping[str, RelativeResource]:
    if globals is not None:
        if not package:
            package = globals.get('__package__')
        if not file:
            file = globals.get('__file__')

    #

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

    lst: list[RelativeResource] = []

    if package:
        pkg_parts = package.split('.')
        if num_up:
            pkg_parts = pkg_parts[:-num_up]
        anchor = '.'.join([*pkg_parts, *path_parts])
        for pf in importlib.resources.files(anchor).iterdir():
            lst.append(RelativeResource(
                name=pf.name,
                is_file=pf.is_file(),
                read_bytes=pf.read_bytes if pf.is_file() else None,  # type: ignore
            ))

    elif file:
        # path = os.path.dirname(file)
        # if prefix:
        #     path = os.path.join(path, prefix.replace('.', os.sep))
        #
        # def _read_file(fp: str) -> bytes:
        #     with open(fp, 'rb') as f:
        #         return f.read()
        #
        # for ff in os.listdir(path):
        #     ff = os.path.join(path, ff)
        #     lst.append(RelativeResource(
        #         name=os.path.basename(ff),
        #         is_file=os.path.isfile(ff),
        #         read_bytes=functools.partial(_read_file, ff),
        #     ))
        raise NotImplementedError

    else:
        raise RuntimeError('no package or file specified')

    return {r.name: r for r in lst}
