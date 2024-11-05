import abc
import base64
import hashlib
import hmac
import json
import time
import typing as ta
import urllib.request

from omlish import lang
from omlish import http
from omdev.secrets import load_secrets


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


def as_bytes(v: str | bytes, encoding: str = 'utf-8') -> bytes:
    return v.encode(encoding) if isinstance(v, str) else v


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


class HmacSha256Algorithm(Algorithm):
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
        return hmac.new(key, msg, self._digest).digest()


class RsaSha256Algorithm(Algorithm):
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
        HmacSha256Algorithm('HS256', hashlib.sha256),
        RsaSha256Algorithm('RS256', 'SHA256'),
    ]
}


def base64url_encode(b: bytes) -> bytes:
    return base64.urlsafe_b64encode(b).replace(b'=', b'')


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
):
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


def generate_gcp_jwt(service_account_info):
    return generate_jwt(
        issuer=service_account_info['client_email'],
        subject=service_account_info['client_email'],
        audience=service_account_info['token_uri'],
        issued_at=(issued_at := int(time.time())),
        expires_at=issued_at + 3600,  # 1 hour expiration
        scope='https://www.googleapis.com/auth/cloud-platform',
        key=service_account_info['private_key'],
        algorithm='RS256',
    )


SERVICE_APPLICATION_GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'


def get_access_token(signed_jwt, token_uri):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    body = f'grant_type={SERVICE_APPLICATION_GRANT_TYPE}&assertion={signed_jwt}'

    request = urllib.request.Request(
        token_uri,
        data=body.encode('utf-8'),
        headers=headers,
        method='POST',
    )
    with urllib.request.urlopen(request) as response:
        response_data = json.loads(response.read().decode('utf-8'))
        return response_data['access_token']


def list_gcp_instances(access_token, api_url):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    request = urllib.request.Request(api_url, headers=headers, method='GET')
    with urllib.request.urlopen(request) as response:
        resp = json.loads(response.read().decode('utf-8'))

    print(json.dumps(resp['items']['zones/us-west1-b'], indent=2, separators=(', ', ': ')))


def _main():
    cfg = load_secrets()
    creds = cfg.try_get('gcp_oauth2').reveal()
    creds_dct = json.loads(creds)

    project_id = creds_dct['project_id']
    api_url = f'https://compute.googleapis.com/compute/v1/projects/{project_id}/aggregated/instances'

    signed_jwt = generate_gcp_jwt(creds_dct)
    access_token = get_access_token(signed_jwt, creds_dct['token_uri'])
    if access_token:
        list_gcp_instances(access_token, api_url)


if __name__ == '__main__':
    _main()
