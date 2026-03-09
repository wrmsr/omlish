# ruff: noqa: UP006 UP045
# @omlish-lite
from .....logs.std.standard import configure_standard_logging
from .clients import print_full_response
from .clients import sync_fetch_url


##


def _main(url: str = 'https://example.com/') -> None:
    resp = sync_fetch_url(
        url,
        flow_auto_read=True,
    )

    print_full_response(resp)


if __name__ == '__main__':
    configure_standard_logging('debug')

    # try:
    #     __import__('omlish.check')
    # except ImportError:
    #     pass

    _main()
