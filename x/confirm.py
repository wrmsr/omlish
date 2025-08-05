import asyncio

from omdev import ptk


async def _a_main() -> None:
    print((await ptk.a_strict_confirm('Do the thing?')))


asyncio.run(_a_main())
