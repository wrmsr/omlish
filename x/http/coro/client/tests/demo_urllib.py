import urllib.request


def _main() -> None:
    def stream_response(url):
        with urllib.request.urlopen(url) as response:  # noqa
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                print(chunk.decode('utf-8'), end='')

    for url in [
        'http://www.example.com',
        'https://www.baidu.com',
        'https://anglesharp.azurewebsites.net/Chunked',
    ]:
        stream_response(url)


if __name__ == '__main__':
    _main()
