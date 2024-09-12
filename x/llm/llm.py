"""
TODO (immed):
 - -c / chat mode

PATH="/usr/local/cuda-12.2/bin:$PATH"
JIT=1
GPU=1
PYTHONPATH=tinygrad
./python
tinygrad/examples/llama.py
--model /raid/huggingface/hub/models--huggyllama--llama-7b/snapshots/8416d3fefb0cb3ff5775a7b13c1692d10ff1aa16/model.safetensors.index.json
--prompt 'hi'
"""
import abc
import argparse
import os.path
import sys
import typing as ta

import yaml

from omlish import lang
from omlish.diag import pycharm


if ta.TYPE_CHECKING:
    import llama_cpp
    import openai
    import transformers

else:
    llama_cpp = lang.proxy_import('llama_cpp')
    openai = lang.proxy_import('openai')
    transformers = lang.proxy_import('transformers')


##


class SimpleLlm(abc.ABC):
    @abc.abstractmethod
    def get_completion(self, prompt: str) -> str:
        raise NotImplementedError


class OpenaiSimpleLlm(SimpleLlm):
    model = 'gpt-3.5-turbo-instruct'

    def get_completion(self, prompt: str) -> str:
        response = openai.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )

        return response.choices[0].text


class LlamacppSimpleLlm(SimpleLlm):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def get_completion(self, prompt: str) -> str:
        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            prompt,
            max_tokens=1024,
            stop=["\n"],
        )

        return output['choices'][0]['text']


class TransformersSimpleLlm(SimpleLlm):
    model = "meta-llama/Meta-Llama-3-8B"

    def get_completion(self, prompt: str) -> str:
        pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            device='mps' if sys.platform == 'darwin' else 'cuda',
        )
        output = pipeline(prompt)
        return output


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

    llm: SimpleLlm
    # llm = OpenaiSimpleLlm()
    # llm = LlamacppSimpleLlm()
    llm = TransformersSimpleLlm()

    response = llm.get_completion(prompt)

    print(response.strip())


if __name__ == '__main__':
    _main()
