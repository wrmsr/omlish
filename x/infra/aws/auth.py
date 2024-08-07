import abc
import calendar
import collections.abc
import datetime
import email.utils
import functools
import hashlib
import hmac
import http.client
import typing as ta
import urllib.parse

from omlish import dataclasses as dc


##


class HttpHeaders(http.client.HTTPMessage):
    pass


@dc.dataclass()
class Request:
    method: str
    url: str
    headers: HttpHeaders
    data: dict[str, ta.Any]
    params: dict[str, ta.Any]
    context: dict[str, ta.Any]
    auth_path: ta.Optional[str] = None
    stream_output: bool = False
    body: ta.Optional[bytes] = None


@dc.dataclass(frozen=True)
class Credentials:
    access_key: ta.Optional[str] = None
    secret_key: ta.Optional[str] = None
    token: ta.Optional[str] = None


class NoCredentialsError(Exception):
    pass


class RequestSigner(abc.ABC):
    @abc.abstractmethod
    def add_auth(self, request: Request) -> None:
        raise NotImplemented


##


_EMPTY_SHA256_HASH = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
_PAYLOAD_BUFFER = 1024 * 1024
_SIGV4_TIMESTAMP = '%Y%m%dT%H%M%SZ'
_SIGNED_HEADERS_BLACKLIST = {
    'expect',
    'user-agent',
    'x-amzn-trace-id',
}
_UNSIGNED_PAYLOAD = 'UNSIGNED-PAYLOAD'
_STREAMING_UNSIGNED_PAYLOAD_TRAILER = 'STREAMING-UNSIGNED-PAYLOAD-TRAILER'


def _normalize_url_path(path: str) -> str:
    if not path:
        return '/'
    return _remove_dot_segments(path)


def _remove_dot_segments(url: str) -> str:
    if not url:
        return ''
    input_url = url.split('/')
    output_list = []
    for x in input_url:
        if x and x != '.':
            if x == '..':
                if output_list:
                    output_list.pop()
            else:
                output_list.append(x)

    if url[0] == '/':
        first = '/'
    else:
        first = ''
    if url[-1] == '/' and output_list:
        last = '/'
    else:
        last = ''
    return first + '/'.join(output_list) + last


def _host_from_url(url: str) -> str:
    url_parts = urllib.parse.urlsplit(url)
    host = url_parts.hostname
    default_ports = {
        'http': 80,
        'https': 443,
    }
    if url_parts.port is not None:
        if url_parts.port != default_ports.get(url_parts.scheme):
            host = '%s:%d' % (host, url_parts.port)
    return host


