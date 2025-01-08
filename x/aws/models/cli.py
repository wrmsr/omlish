"""
TODO:
 - default values? nullability? maybe a new_default helper?
 - relative import base

==

gen-module ec2 -o DescribeInstances
"""
import dataclasses as dc
import os.path
import sys
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.configs import all as configs

from .gen import ModelGen


##


class Cli(ap.Cli):
    def _arg_list(self, s: ta.Iterable[str] | None) -> list[str]:
        return list(lang.flatten(e.split(',') for e in s or []))

    #

    @ap.cmd(
        ap.arg('service'),
        ap.arg('-s', '--shape', action='append'),
        ap.arg('-o', '--operation', action='append'),
    )
    def gen_module(self) -> None:
        shape_names = self._arg_list(self.args.shape)
        operation_names = self._arg_list(self.args.operation)

        service_model = ModelGen.load_service_model(self.args.service)

        bmg = ModelGen(
            service_model,
            shape_names=ModelGen.get_referenced_shape_names(
                service_model,
                shape_names=shape_names,
                operation_names=operation_names,
            ),
            operation_names=operation_names,
        )

        sys.stdout.write(bmg.gen_module())

    #

    @dc.dataclass(frozen=True)
    class ServicesConfig:
        @dc.dataclass(frozen=True)
        class Service:
            name: str
            shapes: ta.Sequence[str] | None = None
            operations: ta.Sequence[str] | None = None

        services: ta.Sequence[Service] | None = None

    def _gen_service(
            self,
            svc: ServicesConfig.Service,
            output_dir: str,
    ) -> None:
        raise NotImplementedError

    @ap.cmd(
        ap.arg('config-file'),
    )
    def gen_services(self) -> None:
        config_file = self.args.config_file

        cfg_dct = dict(configs.DEFAULT_FILE_LOADER.load_file(config_file).as_map())
        cfg_dct['services'] = configs.processing.build_named_children(cfg_dct['services'])
        cfg: Cli.ServicesConfig = msh.unmarshal(cfg_dct, Cli.ServicesConfig)

        output_dir = os.path.dirname(os.path.abspath(config_file))

        for svc in cfg.services:
            self._gen_service(svc, output_dir)

    #

    @ap.cmd(
        ap.arg('service'),
    )
    def list_shapes(self) -> None:
        service_model = ModelGen.load_service_model(self.args.service)
        for name in sorted(service_model.shape_names):
            print(name)

    @ap.cmd(
        ap.arg('service'),
    )
    def list_operations(self) -> None:
        service_model = ModelGen.load_service_model(self.args.service)
        for name in sorted(service_model.operation_names):
            print(name)


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
