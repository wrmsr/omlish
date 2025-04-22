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

from omdev.home.paths import get_home_paths
from omdev.home.secrets import load_secrets
from omlish import check
from omlish import lang
from omlish.diag import pycharm
from omlish.formats import json
from omlish.logs import all as logs
from omlish.subprocesses.editor import edit_text_with_user_editor
from omlish.subprocesses.sync import subprocesses

from .. import minichain as mc
from ..minichain.backends.anthropic.chat import AnthropicChatService
from ..minichain.backends.google.chat import GoogleChatService
from ..minichain.backends.llamacpp.chat import LlamacppChatService
from ..minichain.backends.llamacpp.completion import LlamacppCompletionService
from ..minichain.backends.mistral import MistralChatService
from ..minichain.backends.openai.chat import OpenaiChatService
from ..minichain.backends.openai.completion import OpenaiCompletionService
from ..minichain.backends.openai.embedding import OpenaiEmbeddingService
from ..minichain.backends.sentencetransformers import SentencetransformersEmbeddingService
from ..minichain.backends.transformers import TransformersCompletionService
from .state import load_state
from .state import save_state


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa

    from omdev import ptk

else:
    pimg = lang.proxy_import('PIL.Image')

    ptk = lang.proxy_import('omdev.ptk')


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()


CHAT_MODEL_BACKENDS: ta.Mapping[str, type[mc.ChatService]] = {
    'anthropic': AnthropicChatService,
    'google': GoogleChatService,
    'mistral': MistralChatService,
    'openai': OpenaiChatService,
    'llamacpp': LlamacppChatService,
}


def _run_chat(
        content: mc.Content,
        *,
        new: bool = False,
        backend: str | None = None,
        stream: bool = False,
) -> None:
    prompt = check.isinstance(content, str)

    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
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

    if stream:
        st_mdl = mc.backend_of[mc.ChatStreamService].new('openai')
        with st_mdl.invoke(mc.ChatStreamRequest(state.chat)) as st_resp:
            resp_s = ''
            for o in st_resp:
                o_s = check.isinstance(o[0].m.s, str)
                print(o_s, end='', flush=True)
                resp_s += o_s
            print()
        resp_m = mc.AiMessage(resp_s)

    else:
        mdl = CHAT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
        response = mdl.invoke(mc.ChatRequest.new(state.chat))
        resp_m = response.choices[0].m
        print(check.isinstance(resp_m.s, str).strip())

    state = dc.replace(
        state,
        chat=[
            *state.chat,
            resp_m,
        ],
        updated_at=lang.utcnow(),
    )

    save_state(chat_file, state, ChatState)


##


def _run_interactive(
        *,
        new: bool = False,
        backend: str | None = None,
) -> None:
    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
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

    while True:
        prompt = ptk.prompt('> ')

        state = dc.replace(
            state,
            chat=[
                *state.chat,
                mc.UserMessage(prompt),
            ],
        )

        mdl = CHAT_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
        response = mdl.invoke(mc.ChatRequest.new(state.chat))
        print(check.isinstance(response.choices[0].m.s, str).strip())

        state = dc.replace(
            state,
            chat=[
                *state.chat,
                response.choices[0].m,
            ],
            updated_at=lang.utcnow(),
        )

        save_state(chat_file, state, ChatState)


##


COMPLETION_MODEL_BACKENDS: ta.Mapping[str, type[mc.CompletionService]] = {
    'llamacpp': LlamacppCompletionService,
    'openai': OpenaiCompletionService,
    'transformers': TransformersCompletionService,
}


def _run_completion(
        content: mc.Content,
        *,
        backend: str | None = None,
) -> None:
    prompt = check.isinstance(content, str)
    mdl = COMPLETION_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(mc.CompletionRequest.new(prompt))
    print(response.text.strip())


##


EMBEDDING_MODEL_BACKENDS: ta.Mapping[str, type[mc.EmbeddingService]] = {
    'openai': OpenaiEmbeddingService,
    'sentencetransformers': SentencetransformersEmbeddingService,
}


def _run_embed(
        content: mc.Content,
        *,
        backend: str | None = None,
) -> None:
    mdl = EMBEDDING_MODEL_BACKENDS[backend or DEFAULT_BACKEND]()
    response = mdl.invoke(mc.EmbeddingRequest.new(content))
    print(json.dumps_compact(response.vector))


##

def _main() -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt', nargs='*')

    parser.add_argument('-b', '--backend', default='openai')

    parser.add_argument('-C', '--completion', action='store_true')

    parser.add_argument('-n', '--new', action='store_true')

    parser.add_argument('-e', '--editor', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-s', '--stream', action='store_true')

    parser.add_argument('-E', '--embed', action='store_true')
    parser.add_argument('-j', '--image', action='store_true')

    args = parser.parse_args()

    #

    content: mc.Content

    if args.image:
        content = mc.Image(pimg.open(check.non_empty_str(check.single(args.prompt))))

    elif args.editor:
        check.arg(not args.prompt)
        if (ec := edit_text_with_user_editor('', subprocesses)) is None:
            return
        content = ec

    elif args.interactive:
        if args.prompt:
            raise ValueError('Must not provide prompt')

    elif not args.prompt:
        raise ValueError('Must provide prompt')

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

    if args.interactive:
        _run_interactive(
            backend=args.backend,
            new=bool(args.new),
        )

    elif args.embed:
        _run_embed(
            content,
            backend=args.backend,
        )

    elif args.completion:
        _run_completion(
            content,
            backend=args.backend,
        )

    else:
        _run_chat(
            content,
            backend=args.backend,
            new=bool(args.new),
            stream=bool(args.stream),
        )


if __name__ == '__main__':
    _main()
