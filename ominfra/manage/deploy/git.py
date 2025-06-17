# ruff: noqa: UP006 UP007 UP045
"""
TODO:
 - parse refs, resolve revs
 - non-subtree shallow clone

github.com/wrmsr/omlish@rev
"""
import functools
import os.path
import typing as ta

from omdev.git.shallow import GitShallowCloner
from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.check import check

from .paths.owners import SingleDirDeployPathOwner
from .specs import DeployGitRepo
from .specs import DeployGitSpec
from .tmp import DeployHomeAtomics
from .types import DeployHome
from .types import DeployRev


##


class DeployGitManager(SingleDirDeployPathOwner):
    def __init__(
            self,
            *,
            atomics: DeployHomeAtomics,
    ) -> None:
        super().__init__(
            owned_dir='git',
        )

        self._atomics = atomics

        self._repo_dirs: ta.Dict[DeployGitRepo, DeployGitManager.RepoDir] = {}

    #

    def make_repo_url(self, repo: DeployGitRepo) -> str:
        if repo.username is not None:
            return f'{repo.username}@{repo.host}:{repo.path}'
        else:
            return f'https://{repo.host}/{repo.path}'

    #

    class RepoDir:
        def __init__(
                self,
                git: 'DeployGitManager',
                repo: DeployGitRepo,
                home: DeployHome,
        ) -> None:
            super().__init__()

            self._git = git
            self._repo = repo
            self._home = home
            self._dir = os.path.join(
                self._git._make_dir(home),  # noqa
                check.non_empty_str(repo.host),
                check.non_empty_str(repo.path),
            )

        #

        @property
        def repo(self) -> DeployGitRepo:
            return self._repo

        @property
        def url(self) -> str:
            return self._git.make_repo_url(self._repo)

        #

        async def _call(self, *cmd: str) -> None:
            await asyncio_subprocesses.check_call(
                *cmd,
                cwd=self._dir,
            )

        #

        @async_cached_nullary
        async def init(self) -> None:
            os.makedirs(self._dir, exist_ok=True)
            if os.path.exists(os.path.join(self._dir, '.git')):
                return

            await self._call('git', 'init')
            await self._call('git', 'remote', 'add', 'origin', self.url)

        async def fetch(self, rev: DeployRev) -> None:
            await self.init()

            # This fetch shouldn't be depth=1 - git doesn't reuse local data with shallow fetches.
            await self._call('git', 'fetch', 'origin', rev)

        #

        async def checkout(self, spec: DeployGitSpec, dst_dir: str) -> None:
            check.state(not os.path.exists(dst_dir))
            with self._git._atomics(self._home).begin_atomic_path_swap(  # noqa
                    'dir',
                    dst_dir,
                    auto_commit=True,
                    make_dirs=True,
            ) as dst_swap:
                await self.fetch(spec.rev)

                dst_call = functools.partial(asyncio_subprocesses.check_call, cwd=dst_swap.tmp_path)
                await dst_call('git', 'init')

                await dst_call('git', 'remote', 'add', 'local', self._dir)
                await dst_call('git', 'fetch', '--depth=1', 'local', spec.rev)
                await dst_call('git', 'checkout', spec.rev, *(spec.subtrees or []))

    def get_repo_dir(
            self,
            repo: DeployGitRepo,
            home: DeployHome,
    ) -> RepoDir:
        try:
            return self._repo_dirs[repo]
        except KeyError:
            repo_dir = self._repo_dirs[repo] = DeployGitManager.RepoDir(
                self,
                repo,
                home,
            )
            return repo_dir

    #

    async def shallow_clone(
            self,
            spec: DeployGitSpec,
            home: DeployHome,
            dst_dir: str,
    ) -> None:
        check.state(not os.path.exists(dst_dir))
        with self._atomics(home).begin_atomic_path_swap(  # noqa
                'dir',
                dst_dir,
                auto_commit=True,
                make_dirs=True,
        ) as dst_swap:
            tdn = '.omlish-git-shallow-clone'

            for cmd in GitShallowCloner(
                    base_dir=dst_swap.tmp_path,
                    repo_url=self.make_repo_url(spec.repo),
                    repo_dir=tdn,
                    rev=spec.rev,
                    repo_subtrees=spec.subtrees,
            ).build_commands():
                await asyncio_subprocesses.check_call(
                    *cmd.cmd,
                    cwd=cmd.cwd,
                )

            td = os.path.join(dst_swap.tmp_path, tdn)
            check.state(os.path.isdir(td))
            for n in sorted(os.listdir(td)):
                os.rename(
                    os.path.join(td, n),
                    os.path.join(dst_swap.tmp_path, n),
                )
            os.rmdir(td)

    #

    async def checkout(
            self,
            spec: DeployGitSpec,
            home: DeployHome,
            dst_dir: str,
    ) -> None:
        if spec.shallow:
            await self.shallow_clone(
                spec,
                home,
                dst_dir,
            )

        else:
            await self.get_repo_dir(
                spec.repo,
                home,
            ).checkout(
                spec,
                dst_dir,
            )
