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
import dataclasses as dc
import datetime
import enum
import os.path
import sys
import typing as ta

import yaml

from omlish import lang
from omlish import logs
from omlish import marshal as msh
from omlish.diag import pycharm
from omlish.formats import json


if ta.TYPE_CHECKING:
    import llama_cpp
    import openai
    import transformers

else:
    llama_cpp = lang.proxy_import('llama_cpp')
    openai = lang.proxy_import('openai')
    transformers = lang.proxy_import('transformers')


T = ta.TypeVar('T')


##


class ChatRole(enum.Enum):
    SYSTEM = enum.auto()
    USER = enum.auto()
    ASSISTANT = enum.auto()


@dc.dataclass(frozen=True)
class ChatMessage:
    role: ChatRole
    text: str

    created_at: datetime.datetime = dc.field(default_factory=datetime.datetime.now)


@dc.dataclass(frozen=True)
class Chat:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = dc.field(default_factory=datetime.datetime.now)

    messages: ta.Sequence[ChatMessage] = ()


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
            token=os.environ.get('HUGGINGFACE_HUB_TOKEN'),
        )
        output = pipeline(prompt)
        return output


##


STATE_VERSION = 0


@dc.dataclass(frozen=True)
class MarshaledState:
    version: int
    payload: ta.Any


#


def marshal_state(obj: ta.Any, ty: type | None = None, *, version: int = STATE_VERSION) -> ta.Any:
    ms = MarshaledState(
        version=version,
        payload=msh.marshal(obj, ty)
    )
    return msh.marshal(ms)


def save_state(file: str, obj: ta.Any, ty: type[T] | None, *, version: int = STATE_VERSION) -> bool:
    dct = marshal_state(obj, ty, version=version)
    data = json.dumps(dct)
    with open(file, 'w') as f:
        f.write(data)
    return True


#


def unmarshal_state(obj: ta.Any, ty: type[T] | None = None, *, version: int = STATE_VERSION) -> T | None:
    ms = msh.unmarshal(obj, MarshaledState)
    if ms.version < version:
        return None
    return msh.unmarshal(ms.payload, ty)


def load_state(file: str, ty: type[T] | None, *, version: int = STATE_VERSION) -> T | None:
    if not os.path.isfile(file):
        return None
    with open(file) as f:
        data = f.read()
    dct = json.loads(data)
    return unmarshal_state(dct, ty, version=version)


##


def _load_secrets():
    with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
        dct = yaml.safe_load(f)
    os.environ['OPENAI_API_KEY'] = dct['openai_api_key']
    os.environ['TAVILY_API_KEY'] = dct['tavily_api_key']
    os.environ['HUGGINGFACE_HUB_TOKEN'] = dct['huggingface_token']


def _main() -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt')
    parser.add_argument('-c', '--chat', action='store_true')
    parser.add_argument('-n', '--new', action='store_true')
    args = parser.parse_args()

    #

    prompt = args.prompt

    if not sys.stdin.isatty() and not pycharm.is_pycharm_hosted():
        stdin_data = sys.stdin.read()
        prompt = '\n'.join([prompt, stdin_data])

    #

    state_dir = os.path.expanduser('~/.omlish-llm')
    if not os.path.exists(state_dir):
        os.mkdir(state_dir)
        os.chmod(state_dir, 0o770)

    chat_file = os.path.join(state_dir, 'chat.json')
    if args.new:
        chat = Chat()
    else:
        chat = load_state(chat_file, Chat)
        if chat is None:
            chat = Chat()

    #

    _load_secrets()

    llm: SimpleLlm
    # llm = OpenaiSimpleLlm()
    # llm = LlamacppSimpleLlm()
    llm = TransformersSimpleLlm()

    DELIM = '\n\n====\n\n'

    full_prompt = DELIM.join([
        *[m.text for m in chat.messages],
        prompt,
    ])

    sys.stdout.write(full_prompt)
    sys.stdout.write(DELIM)

    response = llm.get_completion(full_prompt).strip()

    print(response)

    #

    chat = dc.replace(
        chat,
        messages=[
            *chat.messages,
            ChatMessage(ChatRole.USER, prompt),
            ChatMessage(ChatRole.ASSISTANT, response),
        ],
        updated_at=datetime.datetime.now(),
    )

    save_state(chat_file, chat, Chat)


if __name__ == '__main__':
    _main()
