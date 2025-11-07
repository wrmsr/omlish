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
from omlish import lang
from omlish.argparse import all as ap
from omlish.logs import all as logs

from .sessions.chat.configs import ChatConfig


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


# class ProfileAspect(lang.Abstract):
#     def get_parser_args(self) -> ta.Sequence[ap.Arg]: ...
#     def set_args(self, args: ap.Namespace) -> None: ...
#     def configure(self, cfg: ChatConfig) -> ChatConfig: ...
#     def bind(self) -> inj.Elements: ...


class Profile(lang.Abstract):
    @abc.abstractmethod
    def run(self, argv: ta.Sequence[str]) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class ChatProfile(Profile):
    _args: ap.Namespace

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
            raise NotImplementedError

        elif self._args.message:
            # TODO: '-' -> stdin
            raise NotImplementedError

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
            state='ephemeral' if self._args.ephemeral else 'new' if self._args.new else 'continue',
        )

    #

    OUTPUT_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('-s', '--stream', action='store_true', group='output'),
        ap.arg('-M', '--markdown', action='store_true', group='output'),
    ]

    def configure_output(self, cfg: ChatConfig) -> ChatConfig:
        return dc.replace(
            cfg,
            stream=bool(self._args.stream),
            markdown=bool(self._args.markdown),
        )

    #

    async def run(self, argv: ta.Sequence[str]) -> None:
        parser = ap.ArgumentParser()

        for grp_name, grp_args in [
            ('input', self.INPUT_ARGS),
            ('state', self.STATE_ARGS),
            ('output', self.OUTPUT_ARGS),
        ]:
            grp = parser.add_argument_group(grp_name)
            for a in grp_args:
                grp.add_argument(*a.args, **a.kwargs)

        self._args = parser.parse_args(argv)

        cfg = ChatConfig()
        cfg = self.configure_input(cfg)
        cfg = self.configure_state(cfg)
        cfg = self.configure_output(cfg)

        print(cfg)


##


PROFILE_TYPES: ta.Mapping[str, type[Profile]] = {
    'chat': ChatProfile,
}


##


MAIN_PROFILE_ARGS: ta.Sequence[ap.Arg] = [
    ap.arg('profile', nargs='?', default='chat'),
    ap.arg('args', nargs=ap.REMAINDER),
]


async def _a_main(argv: ta.Any = None) -> None:
    parser = ap.ArgumentParser()

    for a in [*MAIN_EXTRA_ARGS, *MAIN_PROFILE_ARGS]:
        parser.add_argument(*a.args, **a.kwargs)

    args, unk_args = parser.parse_known_args(argv)

    _process_main_extra_args(args)

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
