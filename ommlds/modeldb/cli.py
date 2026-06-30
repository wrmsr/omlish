"""
https://models.dev/
https://github.com/anomalyco/models.dev
"""
import bz2
import os.path
import typing as ta
import urllib.request

from omlish.argparse import all as ap
from omlish.formats.json import all as json

from .cache import load_providers
from .cache import load_providers_raw


##


MODELS_URL = 'https://models.dev/api.json'


def fetch_models(url: str | None = None) -> dict[str, dict[str, ta.Any]]:
    if url is None:
        url = MODELS_URL

    with urllib.request.urlopen(urllib.request.Request(  # noqa
            url,
            headers={
                'User-Agent': 'curl/8.7.1',
            },
    )) as f:
        src = f.read()

    models = json.loads(src.decode('utf-8'))
    return models


##


class Cli(ap.Cli):
    @ap.cmd()
    def fetch(self) -> None:
        models = fetch_models()

        compressed = bz2.compress(json.dumps_compact(models).encode('utf-8'))

        cache_file = os.path.join(os.path.dirname(__file__), 'cache.json.bz2')
        with open(cache_file, 'wb') as f:
            f.write(compressed)

    @ap.cmd(
        ap.arg('-m', '--marshal', action='store_true'),
    )
    def dump(self) -> None:
        dct: ta.Any = load_providers() if self.args.marshal else load_providers_raw()

        print(json.dumps_pretty(dct))


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
