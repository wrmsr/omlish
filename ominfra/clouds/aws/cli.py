from omlish.argparse import all as ap
from omlish.formats import json

from . import metadata


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('key', nargs='*'),
        ap.arg('--url'),
    )
    def metadata(self) -> None:
        md = metadata.read_metadata(
            self.args.key or metadata.DEFAULT_METADATA_KEYS,
            url=self.args.url or metadata.DEFAULT_METADATA_URL,
        )
        print(json.dumps_pretty(md))


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
