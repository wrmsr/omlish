"""
See:
 - piku, obviously
 - https://github.com/mitogen-hq/mitogen/

git init
git remote add local ~/src/wrmsr/omlish/.git
git fetch --depth=1 local master
git remote add origin https://github.com/wrmsr/omlish
git fetch --depth=1 origin master
git checkout origin/master

{base_path}/{deploys}/
  current ->
  previous ->
  20240522T120000_{rev}
"""
import asyncio
import itertools
import os.path
import shlex
import tempfile

from omlish import check

from .. import cmds


def render_script(*cs: list[str] | tuple[str, ...]) -> str:
    return ' '.join(itertools.chain.from_iterable(
        [
            *(['&&'] if i > 0 else []),
            shlex.join(check.not_isinstance(l, str)),
        ]
        for i, l in enumerate(cs)
    ))


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


async def _a_main():
    cwd = tempfile.mkdtemp()
    print(cwd)

    bootstrap_git_path = os.path.join(os.getcwd(), '.git')
    check.state(os.path.isdir(bootstrap_git_path))

    cr: cmds.CommandRunner = cmds.LocalCommandRunner(cmds.LocalCommandRunner.Config(
        cwd=cwd,
    ))

    await do_remote_deploy(
        cr,
        local_repo_path=os.path.expanduser('~/src/wrmsr/omlish/.git'),
    )


if __name__ == '__main__':
    asyncio.run(_a_main())
