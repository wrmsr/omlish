"""
https://github.com/HenryHengLUO/Retrieval-Augmented-Generation-Intro-Project lol
"""
import os.path
import typing as ta

import openai
import yaml


def _main():
    with open('secrets.yml', 'r') as f:
        openai_api_key = yaml.safe_load(f)['openai_api_key']

    oai = openai.OpenAI(api_key=openai_api_key)
    del openai_api_key

    docs: dict[str, str] = {}
    for fn in os.listdir(bd := os.path.join(os.path.dirname(__file__), 'docs')):
        with open(os.path.join(bd, fn)) as f:
            txt = f.read()
        docs[fn] = txt

    emb_eng = 'text-embedding-ada-002'
    res = oai.embeddings.create(
        input=list(docs.values()),
        model=emb_eng,
    )
    print(res)


if __name__ == '__main__':
    _main()
