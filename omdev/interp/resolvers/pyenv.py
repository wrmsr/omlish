# ruff: noqa: UP007
import os.path
import shutil
import typing as ta

from ...amalg.std.cached import cached_nullary
from ...amalg.std.check import check_not_none
from ..cmd import cmd
from .base import InterpResolver


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
