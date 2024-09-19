"""
*** THIS GOES IN OMDEV lol ***
 - or..? pycharm already in core lol..

pycharm 242.21829.153

https://github.com/JetBrains/intellij-community/blob/6400f70dde6f743e39a257a5a78cc51b644c835e/python/helpers/pycharm/_jb_pytest_runner.py
https://github.com/JetBrains/intellij-community/blob/5a4e584aa59767f2e7cf4bd377adfaaf7503984b/python/helpers/pycharm/_jb_runner_tools.py

==

https://docs.python.org/3/library/site.html

https://github.com/xolox/python-coloredlogs/blob/65bdfe976ac0bf81e8c0bd9a98242b9d666b2859/setup.py#L64

_distutils_hack


==

sys.argv=['/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64678', '--file', '/Users/spinlock/src/wrmsr/omlish/x/asts/marshal.py']
sys.orig_argv=['/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python', '-X', 'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache', '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64678', '--file', '/Users/spinlock/src/wrmsr/omlish/x/asts/marshal.py']

sys.argv=['/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64687', '--file', '/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs/lfs.py']
sys.orig_argv=['/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python', '-X', 'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache', '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64687', '--file', '/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs/lfs.py']

==
BUSTED:

sys.argv=[
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py',
  '--multiprocess',
  '--qt-support=auto',
  '--client',
  '127.0.0.1',
  '--port',
  '64701',
  '--file',
  '/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs/lfs.py',
]
sys.orig_argv=[
  '/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python',
  '-X',
  'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache',
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py',
  '--multiprocess',
  '--qt-support=auto',
  '--client',
  '127.0.0.1',
  '--port',
  '64701',
  '--file',
  '/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs/lfs.py',
]
os.getcwd()='/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs'
sorted(os.environ)=[
  'ASYNCIO_DEBUGGER_ENV',
  'COMMAND_MODE',
  'DISPLAY',
  'DOCKER_CLI_HINTS',
  'HALT_VARIABLE_RESOLVE_THREADS_ON_STEP_RESUME',
  'HOME',
  'HOMEBREW_CELLAR',
  'HOMEBREW_PREFIX',
  'HOMEBREW_REPOSITORY',
  'IDE_PROJECT_ROOTS',
  'INFOPATH',
  'IPYTHONENABLE',
  'LC_CTYPE',
  'LESS',
  'LIBRARY_ROOTS',
  'LOGNAME',
  'LSCOLORS',
  'LS_COLORS',
  'OLDPWD',
  'PAGER',
  'PATH',
  'PS1',
  'PWD',
  'PYCHARM_DISPLAY_PORT',
  'PYCHARM_HOSTED',
  'PYCHARM_INTERACTIVE_PLOTS',
  'PYCHARM_PROJECT_ID',
  'PYDEVD_LOAD_VALUES_ASYNC',
  'PYTHONIOENCODING',
  'PYTHONPATH',
  'PYTHONUNBUFFERED',
  'SHELL',
  'TMPDIR',
  'USER',
  'USE_LOW_IMPACT_MONITORING',
  'VIRTUAL_ENV',
  'WASIENV_DIR',
  'WASMER_CACHE_DIR',
  'WASMER_DIR',
  'XPC_FLAGS',
  'XPC_SERVICE_NAME',
  'ZSH',
  '__CFBundleIdentifier',
  '__CF_USER_TEXT_ENCODING'
]

==
BUSTED:

sys.argv=[
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
]
sys.orig_argv=[
  '/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python',
  '-X',
  'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache',
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
]
os.getcwd()='/Users/spinlock/src/wrmsr/omlish/omlish'
sorted(os.environ)=[
  'ASYNCIO_DEBUGGER_ENV',
  'COMMAND_MODE',
  'DISPLAY',
  'DOCKER_CLI_HINTS',
  'HALT_VARIABLE_RESOLVE_THREADS_ON_STEP_RESUME',
  'HOME',
  'HOMEBREW_CELLAR',
  'HOMEBREW_PREFIX',
  'HOMEBREW_REPOSITORY',
  'IDE_PROJECT_ROOTS',
  'INFOPATH',
  'IPYTHONENABLE',
  'LC_CTYPE',
  'LESS',
  'LIBRARY_ROOTS',
  'LOGNAME',
  'LSCOLORS',
  'LS_COLORS',
  'OLDPWD',
  'PAGER',
  'PATH',
  'PS1',
  'PWD',
  'PYCHARM_DISPLAY_PORT',
  'PYCHARM_HELPERS_DIR',
  'PYCHARM_HOSTED',
  'PYCHARM_INTERACTIVE_PLOTS',
  'PYCHARM_PROJECT_ID',
  'PYDEVD_LOAD_VALUES_ASYNC',
  'PYTEST_RUN_CONFIG',
  'PYTHONIOENCODING',
  'PYTHONPATH',
  'PYTHONUNBUFFERED',
  'SHELL',
  'TMPDIR',
  'USER',
  'USE_LOW_IMPACT_MONITORING',
  'VIRTUAL_ENV',
  'WASIENV_DIR',
  'WASMER_CACHE_DIR',
  'WASMER_DIR',
  'XPC_FLAGS',
  'XPC_SERVICE_NAME',
  'ZSH',
  '__CFBundleIdentifier',
  '__CF_USER_TEXT_ENCODING',
]

==
GOOD

sys.argv=[
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
]
sys.orig_argv=[
  '/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python',
  '-X',
  'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache',
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
]
os.getcwd()='/Users/spinlock/src/wrmsr/omlish'

====

'ASYNCIO_DEBUGGER_ENV' = 'True'
'HALT_VARIABLE_RESOLVE_THREADS_ON_STEP_RESUME' = 'True'
'IDE_PROJECT_ROOTS' = '/Users/spinlock/src/wrmsr/omlish'
'IPYTHONENABLE' = 'True'
'LC_CTYPE' = 'en_US.UTF-8'
'LOGNAME' = 'spinlock'
'OLDPWD' = '/'
'PWD' = '/Users/spinlock/src/wrmsr/omlish'
'PYCHARM_DISPLAY_PORT' = '63342'
'PYCHARM_HELPERS_DIR' = '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm'
'PYCHARM_HOSTED' = '1'
'PYCHARM_INTERACTIVE_PLOTS' = '1'
'PYCHARM_PROJECT_ID' = 'b53768a5'
'PYDEVD_LOAD_VALUES_ASYNC' = 'True'
'PYTEST_CURRENT_TEST' = 'omlish/diag/tests/test_asts.py::test_check_equal (call)'
'PYTEST_RUN_CONFIG' = 'True'
'PYTEST_VERSION' = '8.3.3'
'PYTHONIOENCODING' = 'UTF-8'
'PYTHONUNBUFFERED' = '1'
'TEAMCITY_VERSION' = 'LOCAL'
'USE_LOW_IMPACT_MONITORING' = 'True'
'VIRTUAL_ENV' = '/Users/spinlock/src/wrmsr/omlish/.venvs/default'
'_JB_PPRINT_PRIMITIVES' = '1'
'__CFBundleIdentifier' = 'com.jetbrains.pycharm'
'__CF_USER_TEXT_ENCODING' = '0x1F5:0x0:0x0'

==

os.environ["LIBRARY_ROOTS"]=
  /Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12:
  /Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/lib-dynload:
  /Users/spinlock/src/wrmsr/omlish/.venvs/default/lib/python3.12/site-packages:
  /Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/python_stubs/-2014666999:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/python-skeletons:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/typeshed/stdlib:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/typeshed/stubs/...

os.environ["PATH"]=
  /Users/spinlock/src/wrmsr/omlish/.venvs/default/bin:
  ...

os.environ["PYTHONPATH"]=
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/third_party/thriftpy:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm:
  /Users/spinlock/src/wrmsr/omlish:
  /Users/spinlock/src/wrmsr/omlish/tinygrad:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_plotly_backend:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_matplotlib_backend:
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_display:
  /Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cythonExtensions:
  /Applications/PyCharm.app/Contents/plugins/python/helpers-pro/pydevd_asyncio:
  /Users/spinlock/src/wrmsr/omlish'

====

sys.path=[
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/third_party/thriftpy',
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev',
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm',
  '/Users/spinlock/src/wrmsr/omlish',
  '/Users/spinlock/src/wrmsr/omlish/tinygrad',
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_plotly_backend',
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_matplotlib_backend',
  '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_display',
  '/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cythonExtensions',
  '/Applications/PyCharm.app/Contents/plugins/python/helpers-pro/pydevd_asyncio',
  '/Users/spinlock/src/wrmsr/omlish/omlish',
  '/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python312.zip',
  '/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12',
  '/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/lib-dynload',
  '/Users/spinlock/src/wrmsr/omlish/.venvs/default/lib/python3.12/site-packages'
]

====

sys.path=[
'/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/third_party/thriftpy',
'/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev',
'/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm',
'/Users/spinlock/src/wrmsr/omlish',
'/Users/spinlock/src/wrmsr/omlish/tinygrad',
'/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_plotly_backend',
'/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_matplotlib_backend',
'/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm_display',
'/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cythonExtensions',
'/Applications/PyCharm.app/Contents/plugins/python/helpers-pro/pydevd_asyncio',
'/Users/spinlock/src/wrmsr/omlish/omlish',
'/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python312.zip',
'/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12',
'/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/lib-dynload',
'/Users/spinlock/src/wrmsr/omlish/.venvs/default/lib/python3.12/site-packages'
]


====

BAD:
[..., '--path', '/Users/spinlock/src/wrmsr/omlish/omlish/lifecycles/tests/test_lifecycles.py']
os.getcwd()='/Users/spinlock/src/wrmsr/omlish/omlish'

GOOD:
[..., '--target', 'omlish/diag/tests/test_asts.py::test_check_equal']
os.getcwd()='/Users/spinlock/src/wrmsr/omlish'

"""
import os.path
import sys


