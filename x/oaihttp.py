import json
import urllib.request

from omdev.secrets import load_secrets
from omlish import http as hu


def _main() -> None:
    key = load_secrets().get('openai_api_key')

    with urllib.request.urlopen(urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            headers={k.decode('ascii'): v.decode('ascii') for k, v in {
                hu.consts.HEADER_CONTENT_TYPE: hu.consts.CONTENT_TYPE_JSON,
                hu.consts.HEADER_AUTH: hu.consts.format_bearer_auth_header(key.reveal()),
            }.items()},
            data=json.dumps(dict(
                model='gpt-4o-mini',
                messages=[
                    dict(
                        role='user',
                        content='Hi!',
                    ),
                ],
            )).encode('utf-8'),
    )) as resp:
        print(resp.read())


if __name__ == '__main__':
    _main()
