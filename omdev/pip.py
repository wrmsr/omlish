import importlib.metadata
import json
import sys
import typing as ta
import urllib.request

from omlish import check

from .packaging.names import canonicalize_name
from .packaging.requires import RequiresVariable
from .packaging.requires import parse_requirement


##


DEFAULT_PYPI_URL = 'https://pypi.org/'


def lookup_latest_package_version(
        package: str,
        *,
        pypi_url: str = DEFAULT_PYPI_URL,
) -> str:
    pkg_name = check.non_empty_str(package)
    with urllib.request.urlopen(f'{pypi_url.rstrip("/")}/pypi/{pkg_name}/json') as resp:  # noqa
        buf = resp.read()
    # https://github.com/python/cpython/blob/51d4bf1e0e5349090da72721c865b6c2b28277f3/Tools/scripts/checkpip.py
    dct = json.loads(buf.decode('utf-8'))
    return check.non_empty_str(dct['info']['version'])


##


def get_root_dists(
        *,
        paths: ta.Iterable[str] | None = None,
) -> ta.Sequence[str]:
    # FIXME: track req extras - tuple[str, str] with ('pkg', '') as 'bare'?
    if paths is None:
        paths = sys.path

    dists: set[str] = set()
    reqs_by_use: dict[str, set[str]] = {}
    uses_by_req: dict[str, set[str]] = {}
    for dist in importlib.metadata.distributions(paths=paths):
        dist_cn = canonicalize_name(dist.metadata['Name'], validate=True)
        if dist_cn in dists:
            # raise NameError(dist_cn)
            # print(f'!! duplicate dist: {dist_cn}', file=sys.stderr)
            continue

        dists.add(dist_cn)
        for req_str in dist.requires or []:
            req = parse_requirement(req_str)

            if any(v.value == 'extra' for m in req.marker or [] if isinstance(v := m[0], RequiresVariable)):
                continue

            req_cn = canonicalize_name(req.name)
            reqs_by_use.setdefault(dist_cn, set()).add(req_cn)
            uses_by_req.setdefault(req_cn, set()).add(dist_cn)

    roots: list[str] = []
    for d in sorted(dists):
        if not uses_by_req.get(d):
            roots.append(d)

    return roots
