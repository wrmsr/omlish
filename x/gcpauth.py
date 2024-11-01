"""
https://cloud.google.com/compute/docs/reference/rest/v1
https://cloud.google.com/docs/authentication/rest
https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth.md
https://github.com/googleapis/google-auth-library-python/blob/8cf1cb1663fccd03ea17a1bf055d862bddf61406/google/auth/crypt/es256.py#L76
"""
import json

from google.cloud import compute_v1
from google.oauth2 import service_account

from omdev.secrets import load_secrets
from omlish import check


def _main() -> None:
    cfg = load_secrets()
    creds = cfg.try_get('gcp_oauth2').reveal()
    project = cfg.get('gcp_project_id').reveal()

    credentials = service_account.Credentials.from_service_account_info(json.loads(creds))
    instance_client = compute_v1.InstancesClient(credentials=credentials)
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = project
    request.max_results = 50

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
