import asyncio
import subprocess
import sys

import pytest


def test_no_import_backend():
    # Goes through sh to block pydevd from attaching and importing a ton of junk.
    # -S disables sitecustomize which is used by pydevd (inherited via environ under debug) and imports a ton of junk.
    script = f"""{sys.executable} -S -c 'import sys, {__package__.rpartition(".")[0]}; print(" ".join(sys.modules))'"""
    buf = subprocess.check_output(['sh', '-c', script]).decode()
    mods = frozenset(sl for l in buf.split(' ') if (sl := l.strip()))
    for m in {
        # 'anyio',
        'asyncio',
        'trio',
        'trio_asyncio',
    }:
        assert m not in mods


@pytest.mark.asyncs('asyncio')
async def test_simple():
    l = []

    async def f(sleepfor) -> int:
        await asyncio.sleep(sleepfor)
        return 4

    async def hello(name, sleepfor) -> int:
        l.append(f'start {name}')
        x = await f(sleepfor)
        l.append(f'end {name}')
        return x

    async def main():
        await asyncio.gather(
            hello('Billy Bob', .3),
            hello('Billy Alice', .1),
        )

    await main()
