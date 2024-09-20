import argparse
import dataclasses as dc
import datetime
import os.path
import sys
import typing as ta

from omlish import lang
from omlish import logs
from omlish.diag import pycharm
from omlish.formats import json

from ..backends.llamacpp import LlamacppPromptModel
from ..backends.openai import OpenaiChatModel
from ..backends.openai import OpenaiEmbeddingModel
from ..backends.openai import OpenaiPromptModel
from ..backends.sentencetransformers import SentencetransformersEmbeddingModel
from ..backends.transformers import TransformersPromptModel
from ..chat import Chat
from ..chat import ChatModel
from ..chat import ChatRequest
from ..chat import UserMessage
from ..content import Text
from ..embeddings import EmbeddingModel
from ..models import Request
from ..prompts import Prompt
from ..prompts import PromptModel
from .state import load_state
from .state import save_state


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: Chat = ()


CHAT_MODEL_BACKENDS: ta.Mapping[str, type[ChatModel]] = {
    'openai': OpenaiChatModel,
}


def _run_chat(
        prompt: str,
        *,
        new: bool = False,
        backend: str | None = None,
) -> None:
    state_dir = os.path.expanduser('~/.omlish-llm')
    if not os.path.exists(state_dir):
        os.mkdir(state_dir)
        os.chmod(state_dir, 0o770)  # noqa

    chat_file = os.path.join(state_dir, 'chat.json')
    if new:
        state = ChatState()
    else:
        state = load_state(chat_file, ChatState)  # type: ignore
        if state is None:
            state = ChatState()  # type: ignore

    #

    state = dc.replace(
        state,
        chat=[
            *state.chat,
            UserMessage([Text(prompt)])],
    )

    #

    mdl = CHAT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()

    #

    response = mdl.generate(Request(ChatRequest(state.chat)))

    #

    print(response.v.s.strip())

    #

    chat = dc.replace(
        state,
        chat=[
            *state.chat,
            response.v,
        ],
    )

    #

    chat = dc.replace(
        chat,
        updated_at=lang.utcnow(),
    )

    save_state(chat_file, chat, ChatState)


##


PROMPT_MODEL_BACKENDS: ta.Mapping[str, type[PromptModel]] = {
    'llamacpp': LlamacppPromptModel,
    'openai': OpenaiPromptModel,
    'transformers': TransformersPromptModel,
}


def _run_prompt(
        prompt: str,
        *,
        backend: str | None = None,
) -> None:
    mdl = PROMPT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()

    response = mdl.generate(Request(Prompt(prompt)))

    print(response.v.strip())


##


EMBEDDING_MODEL_BACKENDS: ta.Mapping[str, type[EmbeddingModel]] = {
    'openai': OpenaiEmbeddingModel,
    'sentencetransformers': SentencetransformersEmbeddingModel,
}


def _run_embed(
        prompt: str,
        *,
        backend: str | None = None,
) -> None:
    mdl = EMBEDDING_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()

    response = mdl.generate(Request(Text(prompt)))

    print(json.dumps_compact(response.v.v))


##

def _main() -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt')
    parser.add_argument('-c', '--chat', action='store_true')
    parser.add_argument('-e', '--embed', action='store_true')
    parser.add_argument('-n', '--new', action='store_true')
    parser.add_argument('-b', '--backend', default='openai')
    args = parser.parse_args()

    #

    prompt = args.prompt

    if not sys.stdin.isatty() and not pycharm.is_pycharm_hosted():
        stdin_data = sys.stdin.read()
        prompt = '\n'.join([prompt, stdin_data])

    #

    with open(os.path.join(os.path.expanduser('~/.omlish-llm/.env'))) as f:
        for l in f:
            if l := l.strip():
                k, _, v = l.partition('=')
                os.environ[k] = v

    #

    if args.chat:
        _run_chat(
            prompt,
            backend=args.backend,
            new=bool(args.new),
        )

    elif args.embed:
        _run_embed(
            prompt,
            backend=args.backend,
        )

    else:
        _run_prompt(
            prompt,
            backend=args.backend,
        )


if __name__ == '__main__':
    _main()
