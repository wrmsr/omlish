"""
TODO:
 - custom tags
 - optionally install / upgrade pyenv itself
 - new vers dont need these custom mac opts, only run on old vers
"""
# ruff: noqa: UP007
import abc
import dataclasses as dc
import itertools
import os.path
import shutil
import typing as ta

from ...amalg.std.cached import cached_nullary
from ...amalg.std.check import check_not_none
from ...amalg.std.subprocesses import subprocess_check_call
from ...amalg.std.subprocesses import subprocess_check_output_str
from ...amalg.std.subprocesses import subprocess_try_output
from .base import Interp
from .base import InterpProvider
from .base import InterpVersion


##


class Pyenv:

    def __init__(
            self,
            *,
            root: ta.Optional[str] = None,
    ) -> None:
        if root is not None and not (isinstance(root, str) and root):
            raise ValueError(f'pyenv_root: {root!r}')

        super().__init__()

        self._root_kw = root

    @cached_nullary
    def root(self) -> ta.Optional[str]:
        if self._root_kw is not None:
            return self._root_kw

        if shutil.which('pyenv'):
            return subprocess_check_output_str('pyenv', 'root')

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @cached_nullary
    def exe(self) -> str:
        return os.path.join(check_not_none(self.root()), 'bin', 'pyenv')


##


@dc.dataclass(frozen=True)
class PyenvInstallOpts:
    opts: ta.Sequence[str] = ()
    conf_opts: ta.Sequence[str] = ()
    cflags: ta.Sequence[str] = ()
    ldflags: ta.Sequence[str] = ()
    env: ta.Mapping[str, str] = dc.field(default_factory=dict)

    def merge(self, *others: 'PyenvInstallOpts') -> 'PyenvInstallOpts':
        return PyenvInstallOpts(
            opts=list(itertools.chain.from_iterable(o.opts for o in [self, *others])),
            conf_opts=list(itertools.chain.from_iterable(o.conf_opts for o in [self, *others])),
            cflags=list(itertools.chain.from_iterable(o.cflags for o in [self, *others])),
            ldflags=list(itertools.chain.from_iterable(o.ldflags for o in [self, *others])),
            env=dict(itertools.chain.from_iterable(o.env.items() for o in [self, *others])),
        )


DEFAULT_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-s', '-v'])
DEBUG_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-g'])


#


class PyenvInstallOptsProvider(abc.ABC):
    @abc.abstractmethod
    def install_opts(self) -> PyenvInstallOpts:
        raise NotImplementedError


class LinuxPyenvInstallOpts(PyenvInstallOptsProvider):
    def install_opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts()


class MacPyenvInstallOpts(PyenvInstallOptsProvider):

    @cached_nullary
    def framework_opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts(conf_opts=['--enable-framework'])

    @cached_nullary
    def has_brew(self) -> bool:
        return shutil.which('brew') is not None

    BREW_DEPS: ta.Sequence[str] = [
        'openssl',
        'readline',
        'sqlite3',
        'zlib',
    ]

    @cached_nullary
    def brew_deps_opts(self) -> PyenvInstallOpts:
        cflags = []
        ldflags = []
        for dep in self.BREW_DEPS:
            dep_prefix = subprocess_check_output_str('brew', '--prefix', dep)
            cflags.append(f'-I{dep_prefix}/include')
            ldflags.append(f'-L{dep_prefix}/lib')
        return PyenvInstallOpts(
            cflags=cflags,
            ldflags=ldflags,
        )

    @cached_nullary
    def brew_tcl_opts(self) -> PyenvInstallOpts:
        if subprocess_try_output('brew', '--prefix', 'tcl-tk') is None:
            return PyenvInstallOpts()

        tcl_tk_prefix = subprocess_check_output_str('brew', '--prefix', 'tcl-tk')
        tcl_tk_ver_str = subprocess_check_output_str('brew', 'ls', '--versions', 'tcl-tk')
        tcl_tk_ver = '.'.join(tcl_tk_ver_str.split()[1].split('.')[:2])

        return PyenvInstallOpts(conf_opts=[
            f"--with-tcltk-includes='-I{tcl_tk_prefix}/include'",
            f"--with-tcltk-libs='-L{tcl_tk_prefix}/lib -ltcl{tcl_tk_ver} -ltk{tcl_tk_ver}'",
        ])

    @cached_nullary
    def brew_ssl_opts(self) -> PyenvInstallOpts:
        pkg_config_path = subprocess_check_output_str('brew', '--prefix', 'openssl')
        if 'PKG_CONFIG_PATH' in os.environ:
            pkg_config_path += ':' + os.environ['PKG_CONFIG_PATH']
        return PyenvInstallOpts(env={'PKG_CONFIG_PATH': pkg_config_path})

    def install_opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts().merge(
            self.framework_opts(),
            self.brew_deps_opts(),
            self.brew_tcl_opts(),
            self.brew_ssl_opts(),
        )


##


class PyenvVersionInstaller:

    def __init__(
            self,
            version: str,
            opts: PyenvInstallOpts,
            *,
            debug: bool = False,
            pyenv: Pyenv = Pyenv(),
    ) -> None:
        super().__init__()

        self._version = version
        self._opts = opts
        self._debug = debug
        self._pyenv = pyenv

    @cached_nullary
    def install_name(self) -> str:
        return self._version + ('-debug' if self._debug else '')

    @cached_nullary
    def install_dir(self) -> str:
        return str(os.path.join(check_not_none(self._pyenv.root()), 'versions', self.install_name()))

    @cached_nullary
    def build(self) -> str:
        env = dict(self._opts.env)
        for k, l in [
            ('CFLAGS', self._opts.cflags),
            ('LDFLAGS', self._opts.ldflags),
            ('PYTHON_CONFIGURE_OPTS', self._opts.conf_opts),
        ]:
            v = ' '.join(l)
            if k in os.environ:
                v += ' ' + os.environ[k]
            env[k] = v

        subprocess_check_call(self._pyenv.exe(), 'install', *self._opts.opts, self._version, env=env)

        exe = os.path.join(self.install_dir(), 'bin', 'python')
        if not os.path.isfile(exe):
            raise RuntimeError(f'Interpreter not found: {exe}')
        return exe


##


class PyenvInterpProvider(InterpProvider):

    def __init__(
            self,
            *args,
            pyenv: Pyenv = Pyenv(),
            **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._pyenv = pyenv

    @property
    def name(self) -> str:
        return 'pyenv'

    @cached_nullary
    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def get_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError
