"""
TODO:
 - https://stackoverflow.com/questions/3011067/restart-nginx-without-sudo
"""
import os.path
import textwrap

from omlish.lite.logs import log

from ..base import Concern
from ..base import Phase
from ..base import run_in_phase


class GlobalNginxConcern(Concern):
    @run_in_phase(Phase.HOST)
    def create_global_nginx_conf(self) -> None:
        nginx_conf_dir = os.path.join(self._d.home_dir(), 'conf/nginx')
        if not os.path.isfile(self._d.host_cfg.global_nginx_conf_file_path):
            log.info('Writing global nginx conf at %s', self._d.host_cfg.global_nginx_conf_file_path)
            with open(self._d.host_cfg.global_nginx_conf_file_path, 'w') as f:
                f.write(f'include {nginx_conf_dir}/*.conf;\n')


class NginxConcern(Concern):
    @run_in_phase(Phase.FRONTEND)
    def create_nginx_conf(self) -> None:
        nginx_conf = textwrap.dedent(f"""
            server {{
                listen 80;
                location / {{
                    proxy_pass http://127.0.0.1:8000/;
                }}
            }}
        """)
        nginx_conf_file = os.path.join(self._d.home_dir(), f'conf/nginx/{self._d.cfg.app_name}.conf')
        log.info('Writing nginx conf to %s', nginx_conf_file)
        with open(nginx_conf_file, 'w') as f:
            f.write(nginx_conf)

    @run_in_phase(Phase.START_FRONTEND)
    def poke_nginx(self) -> None:
        log.info('Starting nginx')
        self._d.sh('service nginx start')

        log.info('Poking nginx')
        self._d.sh('nginx -s reload')
