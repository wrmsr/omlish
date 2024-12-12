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
        ['git', 'checkout', f'origin/{rev}'],

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
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.lite.asyncio.subprocesses import asyncio_subprocess_check_call
from omlish.lite.logs import log
from omlish.lite.logs import configure_standard_logging


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
        self._git_path = os.path.join(deploy_home, 'git')

    async def init(self, repo: DeployGitRepo) -> None:
        repo_path = os.path.join(
            self._git_path,
            check.non_empty_str(repo.host),
            check.non_empty_str(repo.path),
        )
        log.info('Repo path: %s', repo_path)
        os.makedirs(repo_path)


async def _a_main() -> None:
    configure_standard_logging('INFO')

    import tempfile
    deploy_home = DeployHome(tempfile.mkdtemp())

    git = DeployGitManager(deploy_home)

    repo = DeployGitRepo(
        host='github.com',
        path='wrmsr/flaskthing',
    )

    await git.init(repo)


if __name__ == '__main__':
    import asyncio
    asyncio.run(_a_main())
