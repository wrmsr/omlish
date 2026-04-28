import os.path
import sys
import typing as ta

from omdev.home.paths import get_home_paths
from omlish import check
from omlish import dataclasses as dc
from omlish.argparse import all as ap

from ... import minichain as mc
from ..profiles import AspectProfile
from ..profiles import ProfileAspect
from .configs import ChatConfig
from .interfaces.bare.configs import BareInterfaceConfig
from .interfaces.configs import InterfaceConfig
from .interfaces.textual.configs import TextualInterfaceConfig


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
            ap.arg('-x', '--autoexec', action='append'),
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
                    ),
                    interface=dc.replace(
                        check.isinstance(cfg.interface, BareInterfaceConfig),
                        interactive=ctx.args.interactive,
                        print_ai_responses=True,
                    ),
                )

            if ctx.args.autoexec:
                cfg = dc.replace(
                    cfg,
                    facade=dc.replace(
                        cfg.facade,
                        commands=dc.replace(
                            cfg.facade.commands,
                            autoexec=[*(cfg.facade.commands.autoexec or []), *ctx.args.autoexec],
                        ),
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
            ap.arg('--db'),
        ]

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if (db_file_path := ctx.args.db) is None:
                db_file_path = os.path.join(get_home_paths().state_dir, 'minichain', 'cli', 'state.db')

            return dc.replace(
                cfg,
                driver=dc.replace(
                    cfg.driver,
                    orm=dc.replace(
                        cfg.driver.orm,
                        file_path=db_file_path,
                    ),
                    state=dc.replace(
                        cfg.driver.state,
                        new=ctx.args.new,
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
                printing=dc.replace(
                    cfg.printing,
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
                modules=[
                    *(cfg.modules or []),
                    mc.modules.BashConfig(),
                    mc.modules.CodeConfig(),
                    mc.modules.FsConfig(),
                    mc.modules.TodoConfig(),
                ],
                driver=dc.replace(
                    cfg.driver,
                    ai=dc.replace(
                        cfg.driver.ai,
                        enable_tools=True,
                    ),
                ),
            )

            return cfg

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if not ctx.args.code:
                return cfg

            return self.configure_for_code(ctx, cfg)

    #

    class Skills(ProfileAspect[ChatConfig]):
        parser_args: ta.ClassVar[ta.Sequence[ap.Arg]] = [
            ap.arg('-k', '--skills', action='store_true'),
        ]

        def configure_for_skills(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            cfg = dc.replace(
                cfg,
                modules=[
                    *(cfg.modules or []),
                    mc.modules.SkillsConfig(),
                ],
            )

            return cfg

        def configure(self, ctx: ProfileAspect.ConfigureContext[ChatConfig], cfg: ChatConfig) -> ChatConfig:
            if not ctx.args.skills:
                return cfg

            return self.configure_for_skills(ctx, cfg)

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
            self.Skills(),
        ]

    def initial_config(self) -> ChatConfig:
        return ChatConfig()


##


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
