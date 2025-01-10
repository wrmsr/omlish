import dataclasses as dc
import keyword
import os.path
import sys
import typing as ta

from omlish import check
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

    def _gen_module(
            self,
            service_name: str,
            *,
            shape_names: ta.Iterable[str] | None = None,
            operation_names: ta.Iterable[str] | None = None,
    ) -> str:
        service_model = ModelGen.load_service_model(service_name)

        shape_names_seq = check.unique(shape_names or ())
        operation_names_seq = check.unique(operation_names or ())

        bmg = ModelGen(
            service_model,
            shape_names=ModelGen.get_referenced_shape_names(
                service_model,
                shape_names=shape_names_seq,
                operation_names=operation_names_seq,
            ),
            operation_names=operation_names_seq,
        )

        return bmg.gen_module()

    @ap.cmd(
        ap.arg('service'),
        ap.arg('-s', '--shape', action='append'),
        ap.arg('-o', '--operation', action='append'),
    )
    def gen_module(self) -> None:
        mod = self._gen_module(
            self.args.service,
            shape_names=self._arg_list(self.args.shape),
            operation_names=self._arg_list(self.args.operation),
        )

        sys.stdout.write(mod)

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
        mod = self._gen_module(
            svc.name,
            shape_names=svc.shapes,
            operation_names=svc.operations,
        )

        fn = svc.name
        if fn in keyword.kwlist:
            fn += '_'
        output_file = os.path.join(output_dir, f'{fn}.py')
        with open(output_file, 'w') as f:
            f.write(mod)

    @ap.cmd(
        ap.arg('config-file', nargs='?'),
    )
    def gen_services(self) -> None:
        config_file = self.args.config_file
        if config_file is None:
            config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/services.toml'))

        cfg_dct = dict(configs.DEFAULT_FILE_LOADER.load_file(config_file).as_map())
        cfg_dct = configs.processing.matched_rewrite(
            configs.processing.build_named_children,
            cfg_dct,
            ('services',),
        )
        cfg: Cli.ServicesConfig = msh.unmarshal(cfg_dct, Cli.ServicesConfig)

        output_dir = os.path.dirname(os.path.abspath(config_file))

        for svc in cfg.services or []:
            self._gen_service(svc, output_dir)

    #

    @ap.cmd()
    def list_services(self) -> None:
        for name in sorted(ModelGen.list_available_services()):
            print(name)

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
