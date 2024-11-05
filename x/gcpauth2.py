import json
import time

from omdev.secrets import load_secrets
from omlish import http
from omlish.http import jwt


def generate_gcp_jwt(service_account_info):
    return jwt.generate_jwt(
        issuer=service_account_info['client_email'],
        subject=service_account_info['client_email'],
        audience=service_account_info['token_uri'],
        issued_at=(issued_at := int(time.time())),
        expires_at=issued_at + 3600,  # 1 hour expiration
        scope='https://www.googleapis.com/auth/cloud-platform',
        key=service_account_info['private_key'],
        algorithm='RS256',
    )



def get_access_token(signed_jwt, token_uri):
    resp = http.request(
        token_uri,
        'POST',
        data=jwt.build_get_token_body(signed_jwt).encode('utf-8'),
        headers={
            http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_FORM_URLENCODED,
        },
    )
    resp_dct = json.loads(resp.data.decode('utf-8'))

    return resp_dct['access_token']


def list_gcp_instances(access_token, api_url):
    resp = http.request(
        api_url,
        'GET',
        headers={
            http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(access_token),
        },
    )
    resp_dct = json.loads(resp.data.decode('utf-8'))

    print(json.dumps(resp_dct['items']['zones/us-west1-b'], indent=2, separators=(', ', ': ')))


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
