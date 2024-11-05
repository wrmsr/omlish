import abc
import base64
import hashlib
import hmac
import json
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import cryptography.hazmat.primitives.asymmetric.padding
    import cryptography.hazmat.primitives.hashes
    import cryptography.hazmat.primitives.serialization
else:
    cryptography = lang.proxy_import('cryptography', extras=[
        'hazmat.primitives.asymmetric.padding',
        'hazmat.primitives.hashes',
        'hazmat.primitives.serialization',
    ])


##


def as_bytes(v: str | bytes, encoding: str = 'utf-8') -> bytes:
    return v.encode(encoding) if isinstance(v, str) else v


def base64url_encode(b: bytes) -> bytes:
    return base64.urlsafe_b64encode(b).replace(b'=', b'')


##


class Algorithm(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def prepare_key(self, key: str | bytes) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def sign(self, msg: str | bytes, key: ta.Any) -> bytes:
        raise NotImplementedError


class HmacAlgorithm(Algorithm):
    def __init__(self, name: str, digest: ta.Any) -> None:
        super().__init__()
        self._name = name
        self._digest = digest

    @property
    def name(self) -> str:
        return self._name

    def prepare_key(self, key: str | bytes) -> ta.Any:
        return as_bytes(key)

    def sign(self, msg: str | bytes, key: ta.Any) -> bytes:
        return hmac.new(key, as_bytes(msg), self._digest).digest()


class RsaAlgorithm(Algorithm):
    def __init__(self, name: str, digest: str) -> None:
        super().__init__()
        self._name = name
        self._digest = digest

    @property
    def name(self) -> str:
        return self._name

    def prepare_key(self, key: str | bytes) -> ta.Any:
        if (key_bytes := as_bytes(key)).startswith(b'ssh-rsa'):
            return cryptography.hazmat.primitives.serialization.load_ssh_public_key(key_bytes)
        else:
            return cryptography.hazmat.primitives.serialization.load_pem_private_key(key_bytes, password=None)

    def sign(self, msg: str | bytes, key: ta.Any) -> bytes:
        return key.sign(
            as_bytes(msg),
            cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15(),
            getattr(cryptography.hazmat.primitives.hashes, self._digest)(),
        )


ALGORITHMS_BY_NAME = {
    a.name: a for a in [
        HmacAlgorithm('HS256', hashlib.sha256),
        HmacAlgorithm('HS384', hashlib.sha384),
        HmacAlgorithm('HS512', hashlib.sha512),

        RsaAlgorithm('RS256', 'SHA256'),
        RsaAlgorithm('RS384', 'SHA384'),
        RsaAlgorithm('RS512', 'SHA512'),
    ]
}


##


def jwt_encode(
        payload: ta.Mapping[str, ta.Any],
        key: str | bytes,
        *,
        algorithm: str = 'HS256',
) -> str:
    alg = ALGORITHMS_BY_NAME[algorithm]

    segments: list[bytes] = []

    header: dict[str, ta.Any] = {
        'typ': 'jwt',
        'alg': alg.name,
    }
    json_header = json.dumps(header, separators=(',', ':'), sort_keys=True).encode('utf-8')
    segments.append(base64url_encode(json_header))

    json_payload = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    msg_payload = base64url_encode(json_payload)
    segments.append(msg_payload)

    signing_input = b'.'.join(segments)

    key = alg.prepare_key(key)
    signature = alg.sign(signing_input, key)

    segments.append(base64url_encode(signature))

    encoded_string = b'.'.join(segments)
    return encoded_string.decode('utf-8')


def generate_jwt(
        *,
        issuer: str,
        subject: str,
        audience: str,
        issued_at: int,
        expires_at: int,
        scope: str,
        key: str | bytes,
        **kwargs: ta.Any,
) -> str:
    payload = {
        'iss': issuer,
        'sub': subject,
        'aud': audience,
        'iat': issued_at,
        'exp': expires_at,
        'scope': scope,
    }

    return jwt_encode(
        payload,
        key,
        **kwargs,
    )


##


SERVICE_APPLICATION_GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'


def build_get_token_body(
        signed_jwt: str,
        *,
        grant_type: str = SERVICE_APPLICATION_GRANT_TYPE,
) -> str:
    return f'grant_type={grant_type}&assertion={signed_jwt}'
