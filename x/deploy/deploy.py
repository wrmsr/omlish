import asyncio
import shlex
import tempfile

from omserv.infra import cmds


async def _a_main():
    cwd = tempfile.mkdtemp()
    print(cwd)

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
