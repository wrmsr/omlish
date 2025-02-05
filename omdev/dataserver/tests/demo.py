from omlish.http.coro.simple import make_simple_http_server

from ..handlers import DataServerRequest
from ..http import DataServerHttpHandler
from ..routes import DataServerRoute
from ..server import DataServer
from ..targets import DataServerTarget


##


def _main() -> None:
    rts = [
        ('/hi', DataServerTarget.of(b'hi!')),
        ('/src', DataServerTarget.of(file_path=__file__)),
        ('/google', DataServerTarget.of(url='https://www.google.com/', methods=['GET'])),
    ]

    ps = DataServer(DataServer.HandlerRoute.of_(*DataServerRoute.of_(*rts)))

    for req in [
        DataServerRequest('HEAD', '/hi'),
        DataServerRequest('GET', '/hi'),
        DataServerRequest('HEAD', '/src'),
        DataServerRequest('GET', '/src'),
        DataServerRequest('GET', '/google'),
    ]:
        with ps.handle(req) as resp:
            print(resp)

    #

    with make_simple_http_server(
            5021,
            DataServerHttpHandler(ps),
            use_threads=True,
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
