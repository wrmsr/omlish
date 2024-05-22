"""
mkdir barf
cd barf
git init
git remote add local ~/src/wrmsr/omlish/.git
git fetch --depth=1 local master
git remote add origin https://github.com/wrmsr/omlish
git fetch --depth=1 origin master
git checkout origin/master
"""
import asyncio
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

    res = await cr.run_command(cr.Command([
        'git', 'clone',
        '--depth', '1',
        'https://github.com/wrmsr/omlish',
    ]))
    res.check()

    res = await cr.run_command(cr.Command([
        'sh', '-c', ' '.join([
            shlex.join([
                'cd', 'omlish',
            ]),
            '&&',
            shlex.join([
                'git', 'submodule',
                'update',
                '--init',
            ]),
            '&&',
            shlex.join([
                'make', 'venv',
            ]),
        ]),
    ]))
    res.check()


if __name__ == '__main__':
    asyncio.run(_a_main())
