"""
TODO:
 - https://github.com/pypa/pip/blob/420435903ff2fc694d6950a47b896427ecaed78f/src/pip/_internal/req/req_file.py ?
"""
import contextlib
import importlib.metadata
import io
import os.path
import sys
import typing as ta
import urllib.request

from omlish import argparse as ap
from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from ..cli import CliModule
from ..packaging import marshal as _  # noqa
from ..packaging.names import canonicalize_name
from ..packaging.requires import ParsedRequirement
from ..packaging.requires import RequiresVariable
from ..packaging.requires import parse_requirement


if ta.TYPE_CHECKING:
    import xml.etree.ElementTree as ET  # noqa
else:
    ET = lang.proxy_import('xml.etree.ElementTree')


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

    @ap.command(
        ap.arg('files', nargs='*'),
        ap.arg('-r', '--follow-requirements', action='store_true'),
        ap.arg('-j', '--json', action='store_true'),
        ap.arg('-b', '--bare', action='store_true'),
    )
    def parse(self) -> None:
        def print_req(req: ParsedRequirement) -> None:
            if self.args.json:
                req_m = msh.marshal(req)
                print(json.dumps(req_m))

            elif self.args.bare:
                print(req.name)

            else:
                print(f'{req.name}{req.specifier or ""}')

        #

        seen_files: set[str] = set()

        def do_file(file: ta.TextIO | str) -> None:
            if isinstance(file, str) and file in seen_files:
                return

            with contextlib.ExitStack() as es:
                f: ta.TextIO
                if isinstance(file, str):
                    f = es.enter_context(open(file))
                else:
                    f = file

                for l in f:
                    if '#' in l:
                        l = l.partition('#')[0]

                    if not (l := l.strip()):
                        continue

                    if l.startswith('git+'):
                        continue  # FIXME

                    elif l.startswith('-r'):  # noqa
                        if self.args.follow_requirements:
                            base_dir = os.path.dirname(file) if isinstance(file, str) else '.'
                            r_file = os.path.join(base_dir, l[2:].strip())
                            do_file(r_file)

                    else:
                        req = parse_requirement(l)
                        print_req(req)

        if self.args.files:
            for file in self.args.files:
                do_file(file)
        else:
            do_file(sys.stdin)


# @omlish-manifest
_CLI_MODULE = CliModule('pip', __name__)


if __name__ == '__main__':
    Cli()()
