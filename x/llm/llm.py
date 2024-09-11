import argparse
import os.path
import sys

import openai
import yaml

from omlish.diag import pycharm


def _load_secrets():
    with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
        dct = yaml.safe_load(f)
    os.environ['OPENAI_API_KEY'] = dct['openai_api_key']
    os.environ['TAVILY_API_KEY'] = dct['tavily_api_key']


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('prompt')
    args = parser.parse_args()

    prompt = args.prompt

    if not sys.stdin.isatty() and not pycharm.is_pycharm_hosted():
        stdin_data = sys.stdin.read()

        prompt = '\n'.join([prompt, stdin_data])

    _load_secrets()

    stream = True

    response = openai.completions.create(
        model='gpt-3.5-turbo-instruct',
        prompt=prompt,
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=stream,
    )

    if stream:
        for chunk in response:
            sys.stdout.write(chunk.choices[0].text)
        print()

    else:
        response_text = response.choices[0].text.strip()
        print(response_text)


if __name__ == '__main__':
    _main()
