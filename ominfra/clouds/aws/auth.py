"""
https://docs.aws.amazon.com/IAM/latest/UserGuide/create-signed-request.html

TODO:
 - https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-streaming.html
  - boto / s3transfer upload_fileobj doesn't stream either lol - eagerly calcs Content-MD5
 - sts tokens
 - !! fix canonical_qs - sort params
"""
import dataclasses as dc
import datetime
import hashlib
import hmac
import typing as ta
import urllib.parse

from omlish import check


##


HttpMap: ta.TypeAlias = ta.Mapping[str, ta.Sequence[str]]


def make_http_map(*kvs: tuple[str, str]) -> HttpMap:
    out: dict[str, list[str]] = {}
    for k, v in kvs:
        out.setdefault(k, []).append(v)
    return out


#

@dc.dataclass(frozen=True)
class Credentials:
    access_key: str
    secret_key: str = dc.field(repr=False)


@dc.dataclass(frozen=True)
class Request:
    method: str
    url: str
    headers: HttpMap = dc.field(default_factory=dict)
    payload: bytes = b''


##


def _host_from_url(url: str) -> str:
    url_parts = urllib.parse.urlsplit(url)
    host = check.non_empty_str(url_parts.hostname)
    default_ports = {
        'http': 80,
        'https': 443,
    }
    if url_parts.port is not None:
        if url_parts.port != default_ports.get(url_parts.scheme):
            host = '%s:%d' % (host, url_parts.port)
    return host


def _as_bytes(data: str | bytes) -> bytes:
    return data if isinstance(data, bytes) else data.encode('utf-8')


def _sha256(data: str | bytes) -> str:
    return hashlib.sha256(_as_bytes(data)).hexdigest()


def _sha256_sign(key: bytes, msg: str | bytes) -> bytes:
    return hmac.new(key, _as_bytes(msg), hashlib.sha256).digest()


def _sha256_sign_hex(key: bytes, msg: str | bytes) -> str:
    return hmac.new(key, _as_bytes(msg), hashlib.sha256).hexdigest()


_EMPTY_SHA256 = _sha256(b'')

_ISO8601 = '%Y%m%dT%H%M%SZ'

_SIGNED_HEADERS_BLACKLIST = frozenset([
    'expect',
    'user-agent',
    'x-amzn-trace-id',
])


def _lower_case_http_map(d: HttpMap) -> HttpMap:
    o: dict[str, list[str]] = {}
    for k, vs in d.items():
        o.setdefault(k.lower(), []).extend(vs)
    return o


class V4AwsSigner:
    def __init__(
            self,
            creds: Credentials,
            region_name: str,
            service_name: str,
    ) -> None:
        super().__init__()
        self._creds = creds
        self._region_name = region_name
        self._service_name = service_name

    def _validate_request(self, req: Request) -> None:
        check.non_empty_str(req.method)
        check.equal(req.method.upper(), req.method)
        for k, vs in req.headers.items():
            check.equal(k.strip(), k)
            for v in vs:
                check.equal(v.strip(), v)

    def sign(
            self,
            req: Request,
            *,
            sign_payload: bool = False,
            utcnow: datetime.datetime | None = None,
    ) -> HttpMap:
        self._validate_request(req)

        #

        if utcnow is None:
            utcnow = datetime.datetime.utcnow()  # noqa
        req_dt = utcnow.strftime(_ISO8601)

        #

        parsed_url = urllib.parse.urlsplit(req.url)
        canon_uri = parsed_url.path
        canon_qs = parsed_url.query

        #

        headers_to_sign = {
            k: v
            for k, v in _lower_case_http_map(req.headers).items()
            if k not in _SIGNED_HEADERS_BLACKLIST
        }

        if 'host' not in headers_to_sign:
            headers_to_sign['host'] = [_host_from_url(req.url)]

        headers_to_sign['x-amz-date'] = [req_dt]

        hashed_payload = _sha256(req.payload) if req.payload else _EMPTY_SHA256
        if sign_payload:
            headers_to_sign['x-amz-content-sha256'] = [hashed_payload]

        sorted_header_names = sorted(headers_to_sign)
        canon_headers = ''.join([
            ':'.join((k, ','.join(headers_to_sign[k]))) + '\n'
            for k in sorted_header_names
        ])
        signed_headers = ';'.join(sorted_header_names)

        #

        canon_req = '\n'.join([
            req.method,
            canon_uri,
            canon_qs,
            canon_headers,
            signed_headers,
            hashed_payload,
        ])

        #

        algorithm = 'AWS4-HMAC-SHA256'
        scope_parts = [
            req_dt[:8],
            self._region_name,
            self._service_name,
            'aws4_request',
        ]
        scope = '/'.join(scope_parts)
        hashed_canon_req = _sha256(canon_req)
        string_to_sign = '\n'.join([
            algorithm,
            req_dt,
            scope,
            hashed_canon_req,
        ])

        #

        key = self._creds.secret_key
        key_date = _sha256_sign(f'AWS4{key}'.encode('utf-8'), req_dt[:8])  # noqa
        key_region = _sha256_sign(key_date, self._region_name)
        key_service = _sha256_sign(key_region, self._service_name)
        key_signing = _sha256_sign(key_service, 'aws4_request')
        sig = _sha256_sign_hex(key_signing, string_to_sign)

        #

        cred_scope = '/'.join([
            self._creds.access_key,
            *scope_parts,
        ])
        auth = f'{algorithm} ' + ', '.join([
            f'Credential={cred_scope}',
            f'SignedHeaders={signed_headers}',
            f'Signature={sig}',
        ])

        #

        out = {
            'Authorization': [auth],
            'X-Amz-Date': [req_dt],
        }
        if sign_payload:
            out['X-Amz-Content-SHA256'] = [hashed_payload]
        return out
