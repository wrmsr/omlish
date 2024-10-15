"""
What this does:
 -


Dimensions:
 - is in pycharm? PYCHARM_HOSTED
 - cwd IDE_PROJECT_ROOTS? should *always* be -
 - is in debugger? pydevd.py
  - --file? --module?
 - is test runner? --file _jb_pytest_runner.py
  - --target? --path?
 - is *not* in debugger?
  - file? argv = ['/x/y.py']
  - module? orig_argv = ['-m', module]

/snap/pycharm-professional/current/plugins/python-ce/helpers/pydev

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

==

debug_opts:
  arg:
    port
    vm_type
    client

    qt-support=.* (special)

    file (last one)

  bool:
    server
    DEBUG_RECORD_SOCKET_READS
    multiproc
    multiprocess
    save-signatures
    save-threading
    save-asyncio
    print-in-debugger-startup
    cmd-line
    module
    help
    DEBUG

test_opts:
  arg:
    path
    offset
    target

==

TODO:
 - *** NOT JUST PYTEST - also just running, and running debugging
 - *** THIS GOES IN OMDEV lol ***
  - or..? pycharm already in core lol..
"""
import os.path
import sys


##


class cached_nullary:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()

    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


def _attr_repr(obj, *atts):
    return f'{obj.__class__.__name__}({", ".join(f"{a}={getattr(obj, a)!r}" for a in atts)})'


##


class RunEnv:
    def __init__(
            self,
            *,
            argv=None,  # type: list[str] | None
            orig_argv=None,  # type: list[str] | None

            cwd=None,  # type: str | None

            library_roots=None,  # type: list[str] | None
            path=None,  # type: list[str] | None
            python_path=None,  # type: list[str] | None
            ide_project_roots=None,  # type: list[str] | None
            pycharm_hosted=None,  # type: bool | None

            sys_path=None,  # type: list[str] | None
    ) -> None:
        super().__init__()

        if argv is None:
            argv = sys.argv
        self._argv = list(argv)

        if orig_argv is None:
            orig_argv = sys.orig_argv
        self._orig_argv = list(orig_argv)

        if cwd is None:
            cwd = os.getcwd()
        self._cwd = cwd

        if library_roots is None:
            library_roots = os.environ.get('LIBRARY_ROOTS', '').split(os.pathsep)
        self._library_roots = list(library_roots)

        if path is None:
            path = os.environ.get('PATH', '').split(os.pathsep)
        self._path = list(path)

        if python_path is None:
            python_path = os.environ.get('PYTHONPATH', '').split(os.pathsep)
        self._python_path = list(python_path)

        if ide_project_roots is None:
            ide_project_roots = os.environ.get('IDE_PROJECT_ROOTS', '').split(os.pathsep)
        self._ide_project_roots = list(ide_project_roots)

        if pycharm_hosted is None:
            pycharm_hosted = 'PYCHARM_HOSTED' in os.environ
        self._pycharm_hosted = pycharm_hosted

        if sys_path is None:
            sys_path = list(sys.path)
        self._sys_path = sys_path

    _SPEC_ATTRS = (
        'argv',
        'orig_argv',

        'cwd',

        'library_roots',
        'path',
        'python_path',
        'ide_project_roots',
        'pycharm_hosted',

        'sys_path',
    )

    def as_dict(self):  # type: () -> dict[str, object]
        return {a: getattr(self, a) for a in self._SPEC_ATTRS}

    def __repr__(self) -> str:
        return _attr_repr(self, *self._SPEC_ATTRS)

    @property
    def argv(self):  # type: () -> list[str]
        return self._argv

    @property
    def orig_argv(self):  # type: () -> list[str]
        return self._orig_argv

    @property
    def cwd(self):  # type: () -> str
        return self._cwd

    @property
    def library_roots(self):  # type: () -> list[str]
        return self._library_roots

    @property
    def path(self):  # type: () -> list[str]
        return self._path

    @property
    def python_path(self):  # type: () -> list[str]
        return self._python_path

    @property
    def ide_project_roots(self):  # type: () -> list[str]
        return self._ide_project_roots

    @property
    def pycharm_hosted(self):  # type: () -> bool
        return self._pycharm_hosted

    @property
    def sys_path(self):  # type: () -> list[str]
        return self._sys_path


##


class ParamDef:
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return _attr_repr(self, 'name')


class BoolParamDef(ParamDef):
    pass


class StrParamDef(ParamDef):
    pass


class FinalParamDef(ParamDef):
    pass


class ParamDefs:
    def __init__(
            self,
            params,  # type: list[ParamDef]
    ) -> None:
        super().__init__()

        self._params = params
        self._params_by_name = {}  # type: dict[str, ParamDef]
        for p in params:
            if p.name in self._params_by_name:
                raise KeyError(p.name)
            self._params_by_name[p.name] = p

    @property
    def params(self):  # type: () -> list[ParamDef]
        return self._params

    @property
    def params_by_name(self):  # type: () -> dict[str, ParamDef]
        return self._params_by_name

    def __repr__(self) -> str:
        return _attr_repr(self, 'params')


