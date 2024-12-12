# ruff: noqa: UP006 UP007
"""
TODO:
 - 'repos'?

git/github.com/wrmsr/omlish <- bootstrap repo
 - shallow clone off bootstrap into /apps

github.com/wrmsr/omlish@rev

==

async def do_remote_deploy(
        cr: cmds.CommandRunner,
        rev: str = 'master',
        *,
        local_repo_path: str | None = None,
        skip_submodules: bool = False,
) -> None:
    clone_script = [
        ['git', 'init'],

        *([
            ['git', 'remote', 'add', 'local', local_repo_path],
            ['git', 'fetch', '--depth=1', 'local', rev],
        ] if local_repo_path is not None else ()),

        ['git', 'remote', 'add', 'origin', 'https://github.com/wrmsr/omlish'],
        ['git', 'fetch', '--depth=1', 'origin', rev],
        ['git', 'checkout', rev],

        *([['git', 'submodule', 'update', '--init']] if not skip_submodules else ()),

        ['make', 'venv-deploy'],
    ]

    res = await cr.run_command(cr.Command([
        'sh', '-c', render_script(
            ['mkdir', 'omlish'],
            ['cd', 'omlish'],
            *clone_script,
        ),
    ]))
    res.check()
"""
import dataclasses as dc
import functools
import os.path
import typing as ta

from omlish.lite.asyncio.subprocesses import asyncio_subprocess_check_call
from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log


DeployHome = ta.NewType('DeployHome', str)


@dc.dataclass(frozen=True)
class DeployGitRepo:
    host: ta.Optional[str] = None
    username: ta.Optional[str] = None
    path: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.host)
        check.non_empty_str(self.path)
        check.not_in('.', self.path)
        check.not_in('..', self.host)



@dc.dataclass(frozen=True)
class DeployGitSpec:
    repo: DeployGitRepo
    rev: str


class DeployGitManager:
    def __init__(
            self,
            deploy_home: DeployHome
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home
        self._dir = os.path.join(deploy_home, 'git')

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
                self._git._dir,
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


async def _a_main() -> None:
    configure_standard_logging('INFO')

    import tempfile
    deploy_home = DeployHome(tempfile.mkdtemp())

    git = DeployGitManager(deploy_home)

    spec = DeployGitSpec(
        repo=DeployGitRepo(
            host='github.com',
            path='wrmsr/flaskthing',
        ),
        rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
    )

    repo_dir = DeployGitManager.RepoDir(git, spec.repo)
    await repo_dir.fetch(spec.rev)


if __name__ == '__main__':
    import asyncio
    asyncio.run(_a_main())
