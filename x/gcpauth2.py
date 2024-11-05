import abc
import base64
import json
import time
import typing as ta
import urllib.request

from omdev.secrets import load_secrets


class Algorithm(abc.ABC):
    @abc.abstractmethod
    def prepare_key(self, key: str) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def sign(self, s: bytes, key: ta.Any) -> bytes:
        raise NotImplementedError


class RsaSha256Algorithm(Algorithm):
    def prepare_key(self, key: str) -> ta.Any:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        return load_pem_private_key(key.encode('utf-8'), password=None)

    def sign(self, msg: bytes, key: ta.Any) -> bytes:
        from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
        from cryptography.hazmat.primitives.hashes import SHA256
        return key.sign(msg, PKCS1v15(), SHA256())


def base64url_encode(b: bytes) -> bytes:
    return base64.urlsafe_b64encode(b).replace(b'=', b'')


def jwt_encode(
        payload: ta.Mapping[str, ta.Any],
        key: str,
        algorithm: str = 'RS256',
):
    segments: list[bytes] = []

    header: dict[str, ta.Any] = {
        'typ': 'jwt',
        'alg': algorithm,
    }
    json_header = json.dumps(header, separators=(',', ':'), sort_keys=True).encode()
    segments.append(base64url_encode(json_header))

    json_payload = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    msg_payload = base64url_encode(json_payload)
    segments.append(msg_payload)

    signing_input = b'.'.join(segments)

    alg_obj = RsaSha256Algorithm()
    key = alg_obj.prepare_key(key)
    signature = alg_obj.sign(signing_input, key)

    segments.append(base64url_encode(signature))

    encoded_string = b'.'.join(segments)
    return encoded_string.decode('utf-8')


def generate_jwt(service_account_info):
    issued_at = int(time.time())
    expires_at = issued_at + 3600  # 1 hour expiration

    payload = {
        'iss': service_account_info['client_email'],
        'sub': service_account_info['client_email'],
        'aud': service_account_info['token_uri'],
        'iat': issued_at,
        'exp': expires_at,
        'scope': 'https://www.googleapis.com/auth/cloud-platform'
    }

    signed_jwt = jwt_encode(
        payload,
        service_account_info['private_key'],
        algorithm='RS256',
    )
    return signed_jwt


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
        response_data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(response_data, indent=2, separators=(', ', ': ')))


def _main():
    cfg = load_secrets()
    creds = cfg.try_get('gcp_oauth2').reveal()
    creds_dct = json.loads(creds)

    project_id = creds_dct['project_id']
    api_url = f'https://compute.googleapis.com/compute/v1/projects/{project_id}/aggregated/instances'

    signed_jwt = generate_jwt(creds_dct)
    access_token = get_access_token(signed_jwt, creds_dct['token_uri'])
    if access_token:
        list_gcp_instances(access_token, api_url)


if __name__ == '__main__':
    _main()
