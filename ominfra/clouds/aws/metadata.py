"""
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` && \
    curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/
"""
import logging
import socket
import typing as ta
import urllib.error
import urllib.parse
import urllib.request

from omlish import check
from omlish import lang


##


DEFAULT_METADATA_URL = 'http://169.254.169.254/'

METADATA_TOKEN_HEADER = 'X-aws-ec2-metadata-token'  # noqa
METADATA_TOKEN_TTL_HEADER = 'X-aws-ec2-metadata-token-ttl-seconds'  # noqa


def read_metadata(
        keys: ta.Iterable[str],
        *,
        url: str = DEFAULT_METADATA_URL,
        version: str = 'latest',
        ping_timeout_s: float = 10.,
        token_ttl: int = 60,
        encoding: str = 'utf-8',
) -> dict[str, str | None] | None:
    check.not_isinstance(keys, str)

    if not url.endswith('/'):
        url += '/'

    parsed: urllib.parse.ParseResult = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = 'http://' + url
        parsed = urllib.parse.urlparse(url)
    check.arg(bool(parsed.netloc))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ping_sock:
        ping_sock.settimeout(ping_timeout_s)
        try:
            ping_sock.connect((parsed.netloc, 80))
        except OSError:
            return None

    with urllib.request.urlopen(urllib.request.Request(  # noqa
            urllib.parse.urljoin(url, f'{version}/api/token'),
            method='PUT',
            headers={
                METADATA_TOKEN_TTL_HEADER: str(token_ttl),
            },
    )) as resp:
        if resp.status != 200:
            raise Exception(f'Failed to get token')
        token = resp.read().decode(encoding).strip()

    dct = {}
    for key in keys:
        try:
            with urllib.request.urlopen(urllib.request.Request(  # noqa
                    urllib.parse.urljoin(url, f'{version}/meta-data/{key}/'),
                    headers={
                        METADATA_TOKEN_HEADER: token,
                    },
            )) as resp:
                dct[key] = resp.read().decode(encoding)
        except urllib.error.URLError:
            dct[key] = None
    return dct


DEFAULT_METADATA_KEYS: ta.AbstractSet[str] = {
    'hostname',
    'instance-id',
}


@lang.cached_function
def metadata() -> ta.Mapping[str, str | None] | None:
    return read_metadata(DEFAULT_METADATA_KEYS)


##


class MetadataLogFilter(logging.Filter):

    def filter(self, record):
        md = metadata() or {}
        record.aws_hostname = md.get('hostname', '?')
        record.aws_instance_id = md.get('instance-id', '?')
        return True


def configure_metadata_logging(handler: logging.Handler) -> None:
    handler.addFilter(MetadataLogFilter())
