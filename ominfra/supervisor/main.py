#!/usr/bin/env python3
# ruff: noqa: UP006 UP007
# @omlish-amalg ../scripts/supervisor.py
import itertools
import os.path
import typing as ta

from omlish.lite.http.coroserver import CoroHttpServer
from omlish.lite.inject import inj
from omlish.lite.journald import journald_log_handler_factory
from omlish.lite.logs import configure_standard_logging

from ..configs import read_config_file
from .configs import ServerConfig
from .configs import prepare_server_config
from .context import ServerContextImpl
from .context import ServerEpoch
from .inject import bind_server
from .process import InheritedFds
from .states import SupervisorState
from .supervisor import Supervisor
from .utils import ExitNow
from .utils import get_open_fds


##


def main(
        argv: ta.Optional[ta.Sequence[str]] = None,
        *,
        no_logging: bool = False,
) -> None:
    server_cls = CoroHttpServer  # noqa

    #

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', metavar='config-file')
    parser.add_argument('--no-journald', action='store_true')
    parser.add_argument('--inherit-initial-fds', action='store_true')
    args = parser.parse_args(argv)

    #

    if not (cf := args.config_file):
        raise RuntimeError('No config file specified')

    if not no_logging:
        configure_standard_logging(
            'INFO',
            handler_factory=journald_log_handler_factory if not args.no_journald else None,
        )

    #

    inherited_fds: ta.Optional[InheritedFds] = None
    if args.inherit_initial_fds:
        inherited_fds = InheritedFds(get_open_fds(0x10000))

    # if we hup, restart by making a new Supervisor()
    for epoch in itertools.count():
        config = read_config_file(
            os.path.expanduser(cf),
            ServerConfig,
            prepare=prepare_server_config,
        )

        injector = inj.create_injector(bind_server(
            config,
            server_epoch=ServerEpoch(epoch),
            inherited_fds=inherited_fds,
        ))

        context = injector[ServerContextImpl]
        supervisor = injector[Supervisor]

        try:
            supervisor.main()
        except ExitNow:
            pass

        if context.state < SupervisorState.RESTARTING:
            break


if __name__ == '__main__':
    main()
