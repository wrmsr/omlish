"""
See:
 - https://github.com/JetBrains/intellij-community/blob/6400f70dde6f743e39a257a5a78cc51b644c835e/python/helpers/pycharm/_jb_pytest_runner.py
 - https://github.com/JetBrains/intellij-community/blob/5a4e584aa59767f2e7cf4bd377adfaaf7503984b/python/helpers/pycharm/_jb_runner_tools.py
 - https://github.com/JetBrains/intellij-community/blob/5a4e584aa59767f2e7cf4bd377adfaaf7503984b/python/helpers/pydev/_pydevd_bundle/pydevd_command_line_handling.py
"""  # noqa
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


class AsDict:
    def as_dict(self):  # type: () -> dict[str, object]
        raise TypeError


class AsJson:
    def as_json(self):  # type: () -> dict[str, object]
        raise TypeError


##


class RunEnv(AsJson):
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

        def get_env_path_list(k):  # type: (str) -> list[str]
            v = os.environ.get(k, '')
            if v:
                return v.split(os.pathsep)
            else:
                return []

        if library_roots is None:
            library_roots = get_env_path_list('LIBRARY_ROOTS')
        self._library_roots = list(library_roots)

        if path is None:
            path = get_env_path_list('PATH')
        self._path = list(path)

        if python_path is None:
            python_path = get_env_path_list('PYTHONPATH')
        self._python_path = list(python_path)

        if ide_project_roots is None:
            ide_project_roots = get_env_path_list('IDE_PROJECT_ROOTS')
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

    def as_json(self):  # type: () -> dict[str, object]
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


class Arg(AsJson):
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

    def as_json(self):  # type: () -> dict[str, object]
        return {self._param.name: True}


class StrArg(Arg):
    def __init__(self, param: Param, value: str) -> None:
        super().__init__(param)

        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return _attr_repr(self, 'param', 'value')

    def as_json(self):  # type: () -> dict[str, object]
        return {self._param.name: self._value}


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

    def as_json(self):  # type: () -> dict[str, object]
        return {self._param.name: self._value}


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

    def as_json(self):  # type: () -> dict[str, object]
        return {self._param.name: self._values}


class Args(AsJson):
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

    def as_json(self):  # type: () -> dict[str, object]
        return {k: v for a in self._args for k, v in a.as_json().items()}


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
        if len(s) > 1 and s.startswith('--'):
            s = s[2:]
        else:
            raise ArgParseError(s, argv)

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
                    raise ArgParseError(s, argv)  # noqa
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


#


def render_arg(arg):  # type: (Arg) -> list[str]
    if isinstance(arg, BoolArg):
        return [f'--{arg.param.name}']

    elif isinstance(arg, StrArg):
        return [f'--{arg.param.name}', arg.value]

    elif isinstance(arg, OptStrArg):
        if arg.value is None:
            return [f'--{arg.param.name}']
        else:
            return [f'--{arg.param.name}={arg.value}']

    elif isinstance(arg, FinalArg):
        return [f'--{arg.param.name}', *arg.values]  # noqa

    else:
        raise TypeError(arg)


def render_args(args):  # type: (list[Arg]) -> list[str]
    return [ra for a in args for ra in render_arg(a)]


##


class Target(AsDict, AsJson):
    pass


#


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

    def as_dict(self):  # type: () -> dict[str, object]
        return {
            'file': self._file,
            'argv': self._argv,
        }

    def as_json(self):  # type: () -> dict[str, object]
        return self.as_dict()


class ModuleTarget(UserTarget):
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

    def as_dict(self):  # type: () -> dict[str, object]
        return {
            'module': self._module,
            'argv': self._argv,
        }

    def as_json(self):  # type: () -> dict[str, object]
        return self.as_dict()


#


class PycharmTarget(Target):
    def __init__(self, file: str, args: Args) -> None:
        super().__init__()

        if not isinstance(file, str):
            raise TypeError(file)
        self._file = file

        if not isinstance(args, Args):
            raise TypeError(args)
        self._args = args

    @property
    def file(self) -> str:
        return self._file

    @property
    def args(self) -> Args:
        return self._args


class DebuggerTarget(PycharmTarget):
    def __init__(self, file: str, args: Args, target: Target) -> None:
        super().__init__(file, args)

        if isinstance(target, DebuggerTarget):
            raise TypeError(target)
        self._target = target

    @property
    def target(self) -> Target:
        return self._target

    def __repr__(self) -> str:
        return _attr_repr(self, 'file', 'args', 'target')

    def as_dict(self):  # type: () -> dict[str, object]
        return {
            'file': self._file,
            'args': self._args,
            'target': self._target,
        }

    def as_json(self):  # type: () -> dict[str, object]
        return {
            'debugger': self._file,
            'args': self._args.as_json(),
            'target': self._target.as_json(),
        }


