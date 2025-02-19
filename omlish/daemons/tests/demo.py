import dataclasses as dc
import functools  # noqa
import logging
import os.path
import tempfile
import time
import urllib.request

from ... import check
from ... import lang  # noqa
from ...logs import all as logs
from ..daemon import Daemon
from ..spawning import ForkSpawning  # noqa
from ..spawning import MultiprocessingSpawning  # noqa
from ..spawning import ThreadSpawning  # noqa
from ..targets import NameTarget  # noqa
from ..targets import Target
from .hi import HiService
from .hi import hi


log = logging.getLogger(__name__)


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    temp_dir = tempfile.mkdtemp()
    pid_file = os.path.join(temp_dir, 'daemon_demo.pid')
    log.info('pid_file: %s', pid_file)

    #

    daemon = Daemon(
        target=Target.of(
            hi().service_(),
            # functools.partial(HiServer.run_config, hi.server),
            # '.'.join([lang.get_real_module_name(globals()), 'run_hi_server']),
            # NameTarget.for_obj(run_hi_server, no_module_name_lookup=True),
            # 'omlish.daemons.tests.demo.run_hi_server',
            # 'omlish.daemons.tests.demo.hi_service_config',
        ),
        config=dc.replace(
            hi().daemon_().config,
            spawning=ThreadSpawning(),
            # spawning=MultiprocessingSpawning(),
            # spawning=ForkSpawning(),
        ),
    )

    daemon.launch()

    #

    if daemon.config.pid_file is not None:
        check.state(daemon.is_pidfile_locked())

    req_str = 'Hi! How are you?'

    hi_server_config = check.isinstance(hi().service_(), HiService).server.config

    with urllib.request.urlopen(urllib.request.Request(
        f'http://localhost:{hi_server_config.port}/',
        data=req_str.encode('utf-8'),
    )) as resp:
        resp_str = resp.read().decode('utf-8')

    log.info('Response: %r', resp_str)

    for i in range(10, 0, -1):
        log.info('Parent process sleeping %d', i)
        time.sleep(1.)


if __name__ == '__main__':
    _main()
