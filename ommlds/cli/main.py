"""
TODO:
 - bootstrap lol
"""
import abc
import functools
import typing as ta

import anyio

from omlish import check
from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang
from omlish.argparse import all as ap
from omlish.logs import all as logs

from .inject import bind_main
from .secrets import install_secrets
from .sessions.base import Session
from .sessions.chat.configs import ChatConfig
from .sessions.completion.configs import CompletionConfig
from .sessions.embedding.configs import EmbeddingConfig


##


MAIN_EXTRA_ARGS: ta.Sequence[ap.Arg] = [
    ap.arg('-v', '--verbose', action='store_true'),
]


def _process_main_extra_args(args: ap.Namespace) -> None:
    if args.verbose:
        logs.configure_standard_logging('DEBUG')
    else:
        logs.configure_standard_logging('INFO')
        logs.silence_noisy_loggers()


##


class Profile(lang.Abstract):
    @abc.abstractmethod
    def run(self, argv: ta.Sequence[str]) -> ta.Awaitable[None]:
        raise NotImplementedError


##


# class ChatAspect(lang.Abstract):
#     def get_parser_args(self) -> ta.Sequence[ap.Arg]: ...
#     def set_args(self, args: ap.Namespace) -> None: ...
#     def configure(self, cfg: ChatConfig) -> ChatConfig: ...


class ChatProfile(Profile):
    _args: ap.Namespace

    #

    BACKEND_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('-b', '--backend', group='backend'),
    ]

    def configure_backend(self, cfg: ChatConfig) -> ChatConfig:
        return dc.replace(
            cfg,
            backend=dc.replace(
                cfg.backend,
                backend=self._args.backend,
            ),
        )

    #

    INPUT_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('message', nargs='*', group='input'),
        ap.arg('-i', '--interactive', action='store_true', group='input'),
        ap.arg('-e', '--editor', action='store_true', group='input'),
    ]

    def configure_input(self, cfg: ChatConfig) -> ChatConfig:
        if self._args.editor:
            check.arg(not self._args.interactive)
            check.arg(not self._args.message)
            raise NotImplementedError

        elif self._args.interactive:
            check.arg(not self._args.message)
            return dc.replace(
                cfg,
                user=dc.replace(
                    cfg.user,
                    interactive=True,
                ),
            )

        elif self._args.message:
            # TODO: '-' -> stdin
            return dc.replace(
                cfg,
                user=dc.replace(
                    cfg.user,
                    initial_user_content=' '.join(self._args.message),
                ),
            )

        else:
            raise ValueError('Must specify input')

    #

    STATE_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('-n', '--new', action='store_true', group='state'),
        ap.arg('--ephemeral', action='store_true', group='state'),
    ]

    def configure_state(self, cfg: ChatConfig) -> ChatConfig:
        return dc.replace(
            cfg,
            state=dc.replace(
                cfg.state,
                state='ephemeral' if self._args.ephemeral else 'new' if self._args.new else 'continue',
            ),
        )

    #

    OUTPUT_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('-s', '--stream', action='store_true', group='output'),
        ap.arg('-M', '--markdown', action='store_true', group='output'),
    ]

    def configure_output(self, cfg: ChatConfig) -> ChatConfig:
        return dc.replace(
            cfg,
            ai=dc.replace(
                cfg.ai,
                stream=bool(self._args.stream),
            ),
            rendering=dc.replace(
                cfg.rendering,
                markdown=bool(self._args.markdown),
            ),
        )

    #

    TOOLS_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('--enable-fs-tools', action='store_true', group='tools'),
        ap.arg('--enable-todo-tools', action='store_true', group='tools'),
        # ap.arg('--enable-unsafe-tools-do-not-use-lol', action='store_true', group='tools'),
        ap.arg('--enable-test-weather-tool', action='store_true', group='tools'),
    ]

    def configure_tools(self, cfg: ChatConfig) -> ChatConfig:
        return dc.replace(
            cfg,
            ai=dc.replace(
                cfg.ai,
                enable_tools=(
                    self._args.enable_fs_tools or
                    self._args.enable_todo_tools or
                    # self._args.enable_unsafe_tools_do_not_use_lol or
                    self._args.enable_test_weather_tool or
                    self._args.code
                ),
            ),
            tools=dc.replace(
                cfg.tools,
                enabled_tools={  # noqa
                    *(cfg.tools.enabled_tools or []),
                    *(['fs'] if self._args.enable_fs_tools else []),
                    *(['todo'] if self._args.enable_todo_tools else []),
                    *(['weather'] if self._args.enable_test_weather_tool else []),
                },
            ),
        )

    #

    CODE_CONFIG: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('-c', '--code', action='store_true', group='code'),
    ]

    def configure_code(self, cfg: ChatConfig) -> ChatConfig:
        if not self._args.code:
            return cfg

        cfg = dc.replace(
            cfg,
            ai=dc.replace(
                cfg.ai,
                enable_tools=True,
            ),
        )

        if self._args.new or self._args.ephemeral:
            from ..minichain.lib.code.prompts import CODE_AGENT_SYSTEM_PROMPT
            system_content = CODE_AGENT_SYSTEM_PROMPT

            cfg = dc.replace(
                cfg,
                user=dc.replace(
                    cfg.user,
                    initial_system_content=system_content,
                ),
            )

        return cfg

    #

    async def run(self, argv: ta.Sequence[str]) -> None:
        parser = ap.ArgumentParser()

        for grp_name, grp_args in [
            ('backend', self.BACKEND_ARGS),
            ('input', self.INPUT_ARGS),
            ('state', self.STATE_ARGS),
            ('output', self.OUTPUT_ARGS),
            ('tools', self.TOOLS_ARGS),
            ('code', self.CODE_CONFIG),
        ]:
            grp = parser.add_argument_group(grp_name)
            for a in grp_args:
                grp.add_argument(*a.args, **a.kwargs)

        self._args = parser.parse_args(argv)

        cfg = ChatConfig()
        cfg = self.configure_backend(cfg)
        cfg = self.configure_input(cfg)
        cfg = self.configure_state(cfg)
        cfg = self.configure_output(cfg)
        cfg = self.configure_tools(cfg)
        cfg = self.configure_code(cfg)

        with inj.create_managed_injector(bind_main(
                session_cfg=cfg,
        )) as injector:
            await injector[Session].run()


