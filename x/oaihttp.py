r"""
https://github.com/chr15m/aish/blob/main/aish

curl "https://api.openai.com/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Write a haiku that explains the concept of recursion."
            }
        ]
    }'

{
  "frequency_penalty": 0.0,
  "max_tokens": 64,
  "messages": [
    {
      "content": "Is water dry?",
      "role": "user"
    }
  ],
  "model": "gpt-4o",
  "presence_penalty": 0.0,
  "stream": false,
  "temperature": 0.1,
  "top_p": 1
}
"""
import urllib.request

from omdev.secrets import load_secrets
from omlish import http as hu
from omlish.formats import json


def _main() -> None:
    key = load_secrets().get('openai_api_key')

    url = 'https://api.openai.com/v1/chat/completions'

    dct = dict(
        model='gpt-4o-mini',
        messages=[
            dict(
                role='user',
                content='Hi!',
            ),
        ],
    )
    data = json.dumps(dct).encode('utf-8')

    headers = {
        hu.consts.HEADER_CONTENT_TYPE: hu.consts.CONTENT_TYPE_JSON,
        hu.consts.HEADER_AUTH: hu.consts.format_bearer_auth_header(key.reveal()),
    }

    print(hu.request(
        url,
        headers=headers,
        data=data,
    ).data)


if __name__ == '__main__':
    _main()
