import importlib.metadata
import io
import sys
import urllib.request
import xml.etree.ElementTree as ET  # noqa

from omlish import argparse as ap
from omlish import check

from ..cli import CliModule
from ..packaging.names import canonicalize_name
from ..packaging.requires import RequiresVariable
from ..packaging.requires import parse_requirement


PYPI_URL = 'https://pypi.org/'


class Cli(ap.Cli):
    @ap.command(
        ap.arg('package'),
    )
    def lookup_latest_version(self) -> None:
        pkg_name = check.non_empty_str(self.args.package)
        with urllib.request.urlopen(f'{PYPI_URL}rss/project/{pkg_name}/releases.xml') as resp:  # noqa
            rss = resp.read()
        doc = ET.parse(io.BytesIO(rss))  # noqa
        latest = check.not_none(doc.find('./channel/item/title')).text
        print(latest)

    @ap.command(
        ap.arg('file'),
        ap.arg('-w', '--write', action='store_true'),
        ap.arg('-q', '--quiet', action='store_true'),
    )
    def filter_dev_deps(self) -> None:
        with open(self.args.file) as f:
            src = f.read()

        out = []
        for l in src.splitlines(keepends=True):
            if l.startswith('-e'):
                continue
            out.append(l)

        new_src = ''.join(out)

        if not self.args.quiet:
            print(new_src)

        if self.args.write:
            with open(self.args.file, 'w') as f:
                f.write(new_src)

    @ap.command(
        ap.arg('path', nargs='*'),
    )
    def list_root_dists(self) -> None:
        # FIXME: track req extras - tuple[str, str] with ('pkg', '') as 'bare'?
        paths = self.args.path or sys.path

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

        for d in sorted(dists):
            if not uses_by_req.get(d):
                print(d)


# @omlish-manifest
_CLI_MODULE = CliModule('pip', __name__)


if __name__ == '__main__':
    Cli()()
