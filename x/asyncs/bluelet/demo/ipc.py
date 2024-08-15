import multiprocessing
import pickle
import uuid

from .. import bluelet as bl


def server(ep):
    while True:
        message = yield ep.get()
        if message == 'stop':
            break
        yield ep.put(message ** 2)


def client(ep):
    for i in range(10):
        yield ep.put(i)
        squared = yield ep.get()
        print(squared)
    yield ep.put('stop')


class BlueletProc(multiprocessing.Process):
    def __init__(self, coro):
        super().__init__()
        self.coro = coro

    def run(self):
        bl.run(self.coro)


class Endpoint:
    def __init__(self, conn, sentinel):
        self.conn = conn
        self.sentinel = sentinel

    def put(self, obj):
        yield self.conn.sendall(pickle.dumps(obj) + self.sentinel)

    def get(self):
        data = yield self.conn.readline(self.sentinel)
        data = data[:-len(self.sentinel)]
        yield bl.end(pickle.loads(data))


def channel(port=4915):
    # Create a pair of connected sockets.
    connections = [None, None]
    listener = bl.Listener('127.0.0.1', port)

    def listen():
        connections[0] = yield listener.accept()  # Avoiding nonlocal.

    listen_thread = listen()
    yield bl.spawn(listen_thread)

    connections[1] = yield bl.connect('127.0.0.1', port)

    yield bl.join(listen_thread)

    # Wrap sockets in Endpoints.
    sentinel = uuid.uuid4().bytes  # Somewhat hacky...
    yield bl.end((Endpoint(connections[0], sentinel),
                       Endpoint(connections[1], sentinel)))


def ipc_demo(serial=False):
    ep1, ep2 = yield channel()
    if serial:
        # Run in bl (i.e., no parallelism).
        yield bl.spawn(server(ep1))
        yield bl.spawn(client(ep2))
    else:
        # Run in separate processes.
        ta = BlueletProc(server(ep1))
        tb = BlueletProc(client(ep2))
        ta.start()
        tb.start()
        ta.join()
        tb.join()


if __name__ == '__main__':
    bl.run(ipc_demo())