##


class CompletionProfile(Profile):
    async def run(self, argv: ta.Sequence[str]) -> None:
        parser = ap.ArgumentParser()
        parser.add_argument('prompt', nargs='*')
        parser.add_argument('-b', '--backend', default='openai')
        args = parser.parse_args(argv)

        content = ' '.join(args.prompt)

        cfg = CompletionConfig(
            check.non_empty_str(content),
            backend=args.backend,
        )

        with inj.create_managed_injector(bind_main(
                session_cfg=cfg,
        )) as injector:
            await injector[Session].run()


##


class EmbedProfile(Profile):
    async def run(self, argv: ta.Sequence[str]) -> None:
        parser = ap.ArgumentParser()
        parser.add_argument('prompt', nargs='*')
        parser.add_argument('-b', '--backend', default='openai')
        args = parser.parse_args(argv)

        content = ' '.join(args.prompt)

        cfg = EmbeddingConfig(
            check.non_empty_str(content),
            backend=args.backend,
        )

        with inj.create_managed_injector(bind_main(
                session_cfg=cfg,
        )) as injector:
            await injector[Session].run()


##


PROFILE_TYPES: ta.Mapping[str, type[Profile]] = {
    'chat': ChatProfile,
    'complete': CompletionProfile,
    'embed': EmbedProfile,
}


##


MAIN_PROFILE_ARGS: ta.Sequence[ap.Arg] = [
    ap.arg('-p', '--profile', default='chat'),
    ap.arg('args', nargs=ap.REMAINDER),
]


async def _a_main(argv: ta.Any = None) -> None:
    parser = ap.ArgumentParser()

    for a in [*MAIN_PROFILE_ARGS, *MAIN_EXTRA_ARGS]:
        parser.add_argument(*a.args, **a.kwargs)

    args, unk_args = parser.parse_known_args(argv)

    _process_main_extra_args(args)

    install_secrets()

    profile_cls = PROFILE_TYPES[args.profile]
    profile = profile_cls()
    await profile.run([*unk_args, *args.args])


def _main(args: ta.Any = None) -> None:
    anyio.run(
        functools.partial(
            _a_main,
            args,
        ),
    )  # noqa


if __name__ == '__main__':
    _main()
