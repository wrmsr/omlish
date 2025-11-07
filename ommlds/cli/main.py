"""
See:
 - https://github.com/simonw/llm
 - https://github.com/TheR1D/shell_gpt
 - https://github.com/paul-gauthier/aider
"""
import functools
import os.path
import typing as ta

import anyio

from omdev.home.secrets import load_secrets
from omlish import check
from omlish import inject as inj
from omlish import lang
from omlish.argparse import all as ap
from omlish.logs import all as logs
from omlish.subprocesses.editor import edit_text_with_user_editor
from omlish.subprocesses.sync import subprocesses

from .. import minichain as mc
from .inject import bind_main
from .sessions.base import Session
from .sessions.chat.configs import ChatConfig
from .sessions.completion.configs import CompletionConfig
from .sessions.embedding.configs import EmbeddingConfig


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


async def _a_main(args: ta.Any = None) -> None:
    parser = ap.ArgumentParser()
    parser.add_argument('prompt', nargs='*')

    parser.add_argument('-b', '--backend', default='openai')

    parser.add_argument('-m', '--model-name')

    parser.add_argument('-C', '--completion', action='store_true')

    parser.add_argument('-n', '--new', action='store_true')
    parser.add_argument('--ephemeral', action='store_true')

    parser.add_argument('-e', '--editor', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-c', '--code', action='store_true')
    parser.add_argument('-s', '--stream', action='store_true')
    parser.add_argument('-M', '--markdown', action='store_true')

    parser.add_argument('-E', '--embed', action='store_true')
    parser.add_argument('-j', '--image', action='store_true')

    parser.add_argument('-v', '--verbose', action='store_true')

    parser.add_argument('--enable-fs-tools', action='store_true')
    parser.add_argument('--enable-todo-tools', action='store_true')
    parser.add_argument('--enable-unsafe-tools-do-not-use-lol', action='store_true')
    parser.add_argument('--enable-test-weather-tool', action='store_true')
    parser.add_argument('--dangerous-no-tool-confirmation', action='store_true')

    args = parser.parse_args(args)

    #

    if args.verbose:
        logs.configure_standard_logging('DEBUG')
    else:
        logs.configure_standard_logging('INFO')
        logs.silence_noisy_loggers()

    #

    content: mc.Content | None

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
        content = None

    elif args.code:
        if args.prompt:
            content = ' '.join(args.prompt)
        else:
            content = None

    elif not args.prompt:
        raise ValueError('Must provide prompt')

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

    session_cfg: ta.Any

    if args.embed:
        session_cfg = EmbeddingConfig(
            check.not_none(content),  # noqa
            backend=args.backend,
        )

    elif args.completion:
        session_cfg = CompletionConfig(
            check.not_none(content),  # noqa
            backend=args.backend,
        )

    else:
        system_content: mc.Content | None = None
        if (args.new or args.ephemeral) and args.code:
            from ..minichain.lib.code.prompts import CODE_AGENT_SYSTEM_PROMPT
            system_content = CODE_AGENT_SYSTEM_PROMPT

        session_cfg = ChatConfig(
            backend=args.backend,
            model_name=args.model_name,
            state='ephemeral' if args.ephemeral else 'new' if args.new else 'continue',
            initial_system_content=system_content,
            initial_user_content=content,  # noqa
            interactive=bool(args.interactive),
            markdown=bool(args.markdown),
            stream=bool(args.stream),
            enable_tools=(
                args.enable_fs_tools or
                args.enable_todo_tools or
                args.enable_unsafe_tools_do_not_use_lol or
                args.enable_test_weather_tool or
                args.code
            ),
            enabled_tools={  # noqa
                *(['fs'] if args.enable_fs_tools else []),
                *(['todo'] if args.enable_todo_tools else []),
                *(['weather'] if args.enable_test_weather_tool else []),
                # FIXME: enable_unsafe_tools_do_not_use_lol
            },
            dangerous_no_tool_confirmation=bool(args.dangerous_no_tool_confirmation),
        )

    #

    with inj.create_managed_injector(bind_main(
            session_cfg=session_cfg,
            enable_backend_strings=isinstance(session_cfg, ChatConfig),
    )) as injector:
        await injector[Session].run()


def _main(args: ta.Any = None) -> None:
    anyio.run(
        functools.partial(
            _a_main,
            args,
        ),
        # backend='trio',
    )  # noqa


if __name__ == '__main__':
    _main()
