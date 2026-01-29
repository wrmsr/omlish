"""
TODO:
 - bootstrap lol
"""
import functools
import typing as ta

import anyio

from omlish import inject as inj
from omlish.argparse import all as ap
from omlish.logs import all as logs

from .inject import bind_main
from .profiles import PROFILE_TYPES
from .secrets import install_env_secrets
from .sessions.base import Session
from .sessions.configs import SessionConfig


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


async def _run_session_cfg(
        session_cfg: SessionConfig,
        *,
        profile_name: str | None = None,
) -> None:
    async with inj.create_async_managed_injector(bind_main(
            session_cfg=session_cfg,
            profile_name=profile_name,
    )) as injector:
        await (await injector[Session]).run()


##


MAIN_PROFILE_ARGS: ta.Sequence[ap.Arg] = [
    ap.arg('-p', '--profile', default='chat'),
    ap.arg('-h', '--help', action='store_true'),
    ap.arg('args', nargs=ap.REMAINDER),
]


async def _a_main(argv: ta.Any = None) -> None:
    parser = ap.ArgumentParser(add_help=False)

    for a in [*MAIN_PROFILE_ARGS, *MAIN_EXTRA_ARGS]:
        parser.add_argument(*a.args, **a.kwargs)

    args, unk_args = parser.parse_known_args(argv)

    _process_main_extra_args(args)

    install_env_secrets()

    profile_cls = PROFILE_TYPES[args.profile]
    profile = profile_cls()

    session_cfg = profile.configure([
        *unk_args,
        *(['--help'] if args.help else []),
        *args.args,
    ])

    await _run_session_cfg(
        session_cfg,
        profile_name=args.profile,
    )


def _main(args: ta.Any = None) -> None:
    anyio.run(
        functools.partial(
            _a_main,
            args,
        ),
    )  # noqa


if __name__ == '__main__':
    _main()
