#!/usr/bin/env python3
# ruff: noqa: UP006 UP007
# @omlish-amalg ../scripts/supervisor.py
import itertools
import os.path
import typing as ta

from omlish.lite.inject import inj
from omlish.lite.journald import journald_log_handler_factory
from omlish.lite.logs import configure_standard_logging

from ..configs import ConfigMapping
from ..configs import build_config_named_children
from ..configs import read_config_file
from .compat import ExitNow
from .compat import get_open_fds
from .configs import ServerConfig
from .context import ServerContext
from .states import SupervisorStates
from .supervisor import Supervisor


##


def prepare_process_group_config(dct: ConfigMapping) -> ConfigMapping:
    out = dict(dct)
    out['processes'] = build_config_named_children(out.get('processes'))
    return out


def prepare_server_config(dct: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, ta.Any]:
    out = dict(dct)
    group_dcts = build_config_named_children(out.get('groups'))
    out['groups'] = [prepare_process_group_config(group_dct) for group_dct in group_dcts or []]
    return out


##


def main(
        argv: ta.Optional[ta.Sequence[str]] = None,
        *,
        no_logging: bool = False,
) -> None:
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

    initial_fds: ta.Optional[ta.FrozenSet[int]] = None
    if args.inherit_initial_fds:
        initial_fds = get_open_fds(0x10000)

    # if we hup, restart by making a new Supervisor()
    for epoch in itertools.count():
        config = read_config_file(
            os.path.expanduser(cf),
            ServerConfig,
            prepare=prepare_server_config,
        )

        context = ServerContext(
            config,
            epoch=epoch,
            inherited_fds=initial_fds,
        )

        injector = inj.create_injector(
            inj.bind(config),
            inj.bind(context),
            inj.bind(Supervisor, singleton=True),
        )

        supervisor = injector.provide(Supervisor)
        try:
            supervisor.main()
        except ExitNow:
            pass

        if context.state < SupervisorStates.RESTARTING:
            break


if __name__ == '__main__':
    main()
