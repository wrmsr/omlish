import subprocess

import pytest

from .. import subprocesses as su


def test_subprocesses_call():
    su.subprocess_check_call('true')
    with pytest.raises(subprocess.CalledProcessError):
        su.subprocess_check_call('false')
    assert su.subprocess_try_call('true')
    assert not su.subprocess_try_call('false')


def test_subprocesses_output():
    su.subprocess_check_output('echo', 'hi')
    with pytest.raises(FileNotFoundError):
        su.subprocess_check_output('xcho', 'hi')
    su.subprocess_try_output('echo', 'hi')
    assert su.subprocess_try_output('xcho', 'hi') is None
