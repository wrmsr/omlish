# ruff: noqa: UP006 UP045
# @omlish-lite
from .clients import sync_fetch_url
from .clients import print_full_response


##


def _main(url: str = 'http://example.com/') -> None:
    resp = sync_fetch_url(
        url,
    )

    print_full_response(resp)


if __name__ == '__main__':
    from omlish.logs.std.standard import configure_standard_logging
    configure_standard_logging('debug')

    # try:
    #     __import__('omlish.check')
    # except ImportError:
    #     pass

    _main()
