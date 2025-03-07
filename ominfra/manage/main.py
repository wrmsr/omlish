# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import asyncio
import dataclasses as dc
import json
import os.path
import sys
import typing as ta

from omdev.home.paths import get_home_paths
from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.configs import load_config_file_obj
from omlish.lite.logs import log  # noqa
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.marshal import ObjMarshalOptions
from omlish.lite.pycharm import PycharmRemoteDebug

from .bootstrap import MainBootstrap
from .bootstrap_ import main_bootstrap
from .commands.base import Command
from .config import MainConfig
from .deploy.config import DeployConfig
from .remote.config import RemoteConfig
from .targets.connection import ManageTargetConnector
from .targets.targets import ManageTarget


@dc.dataclass(frozen=True)
class ManageConfig:
    targets: ta.Optional[ta.Mapping[str, ManageTarget]] = None


class MainCli(ArgparseCli):
    config_file: ta.Optional[str] = argparse_arg('--config-file', help='Config file path')  # type: ignore

    @cached_nullary
    def config(self) -> ManageConfig:
        if (cf := self.config_file) is None:
            cf = os.path.join(get_home_paths().config_dir, 'manage', 'manage.yml')
            if not os.path.isfile(cf):
                cf = None

        if cf is None:
            return ManageConfig()
        else:
            return load_config_file_obj(cf, ManageConfig)

    #

    @argparse_cmd(
        argparse_arg('--_payload-file'),

        argparse_arg('--pycharm-debug-port', type=int),
        argparse_arg('--pycharm-debug-host'),
        argparse_arg('--pycharm-debug-version'),

        argparse_arg('--remote-timebomb-delay-s', type=float),

        argparse_arg('--debug', action='store_true'),

        argparse_arg('target'),
        argparse_arg('-f', '--command-file', action='append'),
        argparse_arg('command', nargs='*'),
    )
    async def run(self) -> None:
        bs = MainBootstrap(
            main_config=MainConfig(
                log_level='DEBUG' if self.args.debug else 'INFO',

                debug=bool(self.args.debug),
            ),

            deploy_config=DeployConfig(),

            remote_config=RemoteConfig(
                payload_file=self.args._payload_file,  # noqa

                pycharm_remote_debug=PycharmRemoteDebug(
                    port=self.args.pycharm_debug_port,
                    **(dict(host=self.args.pycharm_debug_host) if self.args.pycharm_debug_host is not None else {}),
                    install_version=self.args.pycharm_debug_version,
                ) if self.args.pycharm_debug_port is not None else None,

                timebomb_delay_s=self.args.remote_timebomb_delay_s,
            ),
        )

        #

        injector = main_bootstrap(
            bs,
        )

        #

        msh = injector[ObjMarshalerManager]

        tgt: ManageTarget
        if not (ts := self.args.target).startswith('{'):
            tgt = check.not_none(self.config().targets)[ts]
        else:
            tgt = msh.unmarshal_obj(json.loads(ts), ManageTarget)

        #

        cmds: ta.List[Command] = []

        cmd: Command

        for c in self.args.command or []:
            if not c.startswith('{'):
                c = json.dumps({c: {}})
            cmd = msh.unmarshal_obj(json.loads(c), Command)
            cmds.append(cmd)

        for cf in self.args.command_file or []:
            cmd = load_config_file_obj(cf, Command, msh=msh)
            cmds.append(cmd)

        #

        async with injector[ManageTargetConnector].connect(tgt) as ce:
            async def run_command(cmd: Command) -> None:
                res = await ce.try_execute(
                    cmd,
                    log=log,
                    omit_exc_object=True,
                )

                print(msh.marshal_obj(res, opts=ObjMarshalOptions(raw_bytes=True)))

            await asyncio.gather(*[
                run_command(cmd)
                for cmd in cmds
            ])


def _main() -> None:
    sys.exit(asyncio.run(MainCli().async_cli_run()))


if __name__ == '__main__':
    _main()