class Test(AsJson):
    def __init__(self, s: str) -> None:
        super().__init__()

        if not isinstance(s, str):
            raise TypeError(s)

        self._s = s

    @property
    def s(self) -> str:
        return self._s

    def __repr__(self) -> str:
        return _attr_repr(self, 's')


class PathTest(Test):
    def as_json(self):  # type: () -> dict[str, object]
        return {'path': self._s}


class TargetTest(Test):
    def as_json(self):  # type: () -> dict[str, object]
        return {'target': self._s}


class TestRunnerTarget(PycharmTarget):
    def __init__(
            self,
            file: str,
            args: Args,
            tests,  # type: list[Test]
    ) -> None:
        super().__init__(file, args)

        self._tests = tests

    @property
    def tests(self):  # type: () -> list[Test]
        return self._tests

    def __repr__(self) -> str:
        return _attr_repr(self, 'file', 'args', 'tests')

    def as_dict(self):  # type: () -> dict[str, object]
        return {
            'file': self._file,
            'args': self._args,
            'tests': self._tests,
        }

    def as_json(self):  # type: () -> dict[str, object]
        return {
            'test_runner': self._file,
            'args': self._args.as_json(),
            'tests': [t.as_json() for t in self._tests],
        }


#


def is_pycharm_dir(s: str) -> bool:
    s = os.path.abspath(s)
    if not os.path.isdir(s):
        return False

    ps = s.split(os.sep)

    plat = getattr(sys, 'platform')
    if plat == 'darwin':
        # /Applications/PyCharm.app/Contents/bin/pycharm.vmoptions
        return ps[-1] == 'Contents' and os.path.isfile(os.path.join(s, 'bin', 'pycharm.vmoptions'))

    if plat == 'linux':
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

        Param('', FinalArg),
    ]),
)


def try_parse_entrypoint_args(ep, argv):  # type: (PycharmEntrypoint, list[str]) -> Args | None
    if not argv:
        return None

    if not is_pycharm_file(argv[0], ep.file):
        return None

    return parse_args(ep.params, argv[1:])


def _make_module_target(
        argv,  # type: list[str]
) -> ModuleTarget:
    if argv[0] == '-m':
        return ModuleTarget(argv[1], argv[2:])
    elif argv[0].startswith('-m'):
        return ModuleTarget(argv[0][2:], argv[1:])
    else:
        raise ArgParseError(argv)


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

        if isinstance(st, TestRunnerTarget):
            if 'module' in pa.arg_lists_by_name:
                raise ArgParseError(argv)

        elif isinstance(st, FileTarget):
            if 'module' in pa.arg_lists_by_name:
                st = ModuleTarget(st.file, st.argv)

        else:
            raise TypeError(st)

        return DebuggerTarget(
            argv[0],
            pa.without('file', 'module'),
            st,
        )

    elif (pa := try_parse_entrypoint_args(TEST_RUNNER_ENTRYPOINT, argv)) is not None:
        ts = []  # type: list[Test]
        for a in pa.args:
            if isinstance(a, StrArg):
                if a.param.name == 'path':
                    ts.append(PathTest(a.value))
                elif a.param.name == 'target':
                    ts.append(TargetTest(a.value))

        return TestRunnerTarget(
            argv[0],
            pa.without('path', 'target'),
            ts,
        )

    elif argv[0].startswith('-m'):
        return _make_module_target(argv)

    else:
        return FileTarget(argv[0], argv[1:])


#


def render_target_args(tgt):  # type: (Target) -> list[str]
    if isinstance(tgt, FileTarget):
        return [tgt.file, *tgt.argv]

    elif isinstance(tgt, ModuleTarget):
        return ['-m', *tgt.argv]

    elif isinstance(tgt, DebuggerTarget):
        l = [
            tgt.file,
            *render_args(tgt.args.args),
        ]
        dt = tgt.target
        if isinstance(dt, ModuleTarget):
            l.extend(['--module', '--file', dt.module, *dt.argv])
        else:
            l.extend(['--file', *render_target_args(dt)])
        return l

    elif isinstance(tgt, TestRunnerTarget):
        l = [
            tgt.file,
        ]
        for t in tgt.tests:
            if isinstance(t, PathTest):
                l.extend(['--path', t.s])
            elif isinstance(t, TargetTest):
                l.extend(['--target', t.s])
            else:
                raise TypeError(t)
        l.extend(render_args(tgt.args.args))
        return l

    else:
        raise TypeError(tgt)


##


