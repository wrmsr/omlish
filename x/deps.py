import importlib.metadata
import sys

from omdev.packaging.names import canonicalize_name
from omdev.packaging.requires import parse_requirement


def _main() -> None:
    paths = sys.path
    reqs_by_use = {}
    uses_by_req = {}
    for dist in importlib.metadata.distributions(paths=paths):
        use_cn = canonicalize_name(dist.metadata['Name'], validate=True)
        for req_str in dist.requires or []:
            req = parse_requirement(req_str)
            if req.extras:
                continue
            req_cn = canonicalize_name(req.name)
            reqs_by_use.setdefault(use_cn, set()).add(req_cn)
            uses_by_req.setdefault(req_cn, set()).add(use_cn)

    print()


if __name__ == '__main__':
    _main()
