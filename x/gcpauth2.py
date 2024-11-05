import json
import time
import typing as ta

from omdev.secrets import load_secrets
from omlish import http
from omlish.http import jwt


def generate_gcp_jwt(
        creds_dct: ta.Mapping[str, ta.Any],
        *,
        issued_at: int | None = None,
        lifetime_s: int = 3600,
) -> str:
    return jwt.generate_jwt(
        issuer=creds_dct['client_email'],
        subject=creds_dct['client_email'],
        audience=creds_dct['token_uri'],
        issued_at=(issued_at := int(issued_at if issued_at is not None else time.time())),
        expires_at=issued_at + lifetime_s,
        scope='https://www.googleapis.com/auth/cloud-platform',
        key=creds_dct['private_key'],
        algorithm='RS256',
    )


def get_gcp_access_token(
        creds_dct: ta.Mapping[str, ta.Any],
        *,
        client: http.HttpClient | None = None,
) -> str:
    signed_jwt = generate_gcp_jwt(creds_dct)
    resp = http.request(
        creds_dct['token_uri'],
        'POST',
        data=jwt.build_get_token_body(signed_jwt).encode('utf-8'),
        headers={
            http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_FORM_URLENCODED,
        },
        client=client,
    )
    resp_dct = json.loads(resp.data.decode('utf-8'))
    return resp_dct['access_token']


def list_gcp_instances(
        api_url: str,
        access_token: str,
        *,
        client: http.HttpClient | None = None,
):
    resp = http.request(
        api_url,
        'GET',
        headers={
            http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(access_token),
        },
        client=client,
    )
    resp_dct = json.loads(resp.data.decode('utf-8'))
    return resp_dct


def _main():
    cfg = load_secrets()
    creds = cfg.try_get('gcp_oauth2').reveal()
    creds_dct = json.loads(creds)

    project_id = creds_dct['project_id']

    access_token = get_gcp_access_token(creds_dct)
    if not access_token:
        raise Exception('Failed to get access token')

    insts = list_gcp_instances(
        f'https://compute.googleapis.com/compute/v1/projects/{project_id}/aggregated/instances',
        access_token,
    )

    print(json.dumps(insts['items']['zones/us-west1-b'], indent=2, separators=(', ', ': ')))


if __name__ == '__main__':
    _main()
