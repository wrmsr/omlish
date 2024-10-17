"""
https://github.com/chr15m/aish/blob/main/aish
"""
from omdev.secrets import load_secrets
from omlish import http as hu
from omlish.formats import json


def _main() -> None:
    key = load_secrets().get('openai_api_key')

    print(hu.request(
        'https://api.openai.com/v1/chat/completions',
        headers={
            hu.consts.HEADER_AUTH: hu.consts.format_basic_auth_header('', key.reveal()),
            hu.consts.HEADER_CONTENT_TYPE: hu.consts.CONTENT_TYPE_JSON,
        },
        data=json.dumps(dict(
            model='gpt-3.5-turbo',
            messages=[
                dict(
                    role='user',
                    content='Hi!',
                ),
            ],
        )).encode('utf-8'),
    ).data)


if __name__ == '__main__':
    _main()
