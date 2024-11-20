import http.server


def _main() -> None:
    http.server.test(
        HandlerClass=http.server.SimpleHTTPRequestHandler,
        port=8000,
        bind=None,
        protocol='HTTP/1.0',
    )


if __name__ == '__main__':
    _main()
