r"""
https://github.com/googleapis/python-genai/blob/f982dfbda9dc63f38996be3a4f8f90c0d7f14154/google/genai/_api_client.py#L307

https://ai.google.dev/gemini-api/docs/text-generation?lang=python#rest

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[{"text": "Write a story about a magic backpack."}]
        }]
       }' 2> /dev/null

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?alt=sse&key=${GEMINI_API_KEY}" \
        -H 'Content-Type: application/json' \
        --no-buffer \
        -d '{ "contents":[{"parts":[{"text": "Write a story about a magic backpack."}]}]}'
"""  # noqa
import json
import os.path

from omlish import marshal as msh

from ..types import GenerateContentResponse


def test_stream():
    with open(os.path.join(os.path.dirname(__file__), 'story.txt')) as f:
        src_b = f.read()

    for l in src_b.splitlines():
        if not l:
            continue
        if l.startswith('data: '):
            gcr = msh.unmarshal(json.loads(l[6:]), GenerateContentResponse)
            print(gcr)
