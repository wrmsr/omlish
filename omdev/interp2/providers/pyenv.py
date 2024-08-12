# ruff: noqa: UP007
import dataclasses as dc
import itertools
import os.path
import shutil
import typing as ta

from ...amalg.std.cached import cached_nullary
from ...amalg.std.check import check_not_none
from ...amalg.std.subprocesses import subprocess_try_call
from .base import Interp
from .base import InterpProvider
from .base import InterpVersion


@dc.dataclass(frozen=True)
class PyenvInstallOpts(ta.NamedTuple):
    opts: ta.Sequence[str] = ()
    conf_opts: ta.Sequence[str] = ()
    cflags: ta.Sequence[str] = ()
    ldflags: ta.Sequence[str] = ()
    env: ta.Mapping[str, str] = dc.field(default_factory=dict)

    def combine(self, *others: 'PyenvInstallOpts') -> 'PyenvInstallOpts':
        return PyenvInstallOpts(
            opts=itertools.chain.from_iterable(o.opts for o in [self, *others]),
            conf_opts=itertools.chain.from_iterable(o.conf_opts for o in [self, *others]),
            cflags=itertools.chain.from_iterable(o.cflags for o in [self, *others]),
            ldflags=itertools.chain.from_iterable(o.ldflags for o in [self, *others]),
            env=dict(itertools.chain.from_iterable(o.env.items() for o in [self, *others])),
        )


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

    @cached_nullary
    def pyenv_root(self) -> ta.Optional[str]:
        if self._pyenv_root_kw is not None:
            return self._pyenv_root_kw

        if shutil.which('pyenv'):
            return cmd(['pyenv', 'root'])

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @property
    def name(self) -> str:
        return 'pyenv'

    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def get_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError

    # @cached_nullary
    # def _pyenv_bin(self) -> str:
    #     return os.path.join(check_not_none(self._pyenv_root()), 'bin', 'pyenv')
    #
    # @cached_nullary
    # def _pyenv_install_name(self) -> str:
    #     return self._version + ('-debug' if self._debug else '')
    #
    # @cached_nullary
    # def _pyenv_install_path(self) -> str:
    #     return str(os.path.join(check_not_none(self._pyenv_root()), 'versions', self._pyenv_install_name()))
    #
    # @cached_nullary
    # def _pyenv_basic_pio(self) -> PyenvInstallOpts:
    #     return PyenvInstallOpts.new(opts=['-s', '-v'])
    #
    # @cached_nullary
    # def _pyenv_debug_pio(self) -> PyenvInstallOpts:
    #     if not self._debug:
    #         return PyenvInstallOpts.new()
    #     return PyenvInstallOpts.new(opts=['-g'])
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
    # def _provide_pyenv_install_python(self) -> ta.Optional[str]:
    #     pio = PyenvInstallOpts.new().combine(*self._pyenv_pios())
    #
    #     env = dict(pio.env)
    #     for k, l in [
    #         ('CFLAGS', pio.cflags),
    #         ('LDFLAGS', pio.ldflags),
    #         ('PYTHON_CONFIGURE_OPTS', pio.conf_opts),
    #     ]:
    #         v = ' '.join(l)
    #         if k in os.environ:
    #             v += ' ' + os.environ[k]
    #         env[k] = v
    #
    #     cmd([self._pyenv_bin(), 'install', *pio.opts, self._version], env=env)
    #
    #     bin_path = os.path.join(self._pyenv_install_path(), 'bin', 'python')
    #     if not os.path.isfile(bin_path):
    #         raise RuntimeError(f'Interpreter not found: {bin_path}')
    #     return bin_path
    #
    # def _providers(self) -> ta.Sequence[ta.Callable[[], ta.Optional[str]]]:
    #     return [
    #         *super()._providers(),
    #         self._provide_pyenv_existing_python,
    #         self._provide_pyenv_install_python,
    #     ]
