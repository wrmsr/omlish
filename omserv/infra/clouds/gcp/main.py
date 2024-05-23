from collections import defaultdict
from collections.abc import Iterable

from google.oauth2 import service_account
from google.cloud import compute_v1

from ....secrets import load_secrets


def _main() -> None:
    cfg = load_secrets()

    credentials = service_account.Credentials.from_service_account_info(cfg['gcp_oauth2'])

    instance_client = compute_v1.InstancesClient(credentials=credentials)
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = cfg['gcp_project_id']
    # Use the `max_results` parameter to limit the number of results that the API returns per response page.
    request.max_results = 50

    agg_list = instance_client.aggregated_list(request=request)

    all_instances = defaultdict(list)
    print("Instances found:")
    # Despite using the `max_results` parameter, you don't need to handle the pagination
    # yourself. The returned `AggregatedListPager` object handles pagination
    # automatically, returning separated pages as you iterate over the results.
    for zone, response in agg_list:
        if response.instances:
            all_instances[zone].extend(response.instances)
            print(f" {zone}:")
            for instance in response.instances:
                print(f" - {instance.name} ({instance.machine_type})")
    print(all_instances)


if __name__ == '__main__':
    _main()
