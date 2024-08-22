# echoserv.py
#
# Echo server using streams

from .. import run
from .. import tcp_server


async def echo_client(client, addr):
    print('Connection from', addr)
    s = client.as_stream()
    async for line in s:
        await s.write(line)
    print('Connection closed')
    await s.close()


if __name__ == '__main__':
    run(tcp_server, '', 25000, echo_client)
