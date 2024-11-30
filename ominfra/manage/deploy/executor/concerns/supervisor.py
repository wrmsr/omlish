import os.path
import textwrap

from omlish.lite.logs import log

from ..base import Concern
from ..base import Phase
from ..base import run_in_phase


class GlobalSupervisorConcern(Concern):
    @run_in_phase(Phase.HOST)
    def create_global_supervisor_conf(self) -> None:
        sup_conf_dir = os.path.join(self._d.home_dir(), 'conf/supervisor')
        with open(self._d.host_cfg.global_supervisor_conf_file_path) as f:
            glo_sup_conf = f.read()
        if sup_conf_dir not in glo_sup_conf:
            log.info('Updating global supervisor conf at %s', self._d.host_cfg.global_supervisor_conf_file_path)  # noqa
            glo_sup_conf += textwrap.dedent(f"""
                [include]
                files = {self._d.home_dir()}/conf/supervisor/*.conf
            """)
            with open(self._d.host_cfg.global_supervisor_conf_file_path, 'w') as f:
                f.write(glo_sup_conf)


class SupervisorConcern(Concern):
    @run_in_phase(Phase.BACKEND)
    def create_supervisor_conf(self) -> None:
        sup_conf = textwrap.dedent(f"""
            [program:{self._d.cfg.app_name}]
            command={self._d.home_dir()}/venv/{self._d.cfg.app_name}/bin/python -m {self._d.cfg.entrypoint}
            directory={self._d.home_dir()}/app/{self._d.cfg.app_name}
            user={self._d.host_cfg.username}
            autostart=true
            autorestart=true
        """)
        sup_conf_file = os.path.join(self._d.home_dir(), f'conf/supervisor/{self._d.cfg.app_name}.conf')
        log.info('Writing supervisor conf to %s', sup_conf_file)
        with open(sup_conf_file, 'w') as f:
            f.write(sup_conf)

    @run_in_phase(Phase.START_BACKEND)
    def poke_supervisor(self) -> None:
        log.info('Poking supervisor')
        self._d.sh('kill -HUP 1')
