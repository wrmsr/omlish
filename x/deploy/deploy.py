"""
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
from omserv.infra import cmds


async def _a_main():
    cwd = tempfile.mkdtemp()
    print(cwd)

    bootstrap_git_path = os.path.join(os.getcwd(), '.git')
    check.state(os.path.isdir(bootstrap_git_path))

    cr: cmds.CommandRunner = cmds.LocalCommandRunner(cmds.LocalCommandRunner.Config(
        cwd=cwd,
    ))

    clone_script = [
        ['git', 'init'],
        ['git', 'remote', 'add', 'local', os.path.expanduser('~/src/wrmsr/omlish/.git'), ],
        ['git', 'fetch', '--depth=1', 'local', 'master', ],
        ['git', 'remote', 'add', 'origin', 'https://github.com/wrmsr/omlish'],
        ['git', 'fetch', '--depth=1', 'origin', 'master'],
        ['git', 'checkout', 'origin/master'],

        ['git', 'submodule', 'update', '--init'],
        ['make', 'venv'],
    ]

    res = await cr.run_command(cr.Command([
        'sh', '-c', ' '.join(itertools.chain.from_iterable(
            [
                *(['&&'] if i > 0 else []),
                shlex.join(l)
            ]
            for i, l in enumerate([
                ['mkdir', 'omlish'],
                ['cd', 'omlish'],
                *clone_script,
            ])
        )),
    ]))
    res.check()


if __name__ == '__main__':
    asyncio.run(_a_main())
