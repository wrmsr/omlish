"""
https://ai.google.dev/gemini-api/docs/text-generation?lang=python
"""
import urllib.request

import google.generativeai as genai

from omlish.formats import json
from omdev.secrets import load_secrets


def _main():
    key = load_secrets()['gemini_api_key']

    ##

    with urllib.request.urlopen(urllib.request.Request(
            'https://generativelanguage.googleapis.com/v1beta/models/' +
            f'gemini-1.5-flash-latest:generateContent?key={key}',
            headers={
                'Content-Type': 'application/json',
            },
            data=b'{"contents":[{"parts":[{"text":"Explain how AI works"}]}]}',
            method='POST',
    )) as resp:
        buf = resp.read()

    print(json.dumps_pretty(json.loads(buf.decode('utf-8'))))

    ##

    genai.configure(api_key=key)

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Write a story about a magic backpack.")
    print(response.text)


if __name__ == '__main__':
    _main()
