"""
See:
 - https://github.com/simonw/llm
 - https://github.com/TheR1D/shell_gpt
 - https://github.com/paul-gauthier/aider
"""
import argparse
import functools
import os.path
import sys
import typing as ta

import anyio

from omdev.home.secrets import load_secrets
from omlish import check
from omlish import inject as inj
from omlish import lang
from omlish.diag import pycharm
from omlish.logs import all as logs
from omlish.subprocesses.editor import edit_text_with_user_editor
from omlish.subprocesses.sync import subprocesses

from .. import minichain as mc
from .inject import bind_main
from .sessions.base import Session
from .sessions.chat.interactive import InteractiveChatSession
from .sessions.chat.prompt import PromptChatSession
from .sessions.completion.completion import CompletionSession
from .sessions.embedding.embedding import EmbeddingSession
from .tools.config import ToolsConfig


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


async def _a_main(args: ta.Any = None) -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt', nargs='*')

    parser.add_argument('-b', '--backend', default='openai')

    parser.add_argument('-m', '--model-name')

    parser.add_argument('-C', '--completion', action='store_true')

    parser.add_argument('-n', '--new', action='store_true')

    parser.add_argument('-e', '--editor', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-s', '--stream', action='store_true')
    parser.add_argument('-M', '--markdown', action='store_true')

    parser.add_argument('-E', '--embed', action='store_true')
    parser.add_argument('-j', '--image', action='store_true')

    parser.add_argument('--enable-fs-tools', action='store_true')
    parser.add_argument('--enable-unsafe-bash-tool', action='store_true')
    parser.add_argument('--enable-test-weather-tool', action='store_true')
    parser.add_argument('--dangerous-no-tool-confirmation', action='store_true')

    args = parser.parse_args(args)

    #

    content: mc.Content

    if args.image:
        content = mc.ImageContent(pimg.open(check.non_empty_str(check.single(args.prompt))))

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

    session_cfg: Session.Config

    if args.interactive:
        session_cfg = InteractiveChatSession.Config(
            backend=args.backend,
            model_name=args.model_name,
            new=bool(args.new),
            dangerous_no_tool_confirmation=bool(args.dangerous_no_tool_confirmation),
        )

    elif args.embed:
        session_cfg = EmbeddingSession.Config(
            content,  # noqa
            backend=args.backend,
        )

    elif args.completion:
        session_cfg = CompletionSession.Config(
            content,  # noqa
            backend=args.backend,
        )

    else:
        session_cfg = PromptChatSession.Config(
            content,  # noqa
            backend=args.backend,
            model_name=args.model_name,
            new=bool(args.new),
            stream=bool(args.stream),
            markdown=bool(args.markdown),
            dangerous_no_tool_confirmation=bool(args.dangerous_no_tool_confirmation),
        )

    #

    tools_config = ToolsConfig(
        enable_fs_tools=args.enable_fs_tools,
        enable_unsafe_bash_tool=args.enable_unsafe_bash_tool,
        enable_test_weather_tool=args.enable_test_weather_tool,
    )

    #

    with inj.create_managed_injector(bind_main(
            session_cfg=session_cfg,
            tools_config=tools_config,
            enable_backend_strings=isinstance(session_cfg, PromptChatSession.Config),
    )) as injector:
        await injector[Session].run()


def _main(args: ta.Any = None) -> None:
    anyio.run(
        functools.partial(
            _a_main,
            args,
        ),
        backend='asyncio',
    )  # noqa


if __name__ == '__main__':
    _main()
