# ruff: noqa: UP006 UP007
"""
TODO:
 - custom tags
  - 'aliases'
  - https://github.com/pyenv/pyenv/pull/2966
  - https://github.com/pyenv/pyenv/issues/218 (lol)
  - probably need custom (temp?) definition file
  - *or* python-build directly just into the versions dir?
 - optionally install / upgrade pyenv itself
 - new vers dont need these custom mac opts, only run on old vers
"""
import os.path
import shutil
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.check import check


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

    @async_cached_nullary
    async def root(self) -> ta.Optional[str]:
        if self._root_kw is not None:
            return self._root_kw

        if shutil.which('pyenv'):
            return await asyncio_subprocesses.check_output_str('pyenv', 'root')

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @async_cached_nullary
    async def exe(self) -> str:
        return os.path.join(check.not_none(await self.root()), 'bin', 'pyenv')

    async def version_exes(self) -> ta.List[ta.Tuple[str, str]]:
        if (root := await self.root()) is None:
            return []
        ret = []
        vp = os.path.join(root, 'versions')
        if os.path.isdir(vp):
            for dn in os.listdir(vp):
                ep = os.path.join(vp, dn, 'bin', 'python')
                if not os.path.isfile(ep):
                    continue
                ret.append((dn, ep))
        return ret

    async def installable_versions(self) -> ta.List[str]:
        if await self.root() is None:
            return []
        ret = []
        s = await asyncio_subprocesses.check_output_str(await self.exe(), 'install', '--list')
        for l in s.splitlines():
            if not l.startswith('  '):
                continue
            l = l.strip()
            if not l:
                continue
            ret.append(l)
        return ret

    async def update(self) -> bool:
        if (root := await self.root()) is None:
            return False
        if not os.path.isdir(os.path.join(root, '.git')):
            return False
        await asyncio_subprocesses.check_call('git', 'pull', cwd=root)
        return True
