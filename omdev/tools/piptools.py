import io
import urllib.request
import xml.etree.ElementTree as ET  # noqa

from omlish import argparse as ap
from omlish import check

from ..cli import CliModule


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


# @omlish-manifest
_CLI_MODULE = CliModule('pip', __name__)


if __name__ == '__main__':
    Cli()()
