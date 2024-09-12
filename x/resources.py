import importlib.resources
import typing as ta


class RelativeResource(ta.NamedTuple):
    name: str
    is_file: bool
    read_bytes: ta.Callable[[], bytes]


def get_relative_resources(
        prefix: str | None = None,
        *,
        globals: ta.Mapping[str, ta.Any] | None = None,
        package: str | None = None,
        file: str | None = None,
) -> ta.Sequence[RelativeResource]:
    if globals is not None:
        if not package:
            package = globals.get('__package__')
        if not file:
            file = globals.get('__file__')

    ret: list[RelativeResource] = []

    if package:
        anchor = package
        if prefix is not None:
            anchor += '.' + prefix

        for f in importlib.resources.files(anchor).iterdir():
            ret.append(RelativeResource(
                name=f.name,
                is_file=f.is_file(),
                read_bytes=f.read_bytes if f.is_file() else None,
            ))

    else:
        raise NotImplementedError

    return ret


def _main() -> None:
    print(get_relative_resources('', globals=globals()))


if __name__ == '__main__':
    _main()
