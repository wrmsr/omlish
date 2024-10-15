import dataclasses as dc
import typing as ta

from . import runhack as rh


##


@dc.dataclass(frozen=True)
class RunConfig:
    argv: ta.Sequence[str]
    orig_argv: ta.Sequence[str]


PYTHON = '/Users/spinlock/.pyenv/versions/3.12.7/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python'
PYDEVD = '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py'
PYCACHE_PREFIX = 'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache'


#


RUN_MODULE_NO_ARG_CFG = RunConfig(**{
    'argv': [
        '-m',
    ],
    'orig_argv': [
        'python',
        '-m',
        'x.js',
    ],
})

RUN_MODULE_FOO_ARG_CFG = RunConfig(**{
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

RUN_FILE_NO_ARG_CFG = RunConfig(**{
    'argv': [
        'x/js.py',
    ],
    'orig_argv': [
        'python',
        'x/js.py',
    ],
})

RUN_FILE_FOO_ARG_CFG = RunConfig(**{
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


##


def test_params():
    for argv in [
        [
            '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py',
            '--multiprocess',
            '--qt-support=auto',
            '--client',
            '127.0.0.1',
            '--port',
            '64701',
            '--file',
            '/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs/lfs.py',
        ],
        [
            '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py',
            '--multiprocess',
            '--client',
            '127.0.0.1',
            '--port',
            '56431',
            '--file',
            '/Users/spinlock/src/wrmsr/omlish/x/llm/cli/main.py',
        ],
        [
            '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py',
            '--multiprocess',
            '--qt-support=auto',
            '--client',
            '127.0.0.1',
            '--port',
            '64722',
            '--file',
            '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py',
            '--path',
            '/Users/spinlock/src/wrmsr/omlish/omlish/lifecycles/tests/test_lifecycles.py',
        ],
        [
            '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py',
            '--multiprocess',
            '--qt-support=auto',
            '--client',
            '127.0.0.1',
            '--port',
            '50791',
            '--file',
            '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py',
            '--target',
            'omlish/diag/tests/test_asts.py::test_check_equal',
        ],
    ]:
        t = rh.parse_args_target(argv)
        print(t)
