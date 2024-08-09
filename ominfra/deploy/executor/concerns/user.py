import pwd

from omdev.amalg.std.logging import log

from ..base import Concern
from ..base import Phase
from ..base import run_in_phase


class User(Concern):
    @run_in_phase(Phase.HOST)
    def create_user(self) -> None:
        try:
            pwd.getpwnam(self._d.host_cfg.username)
        except KeyError:
            log.info('Creating user %s', self._d.host_cfg.username)
            self._d.sh(' '.join([
                'adduser',
                '--system',
                '--disabled-password',
                '--group',
                '--shell /bin/bash',
                self._d.host_cfg.username,
            ]))
            pwd.getpwnam(self._d.host_cfg.username)
