import json
import time
import urllib.request

from omlish.http import jwt
from omdev.secrets import load_secrets


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
