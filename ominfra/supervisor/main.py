# ruff: noqa: UP006 UP007
# @omlish-amalg ../scripts/supervisor.py
#
# Supervisor is Copyright (c) 2006-2015 Agendaless Consulting and Contributors.
# (http://www.agendaless.com), All Rights Reserved
#
# Supervisor is licensed under the following license:
#
#  A copyright notice accompanies this license document that identifies the copyright holders.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions in source code must retain the accompanying copyright notice, this list of conditions, and the
#     following disclaimer.
#
#  2. Redistributions in binary form must reproduce the accompanying copyright notice, this list of conditions, and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Names of the copyright holders must not be used to endorse or promote products derived from this software without
#     prior written permission from the copyright holders.
#
#  4. If any files are modified, you must cause the modified files to carry prominent notices stating that you changed
#     the files and the date of any change.
#
#  Disclaimer
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT
#   NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#   EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import contextlib
import itertools
import os.path
import typing as ta

from omlish.http.coro.server import CoroHttpServer
from omlish.lite.configs import load_config_file_obj
from omlish.lite.inject import inj
from omlish.lite.runtime import is_debugger_attached
from omlish.logs.standard import configure_standard_logging
from omlish.os.journald import journald_log_handler_factory

from .configs import ServerConfig
from .configs import prepare_server_config
from .inject import bind_server
from .spawningimpl import InheritedFds
from .states import SupervisorState
from .supervisor import Supervisor
from .types import ExitNow
from .types import ServerEpoch
from .utils.fds import get_open_fds


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
            handler_factory=journald_log_handler_factory if not (args.no_journald or is_debugger_attached()) else None,
        )

    #

    inherited_fds: ta.Optional[InheritedFds] = None
    if args.inherit_initial_fds:
        inherited_fds = InheritedFds(get_open_fds(0x10000))

    # if we hup, restart by making a new Supervisor()
    for epoch in itertools.count():
        config = load_config_file_obj(
            os.path.expanduser(cf),
            ServerConfig,
            prepare=prepare_server_config,
        )

        with contextlib.ExitStack() as es:
            injector = inj.create_injector(bind_server(
                es,
                config,
                server_epoch=ServerEpoch(epoch),
                inherited_fds=inherited_fds,
            ))

            supervisor = injector[Supervisor]

            try:
                supervisor.main()
            except ExitNow:
                pass

        if supervisor.state < SupervisorState.RESTARTING:
            break


if __name__ == '__main__':
    main()
