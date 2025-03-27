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
from omdev.packaging.specifiers import Specifier


def _main() -> None:
    dist_dct = {}
    for dist in importlib.metadata.distributions(paths=sys.path):
        dist_cn = canonicalize_name(dist.metadata['Name'], validate=True)
        if dist_cn in dist_dct:
            continue
        dist_dct[dist_cn] = dist

    #

    with open('pyproject.toml', 'rb') as f:
        dct = tomllib.load(f)

    pkgs = dct['tool']['omlish']['pyproject']['pkgs']

    for pkg in pkgs:
        pkg_about = importlib.import_module('.'.join([pkg, '__about__']))
        pkg_prj = pkg_about.Project

        pkg_opt_deps = {d for ds in pkg_prj.optional_dependencies.values() for d in ds}
        for opt_dep in sorted(pkg_opt_deps):
            opt_req = parse_requirement(opt_dep)
            opt_cn = canonicalize_name(opt_req.name, validate=True)
            opt_spec = Specifier(opt_req.specifier)

            opt_dist = dist_dct[opt_cn]
            opt_ver = opt_dist.version

            print((opt_dep, opt_spec, opt_ver))
            if not opt_spec.contains(opt_ver):
                print(f'{pkg} :: {opt_cn} : {opt_spec} ! {opt_ver}')


if __name__ == '__main__':
    _main()
