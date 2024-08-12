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
from ...amalg.std.subprocesses import subprocess_check_output
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
        super().__init__()

        self._root_kw = root

    @cached_nullary
    def root(self) -> ta.Optional[str]:
        if self._root_kw is not None:
            return self._root_kw

        if shutil.which('pyenv'):
            return subprocess_check_output('pyenv', 'root').decode()

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @cached_nullary
    def exe(self) -> str:
        return os.path.join(check_not_none(self.root()), 'bin', 'pyenv')


##


@dc.dataclass(frozen=True)
class PyenvInstallOpts(ta.NamedTuple):
    opts: ta.Sequence[str] = ()
    conf_opts: ta.Sequence[str] = ()
    cflags: ta.Sequence[str] = ()
    ldflags: ta.Sequence[str] = ()
    env: ta.Mapping[str, str] = dc.field(default_factory=dict)

    def merge(self, *others: 'PyenvInstallOpts') -> 'PyenvInstallOpts':
        return PyenvInstallOpts(
            opts=itertools.chain.from_iterable(o.opts for o in [self, *others]),
            conf_opts=itertools.chain.from_iterable(o.conf_opts for o in [self, *others]),
            cflags=itertools.chain.from_iterable(o.cflags for o in [self, *others]),
            ldflags=itertools.chain.from_iterable(o.ldflags for o in [self, *others]),
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
            dep_prefix = subprocess_check_output('brew', '--prefix', dep).decode()
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

        tcl_tk_prefix = subprocess_check_output('brew', '--prefix', 'tcl-tk').decode()
        tcl_tk_ver_str = subprocess_check_output('brew', 'ls', '--versions', 'tcl-tk').decode()
        tcl_tk_ver = '.'.join(tcl_tk_ver_str.split()[1].split('.')[:2])

        return PyenvInstallOpts(conf_opts=[
            f"--with-tcltk-includes='-I{tcl_tk_prefix}/include'",
            f"--with-tcltk-libs='-L{tcl_tk_prefix}/lib -ltcl{tcl_tk_ver} -ltk{tcl_tk_ver}'",
        ])

    @cached_nullary
    def brew_ssl_opts(self) -> PyenvInstallOpts:
        pkg_config_path = subprocess_check_output('brew', '--prefix', 'openssl').decode()
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
            *,
            pyenv: Pyenv = Pyenv(),
    ) -> None:
        super().__init__()

        self._pyenv = pyenv

    def build(self) -> str:
        pio = PyenvInstallOpts().merge(*self._pyenv_pios())

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

        subprocess_check_call([self._pyenv.exe(), 'install', *pio.opts, self._version], env=env)

        bin_path = os.path.join(self._pyenv_install_path(), 'bin', 'python')
        if not os.path.isfile(bin_path):
            raise RuntimeError(f'Interpreter not found: {bin_path}')
        return bin_path


class PyenvInterpProvider(InterpProvider):

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

    @property
    def name(self) -> str:
        return 'pyenv'

    # @cached_nullary
    # def _pyenv_install_name(self) -> str:
    #     return self._version + ('-debug' if self._debug else '')
    #
    # @cached_nullary
    # def _pyenv_install_path(self) -> str:
    #     return str(os.path.join(check_not_none(self._pyenv_root()), 'versions', self._pyenv_install_name()))
    #
    # def _pyenv_pios(self) -> ta.Sequence[PyenvInstallOpts]:
    #     return [
    #         self._pyenv_basic_pio(),
    #         self._pyenv_debug_pio(),
    #     ]
    #
    # def _provide_pyenv_existing_python(self) -> ta.Optional[str]:
    #     bin_path = os.path.join(self._pyenv_install_path(), 'bin', 'python')
    #     if os.path.isfile(bin_path):
    #         return bin_path
    #     return None
    #
    # def _providers(self) -> ta.Sequence[ta.Callable[[], ta.Optional[str]]]:
    #     return [
    #         *super()._providers(),
    #         self._provide_pyenv_existing_python,
    #         self._provide_pyenv_install_python,
    #     ]

    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def get_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError
