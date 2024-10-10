"""
https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list?apix=true
https://google.aip.dev/127
"""
import urllib.request

from omdev.secrets import load_secrets
from omlish.formats import json


def _main() -> None:
    sec = load_secrets()
    cse_id = sec.get('google_cse_id')
    cse_api_key = sec.get('google_cse_api_key')

    with urllib.request.urlopen(
        f'https://www.googleapis.com/customsearch/v1'
        f'?key={cse_api_key.reveal()}'
        f'&cx={cse_id.reveal()}'
        # f':omuauf_lfve'
        f'&q=lectures'
    ) as resp:
        out = resp.read()

    dct = json.loads(out.decode('utf-8'))
    print(json.dumps_pretty(dct))


if __name__ == '__main__':
    _main()
