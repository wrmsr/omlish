"""
https://redis.io/docs/latest/develop/reference/protocol-spec/

https://github.com/wrmsr/tokamak/blob/3ebf3395c5bb78b80e0445199958cb81f4cf9be8/tokamak-core/src/test/java/com/wrmsr/tokamak/core/redis/Resp.java#L14
https://github.com/wrmsr/tokamak/blob/3ebf3395c5bb78b80e0445199958cb81f4cf9be8/tokamak-core/src/test/java/com/wrmsr/tokamak/core/redis/RedisTest.java
"""  # noqa
from omlish import docker
from omlish import lang
import anyio
import redis  # noqa


async def _a_main() -> None:
    cc = docker.ComposeConfig('omlish-', file_path='docker/docker-compose.yml')
    svc = cc.get_services()['redis']
    port = docker.get_compose_port(svc, 6379)
    conn = await anyio.connect_tcp('localhost', port)
    async with lang.a_defer(conn.aclose()):
        await conn.send(b'INFO\r\n')
        buf = await conn.receive()
        print(buf.decode())


if __name__ == '__main__':
    anyio.run(_a_main, backend='trio')
