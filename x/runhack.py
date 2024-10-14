"""
What this does:
 -

bad argv = cwd=/x
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py
  ...
  --file
  /x/y.py

bad argv = cwd=/x
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py
  ...
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py
  --path
  /x/y.py

good argv = cwd=/
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py
  ...
  --file
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py
  --target
  omlish/diag/tests/test_asts.py::test_check_equal

bad argv = cwd=/x
  /x/y.py

bad argv = cwd=/x
  /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py
  ...
  --file
  /Users/spinlock/src/wrmsr/omlish/x/llm/cli/main.py

TODO:
 - *** NOT JUST PYTEST - also just running, and running debugging
 - *** THIS GOES IN OMDEV lol ***
  - or..? pycharm already in core lol..
"""
import os.path
import sys


##


_DEFAULT_ENABLED = True
_DEFAULT_DEBUG = True


_HAS_RUN = False


def _run() -> None:
    global _HAS_RUN
    if _HAS_RUN:
        return
    _HAS_RUN = True

    #

    is_enabled = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_ENABLED', _DEFAULT_ENABLED))
    if not is_enabled:
        return

    #

    is_debug = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_DEBUG', _DEFAULT_DEBUG))

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


##


_DEFAULT_PTH_FILE_NAME = 'omlish-pycharm-runhack.pth'
_DEFAULT_PTH_MODULE_NAME = 'x.runhack'


def _build_pth_file_src(module_name: str) -> str:
    return (
        'import sys; '
        r"exec('\n'.join(["
        "'try:', "
        f"'  import {module_name}', "
        "'except ImportError:', " ""
        "'  pass', "
        "'else:', "
        f"'  {module_name}._run()'"
        "]))"
    )


def _install_pth_file(
        *,
        file_name: str | None = _DEFAULT_PTH_FILE_NAME,
        module_name: str | None = _DEFAULT_PTH_MODULE_NAME,
) -> None:
    import site

    if os.path.isfile(file := os.path.join(site.getsitepackages()[0], file_name)):
        return

    with open(file, 'w') as f:
        f.write(_build_pth_file_src(module_name))


if __name__ == '__main__':
    _install_pth_file()
