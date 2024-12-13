import logging  # noqa

import pytest  # noqa

from ...logs import all as logs  # noqa
from ...testing import pytest as ptu
from ..threadlets import GreenletThreadlets
from ..threadlets import Threadlets
from .real import RealThreadlets


def _test_threadlets(api: Threadlets):
    done = 0

    def test1():
        gr2.switch()
        gr2.switch()
        nonlocal done
        done += 1

    def test2():
        def f():
            gr1.switch()
        f()
        nonlocal done
        done += 1
        gr1.switch()

    gr1 = api.spawn(test1)
    gr2 = api.spawn(test2)
    gr1.switch()
    assert done == 2


# @pytest.mark.skip
@ptu.skip.if_cant_import('greenlet')
def test_greenlet():
    _test_threadlets(GreenletThreadlets())


LOG_LIST = logs.ListHandler()


@pytest.mark.skip
def test_real():
    logs.configure_standard_logging('DEBUG')
    logging.root.addHandler(LOG_LIST)

    s = RealThreadlets()
    _test_threadlets(s)
    s.shutdown()
