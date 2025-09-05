# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.logs.protocols import LoggerLike

from ...packaging.versions import InvalidVersion
from ...packaging.versions import Version
from ..inspect import InterpInspector
from ..providers.base import InterpProvider
from ..types import Interp
from ..types import InterpOpts
from ..types import InterpSpecifier
from ..types import InterpVersion
from .install import PyenvVersionInstaller
from .pyenv import Pyenv


##


class PyenvInterpProvider(InterpProvider):
    @dc.dataclass(frozen=True)
    class Options:
        inspect: bool = False

        try_update: bool = False

    def __init__(
            self,
            options: Options = Options(),
            *,
            pyenv: Pyenv,
            inspector: InterpInspector,
            log: ta.Optional[LoggerLike] = None,
    ) -> None:
        super().__init__()

        self._options = options

        self._pyenv = pyenv
        self._inspector = inspector
        self._log = log

    #

    @staticmethod
    def guess_version(s: str) -> ta.Optional[InterpVersion]:
        def strip_sfx(s: str, sfx: str) -> ta.Tuple[str, bool]:
            if s.endswith(sfx):
                return s[:-len(sfx)], True
            return s, False
        ok = {}
        s, ok['debug'] = strip_sfx(s, '-debug')
        s, ok['threaded'] = strip_sfx(s, 't')
        try:
            v = Version(s)
        except InvalidVersion:
            return None
        return InterpVersion(v, InterpOpts(**ok))

    class Installed(ta.NamedTuple):
        name: str
        exe: str
        version: InterpVersion

    async def _make_installed(self, vn: str, ep: str) -> ta.Optional[Installed]:
        iv: ta.Optional[InterpVersion]
        if self._options.inspect:
            try:
                iv = check.not_none(await self._inspector.inspect(ep)).iv
            except Exception as e:  # noqa
                return None
        else:
            iv = self.guess_version(vn)
        if iv is None:
            return None
        return PyenvInterpProvider.Installed(
            name=vn,
            exe=ep,
            version=iv,
        )

    async def installed(self) -> ta.Sequence[Installed]:
        ret: ta.List[PyenvInterpProvider.Installed] = []
        for vn, ep in await self._pyenv.version_exes():
            if (i := await self._make_installed(vn, ep)) is None:
                if self._log is not None:
                    self._log.debug('Invalid pyenv version: %s', vn)
                continue
            ret.append(i)
        return ret

    #

    async def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [i.version for i in await self.installed()]

    async def get_installed_version(self, version: InterpVersion) -> Interp:
        for i in await self.installed():
            if i.version == version:
                return Interp(
                    exe=i.exe,
                    version=i.version,
                )
        raise KeyError(version)

    #

    async def _get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        lst = []

        for vs in await self._pyenv.installable_versions():
            if (iv := self.guess_version(vs)) is None:
                continue
            if iv.opts.debug:
                raise Exception('Pyenv installable versions not expected to have debug suffix')
            for d in [False, True]:
                lst.append(dc.replace(iv, opts=dc.replace(iv.opts, debug=d)))

        return lst

    async def get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        lst = await self._get_installable_versions(spec)

        if self._options.try_update and not any(v in spec for v in lst):
            if self._pyenv.update():
                lst = await self._get_installable_versions(spec)

        return lst

    async def install_version(self, version: InterpVersion) -> Interp:
        inst_version = str(version.version)
        inst_opts = version.opts
        if inst_opts.threaded:
            inst_version += 't'
            inst_opts = dc.replace(inst_opts, threaded=False)

        installer = PyenvVersionInstaller(
            inst_version,
            interp_opts=inst_opts,
            pyenv=self._pyenv,
        )

        exe = await installer.install()
        return Interp(exe, version)
