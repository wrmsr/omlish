from .. import bluelet as bl


def echoer(conn):
    while True:
        data = yield conn.recv(1024)
        if not data:
            break
        yield conn.sendall(data)


async def aechoer(conn):
    while True:
        data = await bl.Future(conn.recv(1024))
        if not data:
            break
        await bl.Future(conn.sendall(data))


if __name__ == '__main__':
    def ahandler(conn):
        yield bl.DelegationEvent(bl.drive_awaitable(aechoer(conn)))

    bl.run(
        bl.server(
            '',
            4915,
            # echoer,
            ahandler,
        ),
    )
