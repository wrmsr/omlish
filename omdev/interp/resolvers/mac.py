import os.path
import shutil
import typing as ta

from ...amalg.std.cached import cached_nullary
from ..subprocesses import cmd
from .pyenv import PyenvInstallOpts
from .pyenv import PyenvInterpResolver


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
