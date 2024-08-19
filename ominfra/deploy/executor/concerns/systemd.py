"""
TODO:
 - loginctl enable-linger $USER

==

# https://serverfault.com/questions/617823/how-to-set-systemd-service-dependencies
PIDFile=/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true
"""
import os.path
import textwrap

from omlish.lite.logs import log

from ..base import Concern
from ..base import Phase
from ..base import run_in_phase


class SystemdConcern(Concern):
    service_name: str

    @run_in_phase(Phase.HOST)
    def create_systemd_path(self) -> None:
        sd_svc_dir = os.path.join(self._d.home_dir(), f'.config/systemd/user')
        if not os.path.exists(sd_svc_dir):
            log.info('Creating directory: %s', sd_svc_dir)
            os.makedirs(sd_svc_dir)

    @run_in_phase(Phase.BACKEND)
    def create_systemd_service(self) -> None:
        sd_svc = textwrap.dedent(f"""
            [Unit]
            Description={self.service_name}
            After= \
                syslog.target \
                network.target \
                remote-fs.target \
                nss-lookup.target \
                network-online.target

            [Service]
            Type=simple
            StandardOutput=journal
            ExecStart={self._d.home_dir()}/venv/{self._d.cfg.app_name}/bin/python -m {self._d.cfg.entrypoint}
            WorkingDirectory={self._d.home_dir()}/app/{self._d.cfg.app_name}

            Restart=always
            RestartSec=3

            [Install]
            WantedBy=multi-user.target
        """)
        sd_svc_file = os.path.join(self._d.home_dir(), f'.config/systemd/user/{self.service_name}.service')
        log.info('Writing systemd service to %s', sd_svc_file)
        with open(sd_svc_file, 'w') as f:
            f.write(sd_svc)

    @run_in_phase(Phase.START_BACKEND)
    def poke_systemd(self) -> None:
        log.info('Poking systemd')
        self._d.sh('systemctl --user daemon-reload')
        self._d.sh(f'systemctl --user enable {self.service_name}')
        self._d.sh(f'systemctl --user restart {self.service_name}')
