import asyncio

import tempfile
from omserv.infra import cmds


async def _a_main():
    cwd = tempfile.mkdtemp()

    cr: cmds.CommandRunner = cmds.LocalCommandRunner(cmds.LocalCommandRunner.Config(
        cwd=cwd,
    ))

    res = await cr.run_command(cr.Command(['ls', '-al']))
    res.check()

    print(res.out.decode())


if __name__ == '__main__':
    asyncio.run(_a_main())
