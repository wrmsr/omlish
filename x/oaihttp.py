"""
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

{
  "host": "api.openai.com",
  "accept-encoding": "gzip, deflate",
  "connection": "keep-alive",
  "accept": "application/json",
  "content-type": "application/json",
  "user-agent": "OpenAI/Python 1.52.0",
  "x-stainless-lang": "python",
  "x-stainless-package-version": "1.52.0",
  "x-stainless-os": "MacOS",
  "x-stainless-arch": "arm64",
  "x-stainless-runtime": "CPython",
  "x-stainless-runtime-version": "3.12.7",
  "authorization": "Bearer ...",
  "x-stainless-async": "false",
  "x-stainless-retry-count": "0",
  "content-length": "197"
}
"""
import urllib.request

from omdev.secrets import load_secrets
from omlish import http as hu
from omlish.formats import json


def _main() -> None:
    key = load_secrets().get('openai_api_key')

    with urllib.request.urlopen(urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            headers={
                hu.consts.HEADER_CONTENT_TYPE.decode(): hu.consts.CONTENT_TYPE_JSON.decode(),
                hu.consts.HEADER_AUTH.decode(): hu.consts.format_bearer_auth_header(key.reveal()),
            },
            data="""{
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
            }""".encode('utf-8'),
        ),
    ) as resp:
        print(resp.read())

    print(hu.request(
        'https://api.openai.com/v1/chat/completions',
        headers={
            hu.consts.HEADER_AUTH: hu.consts.format_bearer_auth_header(key.reveal()),
            hu.consts.HEADER_CONTENT_TYPE: hu.consts.CONTENT_TYPE_JSON,
        },
        data=json.dumps(dict(
            model='gpt-4o-mini',
            messages=[
                dict(
                    role='user',
                    content='Hi!',
                ),
            ],
        )),
    ).data)


if __name__ == '__main__':
    _main()
