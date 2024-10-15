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

TODO:
 - *** NOT JUST PYTEST - also just running, and running debugging
 - *** THIS GOES IN OMDEV lol ***
  - or..? pycharm already in core lol..
"""
import os.path
import sys


##


class _cached_nullary:  # noqa
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


class Param:
    def __init__(
            self,
            name: str,
            cls,  # type: type[Arg]
    ) -> None:
        super().__init__()

        if not issubclass(cls, Arg):
            raise TypeError(cls)

        self._name = name
        self._cls = cls

    @property
    def name(self) -> str:
        return self._name

    @property
    def cls(self):  # type: () -> type[Arg]
        return self._cls

    def __repr__(self) -> str:
        return _attr_repr(self, 'name', 'cls')


class Params:
    def __init__(
            self,
            params,  # type: list[Param]
    ) -> None:
        super().__init__()

        self._params = params
        self._params_by_name = {}  # type: dict[str, Param]

        for p in params:
            if p.name in self._params_by_name:
                raise KeyError(p.name)
            self._params_by_name[p.name] = p

    @property
    def params(self):  # type: () -> list[Param]
        return self._params

    @property
    def params_by_name(self):  # type: () -> dict[str, Param]
        return self._params_by_name

    def __repr__(self) -> str:
        return _attr_repr(self, 'params')


#


class Arg:
    def __init__(self, param: Param) -> None:
        super().__init__()

        if not isinstance(param, Param):
            raise TypeError(param)

        self._param = param

    @property
    def param(self) -> Param:
        return self._param


class BoolArg(Arg):
    def __repr__(self) -> str:
        return _attr_repr(self, 'param')


class StrArg(Arg):
    def __init__(self, param: Param, value: str) -> None:
        super().__init__(param)

        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return _attr_repr(self, 'param', 'value')


class OptStrArg(Arg):
    def __init__(
            self,
            param: Param,
            value,  # type: str | None
    ) -> None:
        super().__init__(param)

        self._value = value

    @property
    def value(self):  # type: () -> str | None
        return self._value

    def __repr__(self) -> str:
        return _attr_repr(self, 'param', 'value')


class FinalArg(Arg):
    def __init__(
            self,
            param: Param,
            values,  # type: list[str]
    ) -> None:
        super().__init__(param)

        self._values = values

    @property
    def values(self):  # type: () -> list[str]
        return self._values

    def __repr__(self) -> str:
        return _attr_repr(self, 'param', 'values')


class Args:
    def __init__(
            self,
            params: Params,
            args,  # type: list[Arg]
    ) -> None:
        super().__init__()

        self._params = params
        self._args = args

        self._arg_lists_by_name = {}  # type: dict[str, list[Arg]]
        for a in args:
            self._arg_lists_by_name.setdefault(a.param.name, []).append(a)

    @property
    def params(self):  # type: () -> Params
        return self._params

    @property
    def args(self):  # type: () -> list[Arg]
        return self._args

    @property
    def arg_lists_by_name(self):  # type: () -> dict[str, list[Arg]]
        return self._arg_lists_by_name

    def without(self, *names: str) -> 'Args':
        return Args(
            self._params,
            [a for a in self._args if a.param.name not in names],
        )

    def __repr__(self) -> str:
        return _attr_repr(self, 'args')


#


class ArgParseError(Exception):
    pass


def parse_args(
        params: Params,
        argv,  # type: list[str]
) -> Args:
    l = []  # type: list[Arg]

    it = iter(argv)
    for s in it:
        if not s.startswith('--'):
            raise ArgParseError(s, argv)
        s = s[2:]

        if '=' in s:
            k, _, v = s.partition('=')
        else:
            k, v = s, None

        p = params.params_by_name[k]

        if p.cls is BoolArg:
            if v is not None:
                raise ArgParseError(s, argv)
            l.append(BoolArg(p))

        elif p.cls is StrArg:
            if v is None:
                try:
                    v = next(it)
                except StopIteration:
                    raise ArgParseError(s, argv)
            l.append(StrArg(p, v))

        elif p.cls is OptStrArg:
            l.append(OptStrArg(p, v))

        elif p.cls is FinalArg:
            vs = []  # type: list[str]
            if v is not None:
                vs.append(v)
            vs.extend(it)
            l.append(FinalArg(p, vs))

        else:
            raise TypeError(p.cls)

    return Args(params, l)


##


class Target:
    pass


class UserTarget(Target):
    def __init__(
            self,
            argv,  # type: list[str]
    ) -> None:
        super().__init__()

        self._argv = argv

    @property
    def argv(self):  # type: () -> list[str]
        return self._argv


class FileTarget(UserTarget):
    def __init__(
            self,
            file: str,
            argv,  # type: list[str]
    ) -> None:
        super().__init__(argv)

        self._file = file

    @property
    def file(self) -> str:
        return self._file

    def __repr__(self) -> str:
        return _attr_repr(self, 'file', 'argv')


class ModuleTarget(Target):
    def __init__(
            self,
            module: str,
            argv,  # type: list[str]
    ) -> None:
        super().__init__(argv)

        self._module = module

    @property
    def module(self) -> str:
        return self._module

    def __repr__(self) -> str:
        return _attr_repr(self, 'module', 'argv')


class PycharmTarget(Target):
    def __init__(self, args: Args) -> None:
        super().__init__()

        if not isinstance(args, Args):
            raise TypeError(args)
        self._args = args

    @property
    def args(self) -> Args:
        return self._args


class DebuggerTarget(PycharmTarget):
    def __init__(self, args: Args, target: Target) -> None:
        super().__init__(args)

        if isinstance(target, DebuggerTarget):
            raise TypeError(target)
        self._target = target

    @property
    def target(self) -> Target:
        return self._target

    def __repr__(self) -> str:
        return _attr_repr(self, 'args', 'target')


class TestRunnerTarget(PycharmTarget):
    def __init__(
            self,
            args: Args,
            *,
            paths,  # type: list[str] | None
            targets,  # type: list[str] | None
    ) -> None:
        super().__init__(args)

        self._paths = paths
        self._targets = targets

    @property
    def paths(self):  # type: () -> list[str] | None
        return self._paths

    @property
    def targets(self):  # type: () -> list[str] | None
        return self._targets

    def __repr__(self) -> str:
        return _attr_repr(self, 'args', 'paths', 'targets')


#


def is_pycharm_dir(s: str) -> bool:
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


def is_pycharm_file(given: str, expected: str) -> bool:
    dgs = os.path.abspath(given).split(os.sep)
    des = expected.split(os.sep)
    return (
            len(des) < len(dgs) and
            dgs[-len(des):] == des and
            is_pycharm_dir(os.sep.join(dgs[:-len(des)]))
    )


class PycharmEntrypoint:
    def __init__(self, file: str, params: Params) -> None:
        super().__init__()

        self._file = file
        self._params = params

    @property
    def file(self) -> str:
        return self._file

    @property
    def params(self) -> Params:
        return self._params

    def __repr__(self) -> str:
        return _attr_repr(self, 'file', 'params')


DEBUGGER_ENTRYPOINT = PycharmEntrypoint(
    'plugins/python-ce/helpers/pydev/pydevd.py',
    Params([
        Param('port', StrArg),
        Param('vm_type', StrArg),
        Param('client', StrArg),

        Param('qt-support', OptStrArg),

        Param('file', FinalArg),

        Param('server', BoolArg),
        Param('DEBUG_RECORD_SOCKET_READS', BoolArg),
        Param('multiproc', BoolArg),
        Param('multiprocess', BoolArg),
        Param('save-signatures', BoolArg),
        Param('save-threading', BoolArg),
        Param('save-asyncio', BoolArg),
        Param('print-in-debugger-startup', BoolArg),
        Param('cmd-line', BoolArg),
        Param('module', BoolArg),
        Param('help', BoolArg),
        Param('DEBUG', BoolArg),
    ]),
)


TEST_RUNNER_ENTRYPOINT = PycharmEntrypoint(
    'plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py',
    Params([
        Param('path', StrArg),
        Param('offset', StrArg),
        Param('target', StrArg),
    ]),
)


def try_parse_entrypoint_args(ep, argv):  # type: (PycharmEntrypoint, list[str]) -> Args | None
    if not argv:
        return None

    if not is_pycharm_file(argv[0], ep.file):
        return None

    return parse_args(ep.params, argv[1:])


def parse_args_target(
        argv,  # type: list[str]
) -> Target:
    if not argv:
        raise Exception

    elif (pa := try_parse_entrypoint_args(DEBUGGER_ENTRYPOINT, argv)) is not None:
        fa = pa.args[-1]
        if not isinstance(fa, FinalArg) or fa.param.name != 'file':
            raise TypeError(fa)

        st = parse_args_target(fa.values)
        return DebuggerTarget(pa.without('file'), st)

    elif (pa := try_parse_entrypoint_args(TEST_RUNNER_ENTRYPOINT, argv)) is not None:
        return TestRunnerTarget(pa)

    elif argv[0] == '-m':
        return ModuleTarget(argv[1], argv[1:])

    else:
        return FileTarget(argv[0], argv[1:])


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
