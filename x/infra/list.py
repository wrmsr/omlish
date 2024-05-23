"""
unique server ids:
 aws:{region_name}:{instance_id}
 runpod:{id}
 lambda_labs:{id}
"""
import json
import pprint
import typing as ta
import urllib3

from omlish import dataclasses as dc
from omlish import check
from omlish import lang
from omserv.secrets import load_secrets


##


@lang.cached_nullary
def _get_secrets() -> dict[str, ta.Any]:
    return load_secrets()


##


@dc.dataclass(frozen=True)
class Server:
    host: str


##


@dc.dataclass(frozen=True)
class AwsServer(Server):
    id: str
    region: str


def get_aws_servers() -> list[Server]:
    import boto3
    ec2 = boto3.client('ec2')
    resp = ec2.describe_instances()
    out = []
    for res in resp.get('Reservations', []):
        for inst in res.get('Instances', []):
            out.append(AwsServer(
                host=inst['PublicIpAddress'],
                id=inst['InstanceId'],
                region=ec2.meta.region_name,
            ))
    return out


##


@dc.dataclass(frozen=True)
class GcpServer(Server):
    id: str
    region: str


def get_gcp_servers() -> list[GcpServer]:
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


##


@dc.dataclass(frozen=True)
class RunpodServer(Server):
    id: str


def get_runpod_servers() -> list[RunpodServer]:
    api_key = _get_secrets()['runpod_api_key']
    query = 'query Pods { myself { pods { id runtime { ports { ip isIpPublic privatePort publicPort type } } } } }'
    resp = urllib3.request(
        'POST',
        f'https://api.runpod.io/graphql?api_key={api_key}',
        body=('{"query": "' + query + '"}').encode('utf-8'),
        headers={
            'content-type': 'application/json',
        },
    )
    dct = json.loads(resp.data.decode('utf-8')).get('data', {}).get('myself', {})
    out = []
    for pod in dct.get('pods', []):
        ssh = check.single([p for p in pod['runtime']['ports'] if p['isIpPublic'] and p['privatePort'] == 22])
        out.append(RunpodServer(
            host=f'{ssh["ip"]}:{ssh["publicPort"]}',
            id=pod['id'],
        ))
    return out


##


@dc.dataclass(frozen=True)
class LambdaLabsServer(Server):
    id: str


def get_lambda_labs_servers() -> list[LambdaLabsServer]:
    api_key = _get_secrets()['lambda_labs_api_key']
    resp = urllib3.request(
        'GET',
        'https://cloud.lambdalabs.com/api/v1/instances',
        headers=urllib3.make_headers(
            basic_auth=f'{api_key}:',
        ),
    )
    insts = json.loads(resp.data.decode('utf-8')).get('data', {})
    out = []
    for inst in insts:
        out.append(LambdaLabsServer(
            host=inst['ip'],
            id=inst['id'],
        ))
    return out


##


@dc.dataclass(frozen=True)
class DigitalOceanServer(Server):
    id: str


def get_digital_ocean_servers() -> list[DigitalOceanServer]:
    api_key = _get_secrets()['digital_ocean_api_key']
    resp = urllib3.request(
        'GET',
        'https://api.digitalocean.com/v2/droplets',
        headers={
            'Authorization': f'Bearer {api_key}'
        }
    )
    droplets = json.loads(resp.data.decode('utf-8')).get('droplets', [])
    out = []
    for droplet in droplets:
        net = check.single([n for n in droplet['networks']['v4'] if n['type'] == 'public'])
        out.append(DigitalOceanServer(
            host=net['ip_address'],
            id=droplet['id'],
        ))
    return out


##


def _main() -> None:
    svrs = [
        *get_aws_servers(),
        *get_runpod_servers(),
        *get_lambda_labs_servers(),
        *get_digital_ocean_servers(),
    ]

    pprint.pprint(svrs)


if __name__ == '__main__':
    _main()