class Exec(AsDict, AsJson):
    def __init__(
            self,
            exe: str,
            exe_args,  # type: list[str]
            target: Target,
    ) -> None:
        super().__init__()

        self._exe = exe
        self._exe_args = exe_args
        self._target = target

    @property
    def exe(self) -> str:
        return self._exe

    @property
    def exe_args(self):  # type: () -> list[str]
        return self._exe_args

    @property
    def target(self) -> Target:
        return self._target

    def __repr__(self) -> str:
        return _attr_repr(self, 'exe', 'exe_args', 'target')

    def as_dict(self):  # type: () -> dict[str, object]
        return {
            'exe': self._exe,
            'exe_args': self._exe_args,
            'target': self._target,
        }

    def as_json(self):  # type: () -> dict[str, object]
        return {
            'exe': self._exe,
            'exe_args': self._exe_args,
            'target': self._target.as_json(),
        }


def parse_exec(
        exe_argv,  # type: list[str]
) -> Exec:
    it = iter(exe_argv)
    exe = next(it)

    exe_args = []  # type: list[str]

    for a in it:
        if a.startswith('-X'):
            if a == '-X':
                exe_args.extend([a, next(it)])
            else:
                exe_args.append(a)
        else:
            break
    else:
        raise Exception(exe_argv)

    argv = [a, *it]

    if argv[0].startswith('-m'):
        tgt = _make_module_target(argv)  # type: Target

    else:
        tgt = parse_args_target(argv)

    return Exec(
        exe,
        exe_args,
        tgt,
    )


def render_exec_args(exe):  # type: (Exec) -> list[str]
    l = [
        exe.exe,
        *exe.exe_args,
    ]

    et = exe.target

    if isinstance(et, ModuleTarget):
        l.extend(['-m', et.module, *et.argv])

    else:
        l.extend(render_target_args(et))

    return l


##


class ExecDecision(AsJson):
    def __init__(
            self,
            target: Target,
            *,
            cwd=None,  # type: str | None
            python_path=None,  # type: list[str] | None
            sys_path=None,  # type: list[str] | None
            os_exec: bool = False,
    ) -> None:
        super().__init__()

        if not isinstance(target, Target):
            raise TypeError(Target)
        self._target = target

        self._cwd = cwd
        self._python_path = python_path
        self._sys_path = sys_path
        self._os_exec = os_exec

    @property
    def target(self) -> Target:
        return self._target

    @property
    def cwd(self):  # type: () -> str | None
        return self._cwd

    @property
    def python_path(self):  # type: () -> list[str] | None
        return self._python_path

    @property
    def sys_path(self):  # type: () -> list[str] | None
        return self._sys_path

    @property
    def os_exec(self) -> bool:
        return self._os_exec

    def __repr__(self) -> str:
        return _attr_repr(
            self,
            'target',
            'cwd',
            'python_path',
            'sys_path',
            'os_exec',
        )

    def as_json(self):  # type: () -> dict[str, object]
        return {
            'target': self._target.as_json(),
            'cwd': self._cwd,
            'python_path': self._python_path,
            'sys_path': self._sys_path,
            'os_exec': self._os_exec,
        }


