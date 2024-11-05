"""
https://cloud.google.com/compute/docs/reference/rest/v1
https://cloud.google.com/docs/authentication/rest
https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth.md
https://github.com/googleapis/google-auth-library-python/blob/8cf1cb1663fccd03ea17a1bf055d862bddf61406/google/auth/crypt/es256.py#L76
"""
import calendar
import datetime

from google.cloud import compute_v1
from google.oauth2 import service_account
import google.auth.transport.requests

from omdev.secrets import load_secrets
from omlish import check
from omlish import http as hu
from omlish import lang
from omlish.formats import json


def _main() -> None:
    cfg = load_secrets()
    creds = cfg.try_get('gcp_oauth2').reveal()
    project = cfg.get('gcp_project_id').reveal()

    creds_dct = json.loads(creds)

    ##

    from requests_oauthlib import OAuth2Session
    from oauthlib.oauth2 import ServiceApplicationClient
    import requests

    # Your client ID and secret from the OAuth2 provider
    client_id = 'your_client_id'
    client_secret = 'your_client_secret'

    # The token URL provided by the OAuth2 service
    token_url = 'https://provider.com/oauth2/token'

    # Create a client for the OAuth2 session
    client = ServiceApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    # Fetch the token
    try:
        token = oauth.fetch_token(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
        )
        print("Access Token:", token['access_token'])
    except Exception as e:
        print("An error occurred:", e)

    now = lang.utcnow()
    expirey = now + datetime.timedelta(hours=1)

    def dt_to_sec(dt: datetime.datetime) -> int:
        return calendar.timegm(dt.utctimetuple())

    payload = {
        'aud': creds_dct['token_uri'],
        'exp': dt_to_sec(expirey),
        'iat': dt_to_sec(now),
        'iss': creds_dct['client_email'],
        'scope': '',
    }

    ##

    credentials = service_account.Credentials.from_service_account_info(json.loads(creds))
    instance_client = compute_v1.InstancesClient(credentials=credentials)
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = project
    request.max_results = 50

    # transport = instance_client.transport
    # session = google.auth.transport.requests.AuthorizedSession(
    #     credentials,
    #     default_host=transport.DEFAULT_HOST
    # )

    import requests
    credentials.refresh(google.auth.transport.requests.Request(requests.Session()))

    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-client': 'gl-python/3.12.7 grpc/1.67.1 gax/2.22.0 gapic/1.20.1',
        'x-goog-request-params': f'project={project}',
    }
    credentials.apply(headers)

    # resp = session.get(
    #     f'https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/instances',
    #     allow_redirects=True,
    #     headers=headers,
    #     params=[('maxResults', '50')],
    #     timeout=None,
    # )
    # print(resp.json())

    resp = hu.request(
        f'https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/instances?maxResults=50',
        headers={
            **headers,
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, zstd',
            # 'Connection': 'keep-alive',
            # 'User-Agent': 'python-requests/2.32.3',
            'x-allowed-locations': '0x0',
        },
    )

    print(json.dumps_pretty(json.loads(resp.data.decode('utf-8'))))

    for zone, response in instance_client.aggregated_list(request=request):
        for instance in (response.instances or []):
            ip = check.single([
                ac.nat_i_p
                for ni in instance.network_interfaces
                for ac in ni.access_configs
                if ac.nat_i_p
            ])  # noqa
            print(dict(
                host=ip,
                id=instance.name,
                zone=zone,
            ))


if __name__ == '__main__':
    _main()
