import abc
import argparse
import os.path
import sys

import openai
import yaml

from omlish.diag import pycharm


##


class SimpleLlm(abc.ABC):
    @abc.abstractmethod
    def get_completion(self, prompt: str) -> str:
        raise NotImplementedError


class OpenaiSimpleLlm(SimpleLlm):
    def get_completion(self, prompt: str) -> str:
        response = openai.completions.create(
            model='gpt-3.5-turbo-instruct',
            prompt=prompt,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )
        return response.choices[0].text


##


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

    llm = OpenaiSimpleLlm()

    response = llm.get_completion(prompt)

    print(response.strip())


if __name__ == '__main__':
    _main()
