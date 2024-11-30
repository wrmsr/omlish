import os.path
import pwd

from omlish.lite.logs import log

from ..base import Concern
from ..base import Phase
from ..base import run_in_phase


class DirsConcern(Concern):
    @run_in_phase(Phase.HOST)
    def create_dirs(self) -> None:
        pwn = pwd.getpwnam(self._d.host_cfg.username)

        for dn in [
            'app',
            'conf',
            'conf/env',
            'conf/nginx',
            'conf/supervisor',
            'venv',
        ]:
            fp = os.path.join(self._d.home_dir(), dn)
            if not os.path.exists(fp):
                log.info('Creating directory: %s', fp)
                os.mkdir(fp)
                os.chown(fp, pwn.pw_uid, pwn.pw_gid)
