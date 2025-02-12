"""
TODO:
 - move to pyproject
 - pyproject api!
"""
import importlib.metadata
import sys
import tomllib

from omdev.packaging.names import canonicalize_name
from omdev.packaging.requires import parse_requirement


def _main() -> None:
    dist_dct = {
        canonicalize_name(dist.metadata['Name'], validate=True): dist
        for dist in importlib.metadata.distributions(paths=sys.path)
    }
    for dist_cn, dist in sorted(dist_dct.items(), key=lambda t: t[0]):
        print(f'{dist.name} {dist.version}')

    print()

    #

    with open('pyproject.toml', 'rb') as f:
        dct = tomllib.load(f)

    pkgs = dct['tool']['omlish']['pyproject']['pkgs']

    for pkg in pkgs:
        print(pkg)

        pkg_about = importlib.import_module('.'.join([pkg, '__about__']))
        pkg_prj = pkg_about.Project
        pkg_opt_deps = {d for ds in pkg_prj.optional_dependencies.values() for d in ds}
        for opt_dep in sorted(pkg_opt_deps):
            opt_req = parse_requirement(opt_dep)
            print(opt_req)

        print()


if __name__ == '__main__':
    _main()
