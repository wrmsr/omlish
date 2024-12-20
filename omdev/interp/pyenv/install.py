# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import itertools
import os.path
import shutil
import sys
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from ..types import InterpOpts
from .pyenv import Pyenv


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


# TODO: https://github.com/pyenv/pyenv/blob/master/plugins/python-build/README.md#building-for-maximum-performance
DEFAULT_PYENV_INSTALL_OPTS = PyenvInstallOpts(
    opts=[
        '-s',
        '-v',
        '-k',
    ],
    conf_opts=[
        # FIXME: breaks on mac for older py's
        '--enable-loadable-sqlite-extensions',

        # '--enable-shared',

        '--enable-optimizations',
        '--with-lto',

        # '--enable-profiling', # ?

        # '--enable-ipv6', # ?
    ],
    cflags=[
        # '-march=native',
        # '-mtune=native',
    ],
)

DEBUG_PYENV_INSTALL_OPTS = PyenvInstallOpts(opts=['-g'])

THREADED_PYENV_INSTALL_OPTS = PyenvInstallOpts(conf_opts=['--disable-gil'])


#


class PyenvInstallOptsProvider(abc.ABC):
    @abc.abstractmethod
    def opts(self) -> ta.Awaitable[PyenvInstallOpts]:
        raise NotImplementedError


class LinuxPyenvInstallOpts(PyenvInstallOptsProvider):
    async def opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts()


class DarwinPyenvInstallOpts(PyenvInstallOptsProvider):
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

    @async_cached_nullary
    async def brew_deps_opts(self) -> PyenvInstallOpts:
        cflags = []
        ldflags = []
        for dep in self.BREW_DEPS:
            dep_prefix = await asyncio_subprocesses.check_output_str('brew', '--prefix', dep)
            cflags.append(f'-I{dep_prefix}/include')
            ldflags.append(f'-L{dep_prefix}/lib')
        return PyenvInstallOpts(
            cflags=cflags,
            ldflags=ldflags,
        )

    @async_cached_nullary
    async def brew_tcl_opts(self) -> PyenvInstallOpts:
        if await asyncio_subprocesses.try_output('brew', '--prefix', 'tcl-tk') is None:
            return PyenvInstallOpts()

        tcl_tk_prefix = await asyncio_subprocesses.check_output_str('brew', '--prefix', 'tcl-tk')
        tcl_tk_ver_str = await asyncio_subprocesses.check_output_str('brew', 'ls', '--versions', 'tcl-tk')
        tcl_tk_ver = '.'.join(tcl_tk_ver_str.split()[1].split('.')[:2])

        return PyenvInstallOpts(conf_opts=[
            f"--with-tcltk-includes='-I{tcl_tk_prefix}/include'",
            f"--with-tcltk-libs='-L{tcl_tk_prefix}/lib -ltcl{tcl_tk_ver} -ltk{tcl_tk_ver}'",
        ])

    # @cached_nullary
    # def brew_ssl_opts(self) -> PyenvInstallOpts:
    #     pkg_config_path = subprocess_check_output_str('brew', '--prefix', 'openssl')
    #     if 'PKG_CONFIG_PATH' in os.environ:
    #         pkg_config_path += ':' + os.environ['PKG_CONFIG_PATH']
    #     return PyenvInstallOpts(env={'PKG_CONFIG_PATH': pkg_config_path})

    async def opts(self) -> PyenvInstallOpts:
        return PyenvInstallOpts().merge(
            self.framework_opts(),
            await self.brew_deps_opts(),
            await self.brew_tcl_opts(),
            # self.brew_ssl_opts(),
        )


PLATFORM_PYENV_INSTALL_OPTS: ta.Dict[str, PyenvInstallOptsProvider] = {
    'darwin': DarwinPyenvInstallOpts(),
    'linux': LinuxPyenvInstallOpts(),
}


##


class PyenvVersionInstaller:
    """
    Messy: can install freethreaded build with a 't' suffixed version str _or_ by THREADED_PYENV_INSTALL_OPTS - need
    latter to build custom interp with ft, need former to use canned / blessed interps. Muh.
    """

    def __init__(
            self,
            version: str,
            opts: ta.Optional[PyenvInstallOpts] = None,
            interp_opts: InterpOpts = InterpOpts(),
            *,
            pyenv: Pyenv,

            install_name: ta.Optional[str] = None,
            no_default_opts: bool = False,
    ) -> None:
        super().__init__()

        self._version = version
        self._given_opts = opts
        self._interp_opts = interp_opts
        self._given_install_name = install_name

        self._no_default_opts = no_default_opts
        self._pyenv = pyenv

    @property
    def version(self) -> str:
        return self._version

    @async_cached_nullary
    async def opts(self) -> PyenvInstallOpts:
        opts = self._given_opts
        if self._no_default_opts:
            if opts is None:
                opts = PyenvInstallOpts()
        else:
            lst = [self._given_opts if self._given_opts is not None else DEFAULT_PYENV_INSTALL_OPTS]
            if self._interp_opts.debug:
                lst.append(DEBUG_PYENV_INSTALL_OPTS)
            if self._interp_opts.threaded:
                lst.append(THREADED_PYENV_INSTALL_OPTS)
            lst.append(await PLATFORM_PYENV_INSTALL_OPTS[sys.platform].opts())
            opts = PyenvInstallOpts().merge(*lst)
        return opts

    @cached_nullary
    def install_name(self) -> str:
        if self._given_install_name is not None:
            return self._given_install_name
        return self._version + ('-debug' if self._interp_opts.debug else '')

    @async_cached_nullary
    async def install_dir(self) -> str:
        return str(os.path.join(check.not_none(await self._pyenv.root()), 'versions', self.install_name()))

    @async_cached_nullary
    async def install(self) -> str:
        opts = await self.opts()
        env = {**os.environ, **opts.env}
        for k, l in [
            ('CFLAGS', opts.cflags),
            ('LDFLAGS', opts.ldflags),
            ('PYTHON_CONFIGURE_OPTS', opts.conf_opts),
        ]:
            v = ' '.join(l)
            if k in os.environ:
                v += ' ' + os.environ[k]
            env[k] = v

        conf_args = [
            *opts.opts,
            self._version,
        ]

        full_args: ta.List[str]
        if self._given_install_name is not None:
            full_args = [
                os.path.join(check.not_none(await self._pyenv.root()), 'plugins', 'python-build', 'bin', 'python-build'),  # noqa
                *conf_args,
                await self.install_dir(),
            ]
        else:
            full_args = [
                await self._pyenv.exe(),
                'install',
                *conf_args,
            ]

        await asyncio_subprocesses.check_call(
            *full_args,
            env=env,
        )

        exe = os.path.join(await self.install_dir(), 'bin', 'python')
        if not os.path.isfile(exe):
            raise RuntimeError(f'Interpreter not found: {exe}')
        return exe
