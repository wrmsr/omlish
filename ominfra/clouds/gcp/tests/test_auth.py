import json

import pytest

from omlish import check
from omlish import http
from omlish.secrets.tests.harness import HarnessSecrets
from omlish.testing import pytest as ptu

from ..auth import get_gcp_access_token


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
    resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))
    return resp_dct


@ptu.skip.if_cant_import('cryptography')
@pytest.mark.online
def test_gcp_auth(harness):
    creds = harness[HarnessSecrets].get_or_skip('gcp_oauth2')
    creds_dct = json.loads(creds.reveal())

    project_id = creds_dct['project_id']

    access_token = get_gcp_access_token(creds_dct)
    if not access_token:
        raise Exception('Failed to get access token')

    insts = list_gcp_instances(
        f'https://compute.googleapis.com/compute/v1/projects/{project_id}/aggregated/instances',
        access_token,
    )

    print(json.dumps(insts['items']['zones/us-west1-b'], indent=2, separators=(', ', ': ')))
