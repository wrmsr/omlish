"""
TODO:
 - bootstrap lol
"""
import abc
import functools
import sys
import typing as ta

import anyio

from omlish import check
from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang
from omlish.argparse import all as ap
from omlish.logs import all as logs

from .inject import bind_main
from .secrets import install_env_secrets
from .sessions.base import Session
from .sessions.chat.configs import ChatConfig
from .sessions.chat.interfaces.bare.configs import BareInterfaceConfig
from .sessions.chat.interfaces.configs import InterfaceConfig
from .sessions.chat.interfaces.textual.configs import TextualInterfaceConfig
from .sessions.completion.configs import CompletionConfig
from .sessions.configs import SessionConfig
from .sessions.embedding.configs import EmbeddingConfig


SessionConfigT = ta.TypeVar('SessionConfigT', bound=SessionConfig)
SessionConfigU = ta.TypeVar('SessionConfigU', bound=SessionConfig)


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


class Profile(lang.Abstract, ta.Generic[SessionConfigT]):
    @abc.abstractmethod
    def configure(self, argv: ta.Sequence[str]) -> SessionConfigT:
        raise NotImplementedError


##


class ProfileAspect(lang.Abstract, ta.Generic[SessionConfigT]):
    @property
    def name(self) -> str:
        return lang.low_camel_case(type(self).__name__)

    @property
    def default_parser_arg_group(self) -> str | None:
        return self.name

    @property
    def parser_args(self) -> ta.Sequence[ap.Arg]:
        return []

    @ta.final
    @dc.dataclass(frozen=True)
    class ConfigureContext(ta.Generic[SessionConfigU]):
        profile: 'Profile[SessionConfigU]'
        args: ap.Namespace

    @abc.abstractmethod
    def configure(self, ctx: ConfigureContext[SessionConfigT], cfg: SessionConfigT) -> SessionConfigT:
        raise NotImplementedError


class AspectProfile(Profile[SessionConfigT], lang.Abstract):
    @abc.abstractmethod
    def _build_aspects(self) -> ta.Sequence[ProfileAspect[SessionConfigT]]:
        return []

    __aspects: ta.Sequence[ProfileAspect[SessionConfigT]]

    @ta.final
    @property
    def aspects(self) -> ta.Sequence[ProfileAspect[SessionConfigT]]:
        try:
            return self.__aspects
        except AttributeError:
            pass
        self.__aspects = aspects = tuple(self._build_aspects())
        return aspects

    #

    @abc.abstractmethod
    def initial_config(self) -> SessionConfigT:
        raise NotImplementedError

    #

    def configure(self, argv: ta.Sequence[str]) -> SessionConfigT:
        parser = ap.ArgumentParser()

        pa_grps: dict[str, ta.Any] = {}
        for a in self.aspects:
            for pa in a.parser_args:
                if (pa_gn := lang.opt_coalesce(pa.group, a.default_parser_arg_group)) is not None:
                    check.non_empty_str(pa_gn)
                    try:
                        pa_grp = pa_grps[pa_gn]
                    except KeyError:
                        pa_grps[pa_gn] = pa_grp = parser.add_argument_group(pa_gn)
                    pa_grp.add_argument(*pa.args, **pa.kwargs)
                else:
                    parser.add_argument(*pa.args, **pa.kwargs)

        args = parser.parse_args(argv)

        cfg_ctx = ProfileAspect.ConfigureContext(
            self,
            args,
        )
        cfg = self.initial_config()
        for a in self.aspects:
            cfg = a.configure(cfg_ctx, cfg)

        return cfg


##


