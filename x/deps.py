import importlib.metadata
import sys

from omdev.versioning.names import canonicalize_name
from omdev.versioning.versions import canonicalize_version


def _main() -> None:
    # TODO: https://github.com/pypa/packaging/blob/cf2cbe2aec28f87c6228a6fb136c27931c9af407/src/packaging/_parser.py#L65
    paths = sys.path
    for d in importlib.metadata.distributions(paths=paths):
        cn = canonicalize_name(d.metadata['Name'], validate=True)
        print(cn)
        for r in d.requires or []:
            v = canonicalize_version(r)
            print(v)
        print()


if __name__ == '__main__':
    _main()
