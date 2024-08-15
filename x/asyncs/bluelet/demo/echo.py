from .. import bluelet as bl


def echoer(conn):
    print('Connected: %s' % conn.addr[0])
    try:
        while True:
            data = yield conn.recv(1024)
            if not data:
                break
            print('Read from %s: %s' % (conn.addr[0], repr(data)))
            yield conn.sendall(data)
    finally:
        print('Disconnected: %s' % conn.addr[0])
        conn.close()


def echoserver():
    listener = bl.Listener('', 4915)
    try:
        while True:
            conn = yield listener.accept()
            yield bl.spawn(echoer(conn))
    except KeyboardInterrupt:
        print()
    finally:
        print('Exiting.')
        listener.close()


if __name__ == '__main__':
    bl.run(echoserver())
