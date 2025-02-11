import os
import shutil

import pytest

from ...subprocesses.sync import subprocesses  # noqa
from ..lsof import LsofCommand
from ..lsof import LsofItem


DARWIN_TEST_LSOF_LINES = """
p84733
cPython
u501
f5
tREG
D0x1000011
s0
i29307947
n/private/var/folders/5n/mz7p9dpn4c7cyxwnln7r61hr0000gn/T/tmparvx4lwi/foo.pid
p84743
cPython
u501
f5
tREG
D0x1000011
s0
i29307947
n/private/var/folders/5n/mz7p9dpn4c7cyxwnln7r61hr0000gn/T/tmparvx4lwi/foo.pid
""".strip().splitlines()


LINUX_TEST_LSOF_LINES = """
p3367981
cpython
u1000
f6
tREG
D0x1e
s0
i9723117
n/tmp/tmpczn1zg20/foo.pid
p3368014
cpython
u1000
f5
tREG
D0x1e
s0
i9723117
n/tmp/tmpczn1zg20/foo.pid
""".strip().splitlines()


def test_lsof_parse():
    print(LsofItem.from_prefix_lines(DARWIN_TEST_LSOF_LINES))


def test_lsof_cmd():
    if not shutil.which('lsof'):
        pytest.skip('no lsof command')
    print(LsofCommand(pid=os.getpid()).run())
