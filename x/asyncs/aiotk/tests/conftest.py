# -*- coding: utf-8 -*-


import os
import pytest
import testfixtures

from contextlib import contextmanager

from aiotk import monkey_patch


@contextmanager
def cwd(new_cwd):
    """Context manager to swap the current working directory."""

    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(old_cwd)


@pytest.yield_fixture(scope='function')
def tempdir():
    """py.test fixture to create a temporary folder for a test."""

    with testfixtures.TempDirectory(create=True) as d:
        yield d
        d.cleanup()


@pytest.yield_fixture(scope='function')
def tempcwd(tempdir):
    """py.test fixture to move into a temporary folder for a test."""

    with cwd(tempdir.path):
        yield


@pytest.fixture(scope='session')
def monkey():
    """py.test fixture to apply monkey patches."""
    monkey_patch()
