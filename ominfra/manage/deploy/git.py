# ruff: noqa: UP006 UP007
"""
TODO:
 - 'repos'?

git/github.com/wrmsr/omlish <- bootstrap repo
 - shallow clone off bootstrap into /apps

github.com/wrmsr/omlish@rev
"""
import dataclasses as dc
import functools
import os.path
import typing as ta

from omlish.lite.asyncio.subprocesses import asyncio_subprocess_check_call
from omlish.lite.cached import async_cached_nullary
from omlish.lite.check import check

from .types import DeployHome


##


@dc.dataclass(frozen=True)
class DeployGitRepo:
    host: ta.Optional[str] = None
    username: ta.Optional[str] = None
    path: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.not_in('..', check.non_empty_str(self.host))
        check.not_in('.', check.non_empty_str(self.path))


@dc.dataclass(frozen=True)
class DeployGitSpec:
    repo: DeployGitRepo
    rev: str


##


class DeployGitManager:
    def __init__(
            self,
            deploy_home: DeployHome,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home
        self._dir = os.path.join(deploy_home, 'git')

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
                self._git._dir,  # noqa
                check.non_empty_str(repo.host),
                check.non_empty_str(repo.path),
            )

        @property
        def repo(self) -> DeployGitRepo:
            return self._repo

        @property
        def url(self) -> str:
            return f'{self._repo.username or "git"}@{self._repo.host}:{self._repo.path}'

        async def _call(self, *cmd: str) -> None:
            await asyncio_subprocess_check_call(
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

        async def fetch(self, rev: str) -> None:
            await self.init()
            await self._call('git', 'fetch', '--depth=1', 'origin', rev)

        async def checkout(self, rev: str, dst_dir: str) -> None:
            check.state(not os.path.exists(dst_dir))

            await self.fetch(rev)

            # FIXME: temp dir swap
            os.makedirs(dst_dir)

            dst_call = functools.partial(asyncio_subprocess_check_call, cwd=dst_dir)
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

    async def checkout(self, spec: DeployGitSpec, dst_dir: str) -> None:
        await self.get_repo_dir(spec.repo).checkout(spec.rev, dst_dir)
