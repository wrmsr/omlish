from . import runhack as rh



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
        pa = rh.parse_args(DEBUGGER_PARAMS, argv[1:])
        print(pa)
