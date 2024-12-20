"""
TODO:
 - https://github.com/pypa/pip/blob/420435903ff2fc694d6950a47b896427ecaed78f/src/pip/_internal/req/req_file.py ?
"""
import contextlib
import os.path
import sys
import typing as ta

from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.formats import json

from ..cli import CliModule
from ..packaging import marshal as _  # noqa
from ..packaging.requires import ParsedRequirement
from ..packaging.requires import parse_requirement
from ..pip import get_root_dists
from ..pip import lookup_latest_package_version


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('package'),
    )
    def lookup_latest_version(self) -> None:
        print(lookup_latest_package_version(self.args.package))

    @ap.cmd(
        ap.arg('path', nargs='*'),
    )
    def list_root_dists(self) -> None:
        for d in get_root_dists(paths=self.args.path):
            print(d)

    @ap.cmd(
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

    @ap.cmd(
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
