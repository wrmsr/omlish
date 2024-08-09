#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omdev-amalg-output ../interp/interp.py
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
"""
# ruff: noqa: UP007
import argparse
import functools
import logging
import os.path
import shutil
import subprocess
import sys
import typing as ta


T = ta.TypeVar('T')


########################################
# ../../amalg/std/cached.py


class cached_nullary:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


########################################
# ../../amalg/std/check.py
# ruff: noqa: UP007


def check_not_none(v: ta.Optional[T]) -> T:
    if v is None:
        raise ValueError
    return v


def check_not(v: ta.Any) -> None:
    if v:
        raise ValueError(v)
    return v


########################################
# ../../amalg/std/logging.py
"""
TODO:
 - debug
"""


log = logging.getLogger(__name__)


def setup_standard_logging() -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')


########################################
# ../../amalg/std/runtime.py


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../amalg/std/subprocesses.py


def _mask_env_kwarg(kwargs):
    return {**kwargs, **({'env': '...'} if 'env' in kwargs else {})}


def subprocess_check_call(*args, stdout=sys.stderr, **kwargs):
    log.debug((args, _mask_env_kwarg(kwargs)))
    return subprocess.check_call(*args, stdout=stdout, **kwargs)  # type: ignore


def subprocess_check_output(*args, **kwargs):
    log.debug((args, _mask_env_kwarg(kwargs)))
    return subprocess.check_output(*args, **kwargs)


########################################
# ../subprocesses.py
# ruff: noqa: UP006 UP007


DEFAULT_CMD_TRY_EXCEPTIONS: ta.AbstractSet[ta.Type[Exception]] = frozenset([
    FileNotFoundError,
])


def cmd(
        cmd: ta.Union[str, ta.Sequence[str]],
        *,
        try_: ta.Union[bool, ta.Iterable[ta.Type[Exception]]] = False,
        env: ta.Optional[ta.Mapping[str, str]] = None,
        **kwargs,
) -> ta.Optional[str]:
    log.debug(cmd)
    if env:
        log.debug(env)

    env = {**os.environ, **(env or {})}

    es: tuple[ta.Type[Exception], ...] = (Exception,)
    if isinstance(try_, bool):
        if try_:
            es = tuple(DEFAULT_CMD_TRY_EXCEPTIONS)
    elif try_:
        es = tuple(try_)
        try_ = True

    try:
        buf = subprocess_check_output(cmd, env=env, **kwargs)
    except es:
        if try_:
            log.exception('cmd failed: %r', cmd)
            return None
        else:
            raise

    out = buf.decode('utf-8').strip()
    log.debug(out)
    return out


########################################
# ../resolvers/base.py
# ruff: noqa: UP007


class InterpResolver:

    def __init__(
            self,
            version: str,
            *,
            debug: bool = False,
            include_current_python: bool = False,
    ) -> None:
        if version is not None and not (isinstance(version, str) and version.strip()):
            raise ValueError(f'version: {version!r}')
        if not isinstance(debug, bool):
            raise TypeError(f'debug: {debug!r}')

        super().__init__()

        self._version = version.strip()
        self._debug = debug
        self._include_current_python = include_current_python

    def _get_python_ver(self, bin_path: str) -> ta.Optional[str]:
        s = cmd([bin_path, '--version'], try_=True)
        if s is None:
            return None
        ps = s.strip().splitlines()[0].split()
        if ps[0] != 'Python':
            return None
        return ps[1]

    def _resolve_which_python(self) -> ta.Optional[str]:
        wp = shutil.which('python3')
        if wp is None:
            return None
        wpv = self._get_python_ver(wp)
        if wpv == self._version:
            return wp
        return None

    def _resolve_current_python(self) -> ta.Optional[str]:
        if sys.version.split()[0] == self._version:
            return sys.executable
        return None

    def _resolvers(self) -> ta.Sequence[ta.Callable[[], ta.Optional[str]]]:
        return [
            self._resolve_which_python,
            *((self._resolve_current_python,) if self._include_current_python else ()),
        ]

    def resolve(self) -> ta.Optional[str]:
        for fn in self._resolvers():
            p = fn()
            if p is not None:
                return p
        return None


########################################
# ../resolvers/pyenv.py
# ruff: noqa: UP007


class PyenvInstallOpts(ta.NamedTuple):
    opts: ta.Sequence[str]
    conf_opts: ta.Sequence[str]
    cflags: ta.Sequence[str]
    ldflags: ta.Sequence[str]
    env: ta.Mapping[str, str]

    @classmethod
    def new(
            cls,
            *,
            opts: ta.Optional[ta.Sequence[str]] = None,
            conf_opts: ta.Optional[ta.Sequence[str]] = None,
            cflags: ta.Optional[ta.Sequence[str]] = None,
            ldflags: ta.Optional[ta.Sequence[str]] = None,
            env: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> 'PyenvInstallOpts':
        return cls(
            opts=opts if opts is not None else [],
            conf_opts=conf_opts if conf_opts is not None else [],
            cflags=cflags if cflags is not None else [],
            ldflags=ldflags if ldflags is not None else [],
            env=env if env is not None else {},
        )

    def combine(self, *others: 'PyenvInstallOpts') -> 'PyenvInstallOpts':
        opts = [*self.opts]
        conf_opts = [*self.conf_opts]
        cflags = [*self.cflags]
        ldflags = [*self.ldflags]
        env = {**self.env}

        for other in others:
            opts.extend(other.opts)
            conf_opts.extend(other.conf_opts)
            cflags.extend(other.cflags)
            ldflags.extend(other.ldflags)
            env.update(other.env)

        return PyenvInstallOpts(
            opts=opts,
            conf_opts=conf_opts,
            cflags=cflags,
            ldflags=ldflags,
            env=env,
        )


class PyenvInterpResolver(InterpResolver):

    def __init__(
            self,
            *args,
            pyenv_root: ta.Optional[str] = None,
            **kwargs,
    ) -> None:
        if pyenv_root is not None and not (isinstance(pyenv_root, str) and pyenv_root):
            raise ValueError(f'pyenv_root: {pyenv_root!r}')

        super().__init__(*args, **kwargs)

        self._pyenv_root_kw = pyenv_root

    @cached_nullary
    def _pyenv_root(self) -> ta.Optional[str]:
        if self._pyenv_root_kw is not None:
            return self._pyenv_root_kw

        if shutil.which('pyenv'):
            return cmd(['pyenv', 'root'])

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @cached_nullary
    def _pyenv_bin(self) -> str:
        return os.path.join(check_not_none(self._pyenv_root()), 'bin', 'pyenv')

    @cached_nullary
    def _pyenv_install_name(self) -> str:
        return self._version + ('-debug' if self._debug else '')

    @cached_nullary
    def _pyenv_install_path(self) -> str:
        return str(os.path.join(check_not_none(self._pyenv_root()), 'versions', self._pyenv_install_name()))

    @cached_nullary
    def _pyenv_basic_pio(self) -> PyenvInstallOpts:
        return PyenvInstallOpts.new(opts=['-s', '-v'])

    @cached_nullary
    def _pyenv_debug_pio(self) -> PyenvInstallOpts:
        if not self._debug:
            return PyenvInstallOpts.new()
        return PyenvInstallOpts.new(opts=['-g'])

    def _pyenv_pios(self) -> ta.Sequence[PyenvInstallOpts]:
        return [
            self._pyenv_basic_pio(),
            self._pyenv_debug_pio(),
        ]

    def _resolve_pyenv_existing_python(self) -> ta.Optional[str]:
        bin_path = os.path.join(self._pyenv_install_path(), 'bin', 'python')
        if os.path.isfile(bin_path):
            return bin_path
        return None

    def _resolve_pyenv_install_python(self) -> ta.Optional[str]:
        pio = PyenvInstallOpts.new().combine(*self._pyenv_pios())

        env = dict(pio.env)
        for k, l in [
            ('CFLAGS', pio.cflags),
            ('LDFLAGS', pio.ldflags),
            ('PYTHON_CONFIGURE_OPTS', pio.conf_opts),
        ]:
            v = ' '.join(l)
            if k in os.environ:
                v += ' ' + os.environ[k]
            env[k] = v

        cmd([self._pyenv_bin(), 'install', *pio.opts, self._version], env=env)

        bin_path = os.path.join(self._pyenv_install_path(), 'bin', 'python')
        if not os.path.isfile(bin_path):
            raise RuntimeError(f'Interpreter not found: {bin_path}')
        return bin_path

    def _resolvers(self) -> ta.Sequence[ta.Callable[[], ta.Optional[str]]]:
        return [
            *super()._resolvers(),
            self._resolve_pyenv_existing_python,
            self._resolve_pyenv_install_python,
        ]


########################################
# ../resolvers/linux.py


class LinuxInterpResolver(PyenvInterpResolver):

    def _pyenv_pios(self) -> ta.Sequence[PyenvInstallOpts]:
        return [
            *super()._pyenv_pios(),
        ]


########################################
# ../resolvers/mac.py


class MacInterpResolver(PyenvInterpResolver):

    @cached_nullary
    def _framework_pio(self) -> PyenvInstallOpts:
        return PyenvInstallOpts.new(conf_opts=['--enable-framework'])

    @cached_nullary
    def _has_brew(self) -> bool:
        return shutil.which('brew') is not None

    _PYENV_BREW_DEPS: ta.Sequence[str] = [
        'openssl',
        'readline',
        'sqlite3',
        'zlib',
    ]

    @cached_nullary
    def _brew_deps_pio(self) -> PyenvInstallOpts:
        cflags = []
        ldflags = []
        for dep in self._PYENV_BREW_DEPS:
            dep_prefix = cmd(['brew', '--prefix', dep])
            cflags.append(f'-I{dep_prefix}/include')
            ldflags.append(f'-L{dep_prefix}/lib')
        return PyenvInstallOpts.new(
            cflags=cflags,
            ldflags=ldflags,
        )

    @cached_nullary
    def _brew_tcl_pio(self) -> PyenvInstallOpts:
        pfx = cmd(['brew', '--prefix', 'tcl-tk'], try_=True)
        if pfx is None:
            return PyenvInstallOpts.new()

        tcl_tk_prefix = ta.cast(str, cmd(['brew', '--prefix', 'tcl-tk']))
        tcl_tk_ver_str = ta.cast(str, cmd(['brew', 'ls', '--versions', 'tcl-tk']))
        tcl_tk_ver = '.'.join(tcl_tk_ver_str.split()[1].split('.')[:2])

        return PyenvInstallOpts.new(conf_opts=[
            f"--with-tcltk-includes='-I{tcl_tk_prefix}/include'",
            f"--with-tcltk-libs='-L{tcl_tk_prefix}/lib -ltcl{tcl_tk_ver} -ltk{tcl_tk_ver}'",
        ])

    @cached_nullary
    def _brew_ssl_pio(self) -> PyenvInstallOpts:
        pkg_config_path = ta.cast(str, cmd(['brew', '--prefix', 'openssl']))
        if 'PKG_CONFIG_PATH' in os.environ:
            pkg_config_path += ':' + os.environ['PKG_CONFIG_PATH']
        return PyenvInstallOpts.new(env={'PKG_CONFIG_PATH': pkg_config_path})

    def _pyenv_pios(self) -> ta.Sequence[PyenvInstallOpts]:
        return [
            *super()._pyenv_pios(),
            self._framework_pio(),
            self._brew_deps_pio(),
            self._brew_tcl_pio(),
            self._brew_ssl_pio(),
        ]


########################################
# interp.py


def _resolve_cmd(args) -> None:
    if sys.platform == 'darwin':
        resolver_cls = MacInterpResolver
    elif sys.platform in ['linux', 'linux2']:
        resolver_cls = LinuxInterpResolver
    else:
        raise OSError(f'Unsupported platform: {sys.platform}')

    resolver = resolver_cls(
        args.version,
        debug=args.debug,
    )

    resolved = resolver.resolve()
    if resolved is None:
        raise RuntimeError(f'Failed to resolve python version: {args.version}')
    print(resolved)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('resolve')
    parser_resolve.add_argument('version')
    parser_resolve.add_argument('--debug', action='store_true')
    parser_resolve.set_defaults(func=_resolve_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_runtime_version()
    setup_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
