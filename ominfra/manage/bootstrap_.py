# ruff: noqa: UP006 UP007 UP045
from omlish.lite.inject import Injector
from omlish.lite.inject import inj
from omlish.logs.standard import configure_standard_logging

from .bootstrap import MainBootstrap
from .inject import bind_main


##


def main_bootstrap(bs: MainBootstrap) -> Injector:
    if (log_level := bs.main_config.log_level) is not None:
        configure_standard_logging(log_level)

    injector = inj.create_injector(bind_main(  # noqa
        main_config=bs.main_config,

        deploy_config=bs.deploy_config,
        remote_config=bs.remote_config,
        system_config=bs.system_config,

        main_bootstrap=bs,
    ))

    return injector