#


class ParsedArg:
    def __init__(
            self,
            param: ParamDef,
            arg=None,  # type: str | None
    ) -> None:
        super().__init__()

        self._param = param
        self._arg = arg

    @property
    def param(self) -> ParamDef:
        return self._param

    @property
    def arg(self):  # type: () -> str | None
        return self._arg

    def __repr__(self) -> str:
        return _attr_repr(self, 'param', 'arg')


class ParsedArgs:
    def __init__(
            self,
            args,  # list[ParsedArg]
    ) -> None:
        super().__init__()

        self._args = args

    @property
    def args(self):  # type: () -> list[ParsedArg]
        return self._args

    def __repr__(self) -> str:
        return _attr_repr(self, 'args')


#


def parse_args(
        params: ParamDefs,
        args,  # type: list[str]
) -> ParsedArgs:
    l = []  # type: list[ParsedArg]
    i = 0
    while i < len(args):
        raise NotImplementedError
    return ParsedArgs(*l)


##


class Target:
    pass


class DebuggerTarget(Target):
    def __init__(self, target: Target) -> None:
        super().__init__()
        self._target = target

    @property
    def target(self) -> Target:
        return self._target

    def __repr__(self) -> str:
        return _attr_repr(self, 'target')


class FileTarget(Target):
    def __init__(self, file: str) -> None:
        super().__init__()
        self._file = file

    @property
    def file(self) -> str:
        return self._file

    def __repr__(self) -> str:
        return _attr_repr(self, 'file')


class ModuleTarget(Target):
    def __init__(self, module: str) -> None:
        super().__init__()
        self._module = module

    @property
    def module(self) -> str:
        return self._module

    def __repr__(self) -> str:
        return _attr_repr(self, 'module')


class TestTarget(Target):
    def __init__(
            self,
            targets=None,  # type: list[str] | None
            paths=None,  # type: list[str] | None
    ) -> None:
        super().__init__()
        self._targets = list(targets or [])
        self._paths = list(paths or [])

    @property
    def targets(self):  # type: () -> list[str]
        return self._targets

    @property
    def paths(self):  # type: () -> list[str]
        return self._paths

    def __repr__(self) -> str:
        return _attr_repr(self, 'targets', 'paths')


##


def _is_pycharm_dir(s: str) -> bool:
    s = os.path.abspath(s)
    if not os.path.isdir(s):
        return False

    ps = s.split(os.sep)

    if sys.platform == 'darwin':
        # /Applications/PyCharm.app/Contents/bin/pycharm.vmoptions
        return ps[-1] == 'Contents' and os.path.isfile(os.path.join(s, 'bin', 'pycharm.vmoptions'))

    if sys.platform == 'linux':
        # /snap/pycharm-professional/current/bin/pycharm64.vmoptions
        return os.path.isfile(os.path.join(s, 'bin', 'pycharm64.vmoptions'))

    return False


def _is_pycharm_file(given: str, expected: str) -> bool:
    dgs = os.path.abspath(given).split(os.sep)
    des = expected.split(os.sep)
    return (
            len(des) < len(dgs) and
            dgs[-len(des):] == des and
            _is_pycharm_dir(os.sep.join(dgs[:-len(des)]))
    )


class RunSpec:
    def __init__(self, env: RunEnv) -> None:
        super().__init__()
        self._env = env

    def _get_target(
            self,
            argv,  # type: list[str]
    ) -> Target:
        arg0 = argv[0]

        if _is_pycharm_file(arg0, 'plugins/python-ce/helpers/pydev/pydevd.py '):
            raise NotImplementedError

        elif _is_pycharm_file(arg0, 'plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py'):
            raise NotImplementedError

        else:
            raise NotImplementedError

    @cached_nullary
    def target(self) -> Target:
        return self._get_target(self._env.argv)


##


_DEFAULT_ENABLED = False
_DEFAULT_DEBUG = True


_HAS_RUN = False


def _run() -> None:
    global _HAS_RUN
    if _HAS_RUN:
        return
    _HAS_RUN = True

    #

    is_debug = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_DEBUG', _DEFAULT_DEBUG))

    def debug(arg):
        if not is_debug:
            return

        if isinstance(arg, str):
            s = arg
        else:
            import pprint

            s = pprint.pformat(arg)

        print(s, file=sys.stderr)

    #

    env = RunEnv()
    debug(env.as_dict())

    # breakpoint()

    #

    is_enabled = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_ENABLED', _DEFAULT_ENABLED))
    if not is_enabled:
        return

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