class ChatProfile(AspectProfile[ChatConfig]):
    class Backend(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('-b', '--backend'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            return dc.replace(
                cfg,
                driver=dc.replace(
                    cfg.driver,
                    backend=dc.replace(
                        cfg.driver.backend,
                        backend=ctx.args.backend,
                    ),
                ),
            )

    #

    class Interface(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('-i', '--interactive', action='store_true'),
            ap.arg('-T', '--textual', action='store_true'),
            ap.arg('-e', '--editor', action='store_true'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if ctx.args.editor:
                check.arg(not ctx.args.interactive)
                check.arg(not ctx.args.message)
                raise NotImplementedError

            if ctx.args.textual:
                check.isinstance(cfg.interface, BareInterfaceConfig)
                cfg = dc.replace(
                    cfg,
                    interface=TextualInterfaceConfig(**{
                        f.name: getattr(cfg.interface, f.name)
                        for f in dc.fields(InterfaceConfig)
                    }),
                )

            else:
                cfg = dc.replace(
                    cfg,
                    driver=dc.replace(
                        cfg.driver,
                        ai=dc.replace(
                            cfg.driver.ai,
                            verbose=True,
                        ),
                    ),
                    interface=dc.replace(
                        check.isinstance(cfg.interface, BareInterfaceConfig),
                        interactive=ctx.args.interactive,
                    ),
                )

            return cfg

    #

    class Input(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('message', nargs='*'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if ctx.args.interactive or ctx.args.textual:
                check.arg(not ctx.args.message)

            elif ctx.args.message:
                ps: list[str] = []

                for a in ctx.args.message:
                    if a == '-':
                        ps.append(sys.stdin.read())

                    elif a.startswith('@'):
                        with open(a[1:]) as f:
                            ps.append(f.read())

                    else:
                        ps.append(a)

                c = ' '.join(ps)

                cfg = dc.replace(
                    cfg,
                    driver=dc.replace(
                        cfg.driver,
                        user=dc.replace(
                            cfg.driver.user,
                            initial_user_content=c,
                        ),
                    ),
                )

            else:
                raise ValueError('Must specify input')

            return cfg

    #

    class State(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('-n', '--new', action='store_true'),
            ap.arg('--ephemeral', action='store_true'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            return dc.replace(
                cfg,
                driver=dc.replace(
                    cfg.driver,
                    state=dc.replace(
                        cfg.driver.state,
                        state='ephemeral' if ctx.args.ephemeral else 'new' if ctx.args.new else 'continue',
                    ),
                ),
            )

    #

    class Output(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('-s', '--stream', action='store_true'),
            ap.arg('-M', '--markdown', action='store_true'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            return dc.replace(
                cfg,
                driver=dc.replace(
                    cfg.driver,
                    ai=dc.replace(
                        cfg.driver.ai,
                        stream=bool(ctx.args.stream),
                    ),
                ),
                rendering=dc.replace(
                    cfg.rendering,
                    markdown=bool(ctx.args.markdown),
                ),
            )

    #

    class Tools(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('--enable-fs-tools', action='store_true'),
            ap.arg('--enable-todo-tools', action='store_true'),
            # ap.arg('--enable-unsafe-tools-do-not-use-lol', action='store_true'),
            ap.arg('--enable-test-weather-tool', action='store_true'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if not (
                    ctx.args.enable_fs_tools or
                    ctx.args.enable_todo_tools or
                    # ctx.args.enable_unsafe_tools_do_not_use_lol or
                    ctx.args.enable_test_weather_tool or
                    ctx.args.code
            ):
                return cfg

            return dc.replace(
                cfg,
                driver=dc.replace(
                    cfg.driver,
                    ai=dc.replace(
                        cfg.driver.ai,
                        enable_tools=True,
                    ),
                    tools=dc.replace(
                        cfg.driver.tools,
                        enabled_tools={  # noqa
                            *(cfg.driver.tools.enabled_tools or []),
                            *(['fs'] if ctx.args.enable_fs_tools else []),
                            *(['todo'] if ctx.args.enable_todo_tools else []),
                            *(['weather'] if ctx.args.enable_test_weather_tool else []),
                        },
                    ),
                ),
                interface=dc.replace(
                    cfg.interface,
                    enable_tools=True,
                ),
            )

    #

    class Code(ProfileAspect[ChatConfig]):
        parser_config: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('-c', '--code', action='store_true'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if not ctx.args.code:
                return cfg

            cfg = dc.replace(
                cfg,
                driver=dc.replace(
                    cfg.driver,
                    ai=dc.replace(
                        cfg.driver.ai,
                        enable_tools=True,
                    ),
                ),
            )

            if ctx.args.new or ctx.args.ephemeral:
                from ..minichain.lib.code.prompts import CODE_AGENT_SYSTEM_PROMPT
                system_content = CODE_AGENT_SYSTEM_PROMPT

                cfg = dc.replace(
                    cfg,
                    driver=dc.replace(
                        cfg.driver,
                        user=dc.replace(
                            cfg.driver.user,
                            initial_system_content=system_content,
                        ),
                    ),
                )

            return cfg

    #

    def _build_aspects(self) -> ta.Sequence[ProfileAspect[ChatConfig]]:
        return [
            *super()._build_aspects(),
            self.Backend(),
            self.Interface(),
            self.Input(),
            self.State(),
            self.Output(),
            self.Tools(),
            self.Code(),
        ]

    def initial_config(self) -> ChatConfig:
        return ChatConfig()


#


class CodeProfile(ChatProfile):
    pass


##


class CompletionProfile(Profile):
    def configure(self, argv: ta.Sequence[str]) -> SessionConfig:
        parser = ap.ArgumentParser()
        parser.add_argument('prompt', nargs='*')
        parser.add_argument('-b', '--backend', default='openai')
        args = parser.parse_args(argv)

        content = ' '.join(args.prompt)

        cfg = CompletionConfig(
            content=check.non_empty_str(content),
            backend=args.backend,
        )

        return cfg


##


class EmbedProfile(Profile):
    def configure(self, argv: ta.Sequence[str]) -> SessionConfig:
        parser = ap.ArgumentParser()
        parser.add_argument('prompt', nargs='*')
        parser.add_argument('-b', '--backend', default='openai')
        args = parser.parse_args(argv)

        content = ' '.join(args.prompt)

        cfg = EmbeddingConfig(
            content=check.non_empty_str(content),
            backend=args.backend,
        )

        return cfg


##


PROFILE_TYPES: ta.Mapping[str, type[Profile]] = {
    'chat': ChatProfile,
    'code': CodeProfile,

    'complete': CompletionProfile,

    'embed': EmbedProfile,
}


##


async def _run_session_cfg(session_cfg: SessionConfig) -> None:
    async with inj.create_async_managed_injector(bind_main(
            session_cfg=session_cfg,
    )) as injector:
        await (await injector[Session]).run()


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

    install_env_secrets()

    profile_cls = PROFILE_TYPES[args.profile]
    profile = profile_cls()

    session_cfg = profile.configure([*unk_args, *args.args])

    await _run_session_cfg(session_cfg)


def _main(args: ta.Any = None) -> None:
    anyio.run(
        functools.partial(
            _a_main,
            args,
        ),
    )  # noqa


if __name__ == '__main__':
    _main()
