from ..logs import parse_nginx_log_line


def test_logs():
    for line in [
        '95.214.55.32 - - [23/Dec/2024:13:19:49 +0000] "GET / HTTP/1.1" 200 176 "-" "-"',
        '95.214.55.79 - - [23/Dec/2024:12:26:40 +0000] "GET / HTTP/1.1" 200 176 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46"',  # noqa
    ]:
        print(parse_nginx_log_line(line))
