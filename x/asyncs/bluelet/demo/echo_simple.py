from .. import bluelet as bl


def echoer(conn):
    while True:
        data = yield conn.recv(1024)
        if not data:
            break
        yield conn.sendall(data)


async def afoo(conn, data):
    await conn.sendall(data)
    return len(data)


async def aechoer(conn):
    while True:
        data = await conn.recv(1024)
        if not data:
            break
        n = await afoo(conn, data)
        print(n)


if __name__ == '__main__':
    bl.run(
        bl.server(
            '',
            4915,
            # echoer,
            aechoer
        ),
    )
