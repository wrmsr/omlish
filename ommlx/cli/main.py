"""
See:
 - https://github.com/simonw/llm
 - https://github.com/TheR1D/shell_gpt
 - https://github.com/paul-gauthier/aider
"""
import argparse
import dataclasses as dc
import datetime
import os.path
import sys
import typing as ta

from omdev.home.paths import get_state_dir
from omdev.home.secrets import load_secrets
from omlish import check
from omlish import lang
from omlish.diag import pycharm
from omlish.formats import json
from omlish.logs import all as logs

from .. import minichain as mc
from ..minichain.backends.anthropic import AnthropicChatModel
from ..minichain.backends.google import GoogleChatModel
from ..minichain.backends.llamacpp import LlamacppChatModel
from ..minichain.backends.llamacpp import LlamacppPromptModel
from ..minichain.backends.mistral import MistralChatModel
from ..minichain.backends.openai import OpenaiChatModel
from ..minichain.backends.openai import OpenaiEmbeddingModel
from ..minichain.backends.openai import OpenaiPromptModel
from ..minichain.backends.sentencetransformers import SentencetransformersEmbeddingModel
from ..minichain.backends.transformers import TransformersPromptModel
from .state import load_state
from .state import save_state


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()


CHAT_MODEL_BACKENDS: ta.Mapping[str, type[mc.ChatModel]] = {
    'anthropic': AnthropicChatModel,
    'google': GoogleChatModel,
    'mistral': MistralChatModel,
    'openai': OpenaiChatModel,
    'llamacpp': LlamacppChatModel,
}


def _run_chat(
        content: mc.Content,
        *,
        new: bool = False,
        backend: str | None = None,
) -> None:
    prompt = check.isinstance(content, str)

    state_dir = os.path.join(get_state_dir(), 'minichain', 'cli')
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
        os.chmod(state_dir, 0o770)  # noqa

    chat_file = os.path.join(state_dir, 'chat.json')
    if new:
        state = ChatState()
    else:
        state = load_state(chat_file, ChatState)  # type: ignore
        if state is None:
            state = ChatState()  # type: ignore

    state = dc.replace(
        state,
        chat=[
            *state.chat,
            mc.UserMessage(prompt),
        ],
    )

    mdl = CHAT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(mc.ChatRequest.new(state.chat))
    print(check.isinstance(response.v[0].m.s, str).strip())

    chat = dc.replace(
        state,
        chat=[
            *state.chat,
            response.v[0].m,
        ],
    )

    chat = dc.replace(
        chat,
        updated_at=lang.utcnow(),
    )

    save_state(chat_file, chat, ChatState)


##


PROMPT_MODEL_BACKENDS: ta.Mapping[str, type[mc.PromptModel]] = {
    'llamacpp': LlamacppPromptModel,
    'openai': OpenaiPromptModel,
    'transformers': TransformersPromptModel,
}


def _run_prompt(
        content: mc.Content,
        *,
        backend: str | None = None,
) -> None:
    prompt = check.isinstance(content, str)
    mdl = PROMPT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(mc.PromptRequest.new(prompt))
    print(response.v.strip())


##


EMBEDDING_MODEL_BACKENDS: ta.Mapping[str, type[mc.EmbeddingModel]] = {
    'openai': OpenaiEmbeddingModel,
    'sentencetransformers': SentencetransformersEmbeddingModel,
}


def _run_embed(
        content: mc.Content,
        *,
        backend: str | None = None,
) -> None:
    mdl = EMBEDDING_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(mc.EmbeddingRequest.new(content))
    print(json.dumps_compact(response.v))


##

def _main() -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt', nargs='+')

    parser.add_argument('-b', '--backend', default='openai')

    parser.add_argument('-c', '--chat', action='store_true')
    parser.add_argument('-n', '--new', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')

    parser.add_argument('-e', '--embed', action='store_true')
    parser.add_argument('-j', '--image', action='store_true')

    args = parser.parse_args()

    #

    content: mc.Content

    if args.image:
        content = mc.Image(pimg.open(check.non_empty_str(check.single(args.prompt))))

    else:
        prompt = ' '.join(args.prompt)

        if not sys.stdin.isatty() and not pycharm.is_pycharm_hosted():
            stdin_data = sys.stdin.read()
            prompt = '\n'.join([prompt, stdin_data])

        content = prompt

    #

    # FIXME: lol garbage
    for key in [
        'OPENAI_API_KEY',
        'HUGGINGFACE_TOKEN',
        'TAVILY_API_KEY',
        'ANTHROPIC_API_KEY',
        'MISTRAL_API_KEY',
        'GEMINI_API_KEY',
    ]:
        if (sec := load_secrets().try_get(key.lower())) is not None:
            os.environ[key] = sec.reveal()

    #

    if args.chat:
        _run_chat(
            content,
            backend=args.backend,
            new=bool(args.new),
        )

    elif args.embed:
        _run_embed(
            content,
            backend=args.backend,
        )

    else:
        _run_prompt(
            content,
            backend=args.backend,
        )


if __name__ == '__main__':
    _main()