r"""
omlish-pycharm-runhack.pth:
  import sys; exec('\n'.join(['try:', '  import x.runhack', 'except ImportError:', '  pass', 'else:', '  x.runhack._run()']))
"""  # noqa


_HAS_RUN = False


def _run() -> None:
    global _HAS_RUN
    if _HAS_RUN:
        return
    _HAS_RUN = True

    #

    # default_enabled = False
    default_enabled = True

    is_enabled = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_ENABLED', default_enabled))
    if not is_enabled:
        return

    #

    # default_debug = False
    default_debug = True

    is_debug = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_DEBUG', default_debug))

    def debug(*args, **kwargs):
        if is_debug:
            print(*args, **kwargs, file=sys.stderr)

    #

    debug(f'{sys.argv=}')
    debug(f'{sys.orig_argv=}')
    debug(f'{os.getcwd()=}')
    debug(f'{sorted(os.environ)=}')
    debug(f'{os.environ.get("LIBRARY_ROOTS")=}')
    debug(f'{os.environ.get("PATH")=}')
    debug(f'{os.environ.get("PYTHONPATH")=}')
    debug(f'{sys.path=}')

    # breakpoint()

    #

    if len(sys.argv) > 2 and sys.argv[-2] == '--path':
        ide_roots = os.environ['IDE_PROJECT_ROOTS'].split(os.pathsep)
        if len(ide_roots) != 1:
            raise Exception(ide_roots)
        root_dir = ide_roots[0]
        debug(f'{root_dir=}')

        os.chdir(root_dir)
        debug(f'{os.getcwd()=}')

        test_file = sys.argv[-1]
        test_dir = os.path.dirname(test_file)
        debug(f'{test_dir=}')

        rel_path = os.path.relpath(test_file, root_dir)
        debug(f'{rel_path=}')
        if not rel_path.endswith('.py'):
            raise Exception(rel_path)

        pkg_dir = os.path.join(root_dir, rel_path.split(os.sep)[0])
        debug(f'{pkg_dir=}')

        def is_pkg_dir(p: str) -> bool:
            return p == pkg_dir or p.startswith(pkg_dir + os.sep)

        os.environ['PYTHONPATH'] = os.pathsep.join(
            d
            for d in os.environ['PYTHONPATH'].split(os.pathsep)
            if not is_pkg_dir(d)
        )
        debug(f'{os.environ["PYTHONPATH"]=}')

        sys.path = [
            d
            for d in sys.path
            if not is_pkg_dir(d)
        ]
        debug(f'{sys.path=}')

        # mod_name = rel_path.rpartition('.')[0].replace(os.sep, '.')

        # TODO:
        #  - don't touch any args after '--'
        #  - otherwise, pairs of --path or --target
        #  - it appears take a single path *OR* any number of targets

        sys.argv[-2:] = [
            '--target',

            # Pytest: path_to_file.py::module_name::class_name::fun_name
            # When file is launched in pytest it should be file.py: you can't provide it as bare module
            # [t + ".py" if ":" not in t else t for t in joined_targets]

            # rel_path + '::test_lifecycles',  # one test
            # rel_path.rpartition('.')[0],  # whole file
            rel_path + '::test_lifecycles',  # whole file
        ]
        debug(f'{sys.argv=}')
