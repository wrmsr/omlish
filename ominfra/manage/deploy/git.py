# ruff: noqa: UP006 UP007
"""
TODO:
 - 'repos'?

git/github.com/wrmsr/omlish <- bootstrap repo
 - shallow clone off bootstrap into /apps

github.com/wrmsr/omlish@rev
"""
import functools
import os.path
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.check import check

from .paths import SingleDirDeployPathOwner
from .specs import DeployGitRepo
from .types import DeployHome
from .types import DeployRev


##


class DeployGitManager(SingleDirDeployPathOwner):
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,
    ) -> None:
        super().__init__(
            owned_dir='git',
            deploy_home=deploy_home,
        )

        self._repo_dirs: ta.Dict[DeployGitRepo, DeployGitManager.RepoDir] = {}

    class RepoDir:
        def __init__(
                self,
                git: 'DeployGitManager',
                repo: DeployGitRepo,
        ) -> None:
            super().__init__()

            self._git = git
            self._repo = repo
            self._dir = os.path.join(
                self._git._dir(),  # noqa
                check.non_empty_str(repo.host),
                check.non_empty_str(repo.path),
            )

        @property
        def repo(self) -> DeployGitRepo:
            return self._repo

        @property
        def url(self) -> str:
            if self._repo.username is not None:
                return f'{self._repo.username}@{self._repo.host}:{self._repo.path}'
            else:
                return f'https://{self._repo.host}/{self._repo.path}'

        async def _call(self, *cmd: str) -> None:
            await asyncio_subprocesses.check_call(
                *cmd,
                cwd=self._dir,
            )

        @async_cached_nullary
        async def init(self) -> None:
            os.makedirs(self._dir, exist_ok=True)
            if os.path.exists(os.path.join(self._dir, '.git')):
                return

            await self._call('git', 'init')
            await self._call('git', 'remote', 'add', 'origin', self.url)

        async def fetch(self, rev: DeployRev) -> None:
            await self.init()
            await self._call('git', 'fetch', '--depth=1', 'origin', rev)

        async def checkout(self, rev: DeployRev, dst_dir: str) -> None:
            check.state(not os.path.exists(dst_dir))

            await self.fetch(rev)

            # FIXME: temp dir swap
            os.makedirs(dst_dir)

            dst_call = functools.partial(asyncio_subprocesses.check_call, cwd=dst_dir)
            await dst_call('git', 'init')

            await dst_call('git', 'remote', 'add', 'local', self._dir)
            await dst_call('git', 'fetch', '--depth=1', 'local', rev)
            await dst_call('git', 'checkout', rev)

    def get_repo_dir(self, repo: DeployGitRepo) -> RepoDir:
        try:
            return self._repo_dirs[repo]
        except KeyError:
            repo_dir = self._repo_dirs[repo] = DeployGitManager.RepoDir(self, repo)
            return repo_dir

    async def checkout(self, repo: DeployGitRepo, rev: DeployRev, dst_dir: str) -> None:
        await self.get_repo_dir(repo).checkout(rev, dst_dir)
