import io
import urllib.request
import xml.etree.ElementTree as ET  # noqa

from omlish import argparse as ap
from omlish import check


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


if __name__ == '__main__':
    Cli()()