class RequestSignerV4(RequestSigner):

    def __init__(
            self,
            credentials: Credentials,
            service_name: str,
            region_name: str,
    ) -> None:
        super().__init__()

        self._credentials = credentials
        self._region_name = region_name
        self._service_name = service_name

    def _sign(self, key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _sign_hex(self, key: bytes, msg: str) -> str:
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).hexdigest()

    def _headers_to_sign(self, request: Request) -> HttpHeaders:
        header_map = HttpHeaders()
        for name, value in request.headers.items():
            lname = name.lower()
            if lname not in _SIGNED_HEADERS_BLACKLIST:
                header_map[lname] = value
        if 'host' not in header_map:
            header_map['host'] = _host_from_url(request.url)
        return header_map

    def _canonical_query_string(self, request: Request) -> str:
        if request.params:
            return self._canonical_query_string_params(request.params)
        else:
            return self._canonical_query_string_url(urllib.parse.urlsplit(request.url))

    def _canonical_query_string_params(self, params: ta.Union[collections.abc.Mapping, ta.Iterable]) -> str:
        key_val_pairs = []
        if isinstance(params, collections.abc.Mapping):
            params = params.items()
        for key, value in params:
            key_val_pairs.append(
                (urllib.parse.quote(key, safe='-_.~'), urllib.parse.quote(str(value), safe='-_.~'))
            )
        sorted_key_vals = []
        for key, value in sorted(key_val_pairs):
            sorted_key_vals.append(f'{key}={value}')
        canonical_query_string = '&'.join(sorted_key_vals)
        return canonical_query_string

    def _canonical_query_string_url(self, parts: urllib.parse.SplitResult) -> str:
        canonical_query_string = ''
        if parts.query:
            key_val_pairs = []
            for pair in parts.query.split('&'):
                key, _, value = pair.partition('=')
                key_val_pairs.append((key, value))
            sorted_key_vals = []
            for key, value in sorted(key_val_pairs):
                sorted_key_vals.append(f'{key}={value}')
            canonical_query_string = '&'.join(sorted_key_vals)
        return canonical_query_string

    def _canonical_headers(self, headers_to_sign: HttpHeaders) -> str:
        headers = []
        sorted_header_names = sorted(set(headers_to_sign))
        for key in sorted_header_names:
            value = ','.join(
                self._header_value(v) for v in headers_to_sign.get_all(key)
            )
            headers.append(f'{key}:{value}')
        return '\n'.join(headers)

    def _header_value(self, value: str) -> str:
        return ' '.join(value.split())

    def _signed_headers(self, headers_to_sign: HttpHeaders) -> str:
        headers = sorted(n.lower().strip() for n in set(headers_to_sign))
        return ';'.join(headers)

    def _is_streaming_checksum_payload(self, request: Request) -> bool:
        checksum_context = request.context.get('checksum', {})
        algorithm = checksum_context.get('request_algorithm')
        return isinstance(algorithm, dict) and algorithm.get('in') == 'trailer'

    def _payload(self, request: Request):
        if self._is_streaming_checksum_payload(request):
            return _STREAMING_UNSIGNED_PAYLOAD_TRAILER
        elif not self._should_sha256_sign_payload(request):
            return _UNSIGNED_PAYLOAD
        request_body = request.body
        if request_body and hasattr(request_body, 'seek'):
            position = request_body.tell()
            read_chunksize = functools.partial(
                request_body.read, _PAYLOAD_BUFFER
            )
            checksum = hashlib.sha256()
            for chunk in iter(read_chunksize, b''):
                checksum.update(chunk)
            hex_checksum = checksum.hexdigest()
            request_body.seek(position)
            return hex_checksum
        elif request_body:
            return hashlib.sha256(request_body).hexdigest()
        else:
            return _EMPTY_SHA256_HASH

    def _should_sha256_sign_payload(self, request: Request) -> bool:
        if not request.url.startswith('https'):
            return True
        return request.context.get('payload_signing_enabled', True)

    def _canonical_request(self, request: Request) -> str:
        cr = [request.method.upper()]
        path = self._normalize_url_path(urllib.parse.urlsplit(request.url).path)
        cr.append(path)
        cr.append(self._canonical_query_string(request))
        headers_to_sign = self._headers_to_sign(request)
        cr.append(self._canonical_headers(headers_to_sign) + '\n')
        cr.append(self._signed_headers(headers_to_sign))
        if 'X-Amz-Content-SHA256' in request.headers:
            body_checksum = request.headers['X-Amz-Content-SHA256']
        else:
            body_checksum = self._payload(request)
        cr.append(body_checksum)
        return '\n'.join(cr)

    def _normalize_url_path(self, path: str) -> str:
        normalized_path = urllib.parse.quote(_normalize_url_path(path), safe='/~')
        return normalized_path

    def _scope(self, request: Request) -> str:
        scope = [self._credentials.access_key]
        scope.append(request.context['timestamp'][0:8])
        scope.append(self._region_name)
        scope.append(self._service_name)
        scope.append('aws4_request')
        return '/'.join(scope)

    def _credential_scope(self, request: Request) -> str:
        scope = []
        scope.append(request.context['timestamp'][0:8])
        scope.append(self._region_name)
        scope.append(self._service_name)
        scope.append('aws4_request')
        return '/'.join(scope)

    def _string_to_sign(self, request: Request, canonical_request: str) -> str:
        sts = ['AWS4-HMAC-SHA256']
        sts.append(request.context['timestamp'])
        sts.append(self._credential_scope(request))
        sts.append(hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())
        return '\n'.join(sts)

    def _signature(self, string_to_sign: str, request: Request) -> str:
        key = self._credentials.secret_key
        k_date = self._sign((f'AWS4{key}').encode(), request.context['timestamp'][0:8])
        k_region = self._sign(k_date, self._region_name)
        k_service = self._sign(k_region, self._service_name)
        k_signing = self._sign(k_service, 'aws4_request')
        return self._sign_hex(k_signing, string_to_sign)

    def add_auth(self, request: Request) -> None:
        if self._credentials is None:
            raise NoCredentialsError()
        datetime_now = datetime.datetime.utcnow()
        request.context['timestamp'] = datetime_now.strftime(_SIGV4_TIMESTAMP)
        self._modify_request_before_signing(request)
        canonical_request = self._canonical_request(request)
        string_to_sign = self._string_to_sign(request, canonical_request)
        signature = self._signature(string_to_sign, request)
        self._inject_signature_to_request(request, signature)

    def _inject_signature_to_request(self, request: Request, signature: str) -> None:
        auth_str = ['AWS4-HMAC-SHA256 Credential=%s' % self._scope(request)]
        headers_to_sign = self._headers_to_sign(request)
        auth_str.append(f'SignedHeaders={self._signed_headers(headers_to_sign)}')
        auth_str.append('Signature=%s' % signature)
        request.headers['Authorization'] = ', '.join(auth_str)

    def _modify_request_before_signing(self, request: Request) -> None:
        if 'Authorization' in request.headers:
            del request.headers['Authorization']
        self._set_necessary_date_headers(request)
        if self._credentials.token:
            if 'X-Amz-Security-Token' in request.headers:
                del request.headers['X-Amz-Security-Token']
            request.headers['X-Amz-Security-Token'] = self._credentials.token
        if not request.context.get('payload_signing_enabled', True):
            if 'X-Amz-Content-SHA256' in request.headers:
                del request.headers['X-Amz-Content-SHA256']
            request.headers['X-Amz-Content-SHA256'] = _UNSIGNED_PAYLOAD

    def _set_necessary_date_headers(self, request: Request) -> None:
        if 'Date' in request.headers:
            del request.headers['Date']
            datetime_timestamp = datetime.datetime.strptime(request.context['timestamp'], _SIGV4_TIMESTAMP)
            request.headers['Date'] = email.utils.formatdate(int(calendar.timegm(datetime_timestamp.timetuple())))
            if 'X-Amz-Date' in request.headers:
                del request.headers['X-Amz-Date']
        else:
            if 'X-Amz-Date' in request.headers:
                del request.headers['X-Amz-Date']
            request.headers['X-Amz-Date'] = request.context['timestamp']
