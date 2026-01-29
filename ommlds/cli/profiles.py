import abc
import sys
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.argparse import all as ap

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


class Profile(lang.Abstract, ta.Generic[SessionConfigT]):
    @abc.abstractmethod
    def configure(self, argv: ta.Sequence[str]) -> SessionConfigT:
        raise NotImplementedError


##


class ProfileAspect(lang.Abstract, ta.Generic[SessionConfigT]):
    @property
    def name(self) -> str:
        return lang.camel_to_snake(type(self).__name__).lower()

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

        def configure_with_tools(
                self,
                ctx: ProfileAspect.ConfigureContext[ChatConfig],
                cfg: ChatConfig,
                enabled_tools: ta.Iterable[str],
        ) -> ChatConfig:
            check.not_isinstance(enabled_tools, str)

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
                            *enabled_tools,
                        },
                    ),
                ),
                interface=dc.replace(
                    cfg.interface,
                    enable_tools=True,
                ),
            )

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if not (
                    ctx.args.enable_fs_tools or
                    ctx.args.enable_todo_tools or
                    # ctx.args.enable_unsafe_tools_do_not_use_lol or
                    ctx.args.enable_test_weather_tool
            ):
                return cfg

            return self.configure_with_tools(ctx, cfg, {
                *(['fs'] if ctx.args.enable_fs_tools else []),
                *(['todo'] if ctx.args.enable_todo_tools else []),
                *(['weather'] if ctx.args.enable_test_weather_tool else []),
            })

    #

    class Code(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('-c', '--code', action='store_true'),
        ]

        def configure_for_code(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
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

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if not ctx.args.code:
                return cfg

            return self.configure_for_code(ctx, cfg)

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
    class Tools(ChatProfile.Tools):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = []

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            return self.configure_with_tools(ctx, cfg, {
                'fs',
                'todo',
            })

    class Code(ChatProfile.Code):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = []

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            return self.configure_for_code(ctx, cfg)


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
