import dataclasses as dc
import typing as ta

from . import runhack as rh


##


@dc.dataclass(frozen=True)
class RunConfig:
    argv: list[str]
    orig_argv: list[str]
    cwd: str | None = None


#


PYTHON = '/Users/spinlock/.pyenv/versions/3.12.7/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python'  # noqa
PYDEVD = '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py'
TEST_RUNNER = '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py'
PYCACHE_PREFIX = 'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache'


#


RUN_FILE_NO_ARG = RunConfig(**{
    'argv': [
        'x/js.py',
    ],
    'orig_argv': [
        'python',
        'x/js.py',
    ],
})

RUN_FILE_FOO_ARG = RunConfig(**{
    'argv': [
        'x/js.py',
        'foo',
    ],
    'orig_argv': [
        'python',
        'x/js.py',
        'foo',
    ],
})

RUN_MODULE_NO_ARG = RunConfig(**{
    'argv': [
        '-m',
    ],
    'orig_argv': [
        'python',
        '-m',
        'x.js',
    ],
})

RUN_MODULE_FOO_ARG = RunConfig(**{
    'argv': [
        '-m',
        'foo',
    ],
    'orig_argv': [
        'python',
        '-m',
        'x.js',
        'foo',
    ],
})


#


DEBUG_FILE_NO_ARG = RunConfig(**{
    'argv': [
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55770',
        '--file',
        'x/js.py',
    ],
    'orig_argv': [
        PYTHON,
        '-X',
        PYCACHE_PREFIX,
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55770',
        '--file',
        'x/js.py'
    ],
})

DEBUG_FILE_FOO_ARG = RunConfig(**{
    'argv': [
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55780',
        '--file',
        'x/js.py',
        'foo',
    ],
    'orig_argv': [
        PYTHON,
        '-X',
        PYCACHE_PREFIX,
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55780',
        '--file',
        'x/js.py',
        'foo',
    ],
})

DEBUG_MODULE_NO_ARG = RunConfig(**{
    'argv': [
        PYDEVD,
        '--module',
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55806',
        '--file',
        'x.js',
    ],
    'orig_argv': [
        PYTHON,
        '-X',
        PYCACHE_PREFIX,
        PYDEVD,
        '--module',
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55806',
        '--file',
        'x.js',
    ],
})

DEBUG_MODULE_FOO_ARG = RunConfig(**{
    'argv': [
        PYDEVD,
        '--module',
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55815',
        '--file',
        'x.js',
        'foo',
    ],
    'orig_argv': [
        PYTHON,
        '-X',
        PYCACHE_PREFIX,
        PYDEVD,
        '--module',
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55815',
        '--file',
        'x.js',
        'foo',
    ],
})


#


RUN_TEST_FILE = RunConfig(**{
    'argv': [
        TEST_RUNNER,
        '--path',
        'ommlx/minichain/tests/test_strings.py',
    ],
    'orig_argv': [
        PYTHON,
        TEST_RUNNER,
        '--path',
        'ommlx/minichain/tests/test_strings.py',
    ],
    'cwd': 'ommlx',
})

RUN_TEST_MODULE = RunConfig(**{
    'argv': [
        TEST_RUNNER,
        '--path',
        'ommlx/minichain/tests/test_strings.py',
    ],
    'orig_argv': [
        PYTHON,
        TEST_RUNNER,
        '--path',
        'ommlx/minichain/tests/test_strings.py',
    ],
})

RUN_TEST_SINGLE = RunConfig(**{
    'argv': [
        TEST_RUNNER,
        '--target',
        'minichain/tests/test_strings.py::test_transforms',
    ],
    'orig_argv': [
        PYTHON,
        TEST_RUNNER,
        '--target',
        'minichain/tests/test_strings.py::test_transforms',
    ],
    'cwd': 'ommlx',
})


#


DEBUG_TEST_FILE = RunConfig(**{
    'argv': [
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55840',
        '--file',
        TEST_RUNNER,
        '--path',
        'ommlx/minichain/tests/test_strings.py',
    ],
    'orig_argv': [
        PYTHON,
        '-X',
        PYCACHE_PREFIX,
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55840',
        '--file',
        TEST_RUNNER,
        '--path',
        'ommlx/minichain/tests/test_strings.py',
    ],
})

DEBUG_TEST_MODULE = RunConfig(**{
    'argv': [
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55829',
        '--file',
        TEST_RUNNER,
        '--path',
        'test_strings.py',
    ],
    'orig_argv': [
        PYTHON,
        '-X',
        PYCACHE_PREFIX,
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55829',
        '--file',
        TEST_RUNNER,
        '--path',
        'test_strings.py',
    ],
    'cwd': 'ommlx/minichain/tests',
})

DEBUG_TEST_SINGLE = RunConfig(**{
    'argv': [
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55860',
        '--file',
        TEST_RUNNER,
        '--target',
        'minichain/tests/test_strings.py::test_transforms',
    ],
    'orig_argv': [
        PYTHON,
        '-X',
        PYCACHE_PREFIX,
        PYDEVD,
        '--multiprocess',
        '--qt-support=auto',
        '--client',
        '127.0.0.1',
        '--port',
        '55860',
        '--file',
        TEST_RUNNER,
        '--target',
        'minichain/tests/test_strings.py::test_transforms',
    ],
    'cwd': 'ommlx',
})


##


def test_params():
    for rc in [
        RUN_FILE_NO_ARG,
        RUN_FILE_FOO_ARG,
        RUN_MODULE_NO_ARG,
        RUN_MODULE_FOO_ARG,

        DEBUG_FILE_NO_ARG,
        DEBUG_FILE_FOO_ARG,
        DEBUG_MODULE_NO_ARG,
        DEBUG_MODULE_FOO_ARG,

        RUN_TEST_FILE,
        RUN_TEST_MODULE,
        RUN_TEST_SINGLE,

        DEBUG_TEST_FILE,
        DEBUG_TEST_MODULE,
        DEBUG_TEST_SINGLE,
    ]:
        t = rh.parse_exec(rc.orig_argv)
        print(t)