class ExecDecider:
    def __init__(
            self,
            env: RunEnv,
            exe: Exec,
            root_dir: str,
            *,
            debug_fn=None,
    ) -> None:
        super().__init__()

        self._env = env
        self._exe = exe
        self._root_dir = root_dir

        self._debug_fn = debug_fn

    def _debug(self, arg):
        if self._debug_fn is not None:
            self._debug_fn(arg)

    def _decide_file_target(self, tgt):  # type: (Target) -> ExecDecision | None
        if not isinstance(tgt, FileTarget):
            return None

        new_file = os.path.abspath(tgt.file)

        return ExecDecision(
            FileTarget(**{  # type: ignore
                **tgt.as_dict(),
                'file': new_file,
            }),
            cwd=self._root_dir,
        )

    def _decide_module_target_not_in_root(self, tgt):  # type: (Target) -> ExecDecision | None
        if not (isinstance(tgt, ModuleTarget) and self._env.cwd != self._root_dir):
            return None

        rel_path = os.path.relpath(self._env.cwd, self._root_dir)
        new_mod = '.'.join([rel_path.replace(os.sep, '.'), tgt.module])  # noqa

        return ExecDecision(
            ModuleTarget(**{  # type: ignore
                **tgt.as_dict(),
                'module': new_mod,
            }),
            cwd=self._root_dir,
            os_exec=True,
        )

    def _decide_debugger_file_target(self, tgt):  # type: (Target) -> ExecDecision | None
        if not isinstance(tgt, DebuggerTarget):
            return None

        dt = tgt.target
        if not (isinstance(dt, FileTarget) and dt.file.endswith('.py')):
            return None

        af = os.path.abspath(dt.file)
        rp = os.path.relpath(af, self._root_dir).split(os.path.sep)
        mod = '.'.join([*rp[:-1], rp[-1][:-3]])
        new_dt = ModuleTarget(
            mod,
            dt.argv,
        )

        return ExecDecision(
            DebuggerTarget(**{  # type: ignore
                **tgt.as_dict(),
                'target': new_dt,
            }),
            cwd=self._root_dir,
        )

    def _decide_debugger_module_target_not_in_root(self, tgt):  # type: (Target) -> ExecDecision | None
        if not (isinstance(tgt, DebuggerTarget) and self._env.cwd != self._root_dir):
            return None

        dt = tgt.target
        if not isinstance(dt, ModuleTarget):
            return None

        rp = os.path.relpath(self._env.cwd, self._root_dir).split(os.path.sep)
        mod = '.'.join([*rp, dt.module])
        new_dt = ModuleTarget(
            mod,
            dt.argv,
        )

        return ExecDecision(
            DebuggerTarget(**{  # type: ignore
                **tgt.as_dict(),
                'target': new_dt,
            }),
            cwd=self._root_dir,
        )

    def decide(self, tgt):  # type: (Target) -> ExecDecision | None
        for fn in [
            self._decide_file_target,
            self._decide_module_target_not_in_root,
            self._decide_debugger_file_target,
            self._decide_debugger_module_target_not_in_root,
        ]:
            if (ne := fn(tgt)) is not None:
                return ne

        return None


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

    is_debug = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_DEBUG', _DEFAULT_DEBUG))

    def debug(arg):
        if not is_debug:
            return

        if isinstance(arg, str):
            s = arg
        else:
            import pprint

            s = pprint.pformat(arg, sort_dicts=False)

        print(s, file=sys.stderr)

    #

    # breakpoint()

    env = RunEnv()
    debug(env.as_json())

    #

    is_enabled = bool(os.environ.get('OMLISH_PYCHARM_RUNHACK_ENABLED', _DEFAULT_ENABLED))
    if not is_enabled:
        return

    #

    if not env.pycharm_hosted:
        return

    if env.ide_project_roots:
        root_dir = os.path.abspath(env.ide_project_roots[0])
    else:
        root_dir = os.path.abspath(env.sys_path[0])
    debug(f'{root_dir=}')
    if not os.path.isfile(os.path.join(root_dir, 'pyproject.toml')):
        return

    exe = parse_exec(env.orig_argv)
    debug(exe.as_json())

    #

    decider = ExecDecider(
        env,
        exe,
        root_dir,
        debug_fn=debug,
    )

    dec = decider.decide(exe.target)
    if dec is None:
        return

    #

    debug(dec.as_json())

    if dec.cwd is not None:
        os.chdir(dec.cwd)

    if dec.python_path is not None:
        os.environ['PYTHONPATH'] = os.pathsep.join(dec.python_path)

    if dec.sys_path is not None:
        sys.path = dec.sys_path

    if dec.os_exec:
        new_exe = Exec(**{  # type: ignore
            **exe.as_dict(),
            'target': dec.target,
        })

        reexec_argv = render_exec_args(new_exe)
        debug(f'{reexec_argv=}')

        os.execvp(reexec_argv[0], reexec_argv)

    else:
        new_argv = render_target_args(dec.target)
        debug(new_argv)

        sys.argv = new_argv


##


_DEFAULT_PTH_FILE_NAME = f'{"-".join(__package__.split("."))}-runhack.pth'
_DEFAULT_PTH_MODULE_NAME = __package__ + '.runhack'


def _build_pth_file_src(module_name: str) -> str:
    return (
        'import sys; '
        r"exec('\n'.join(["
        "'try:', "
        f"'  import {module_name}', "
        "'except ImportError:', "
        "'  pass', "
        "'else:', "
        f"'  {module_name}._run()'"
        "]))"
    )


def _install_pth_file(
        *,
        file_name: str = _DEFAULT_PTH_FILE_NAME,
        module_name: str = _DEFAULT_PTH_MODULE_NAME,
        dry_run: bool = False,
) -> None:
    import site

    if os.path.isfile(file := os.path.join(site.getsitepackages()[0], file_name)):
        return

    src = _build_pth_file_src(module_name)

    if dry_run:
        print(file)
        print()
        print(src)

    else:
        with open(file, 'w') as f:
            f.write(src)


if __name__ == '__main__':
    def _main() -> None:
        import argparse

        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers()

        def install_cmd(args):
            _install_pth_file(dry_run=args.dry_run)

        parser_install = subparsers.add_parser('install')
        parser_install.add_argument('--dry-run', action='store_true')
        parser_install.set_defaults(func=install_cmd)

        args = parser.parse_args()
        if not getattr(args, 'func', None):
            parser.print_help()
        else:
            args.func(args)

    _main()
