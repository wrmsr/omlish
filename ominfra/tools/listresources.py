"""
TODO:
 - async
 - 'things' not just servers ('resources'?) - s3 buckets, db servers, etc
 - ssh
  - keys

unique server ids:
 aws:{region_name}:{instance_id}
 runpod:{id}
 lambda_labs:{id}
"""
import json
import pprint

import urllib3

from omdev.secrets import load_secrets
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import secrets as sec


##


@lang.cached_function
def _get_secrets() -> sec.Secrets:
    return load_secrets()


##


class Resource(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Server(Resource):
    host: str


class ObjectStorage(Resource):
    pass


@dc.dataclass(frozen=True)
class DbInstance(Resource):
    host: str
    port: int


##


class AwsResource(Resource):
    pass


##


@dc.dataclass(frozen=True)
class Ec2Server(Server, AwsResource):
    id: str
    region: str


def get_ec2_servers() -> list[Ec2Server]:
    cfg = _get_secrets()
    import boto3
    session = boto3.Session(
        aws_access_key_id=cfg.get('aws_access_key_id').reveal(),
        aws_secret_access_key=cfg.get('aws_secret_access_key').reveal(),
        region_name=cfg.get('aws_region').reveal(),
    )
    ec2 = session.client('ec2')
    resp = ec2.describe_instances()
    out: list[Ec2Server] = []
    for res in resp.get('Reservations', []):
        for inst in res.get('Instances', []):
            out.append(Ec2Server(
                host=inst['PublicIpAddress'],
                id=inst['InstanceId'],
                region=ec2.meta.region_name,
            ))
    return out


##


@dc.dataclass(frozen=True)
class RdsInstance(DbInstance, AwsResource):
    id: str
    region: str
    engine: str


def get_rds_instances() -> list[RdsInstance]:
    cfg = _get_secrets()
    import boto3
    session = boto3.Session(
        aws_access_key_id=cfg.get('aws_access_key_id').reveal(),
        aws_secret_access_key=cfg.get('aws_secret_access_key').reveal(),
        region_name=cfg.get('aws_region').reveal(),
    )
    rds = session.client('rds')
    resp = rds.describe_db_instances()
    out: list[RdsInstance] = []
    for inst in resp.get('DBInstances', []):
        out.append(RdsInstance(
            host=inst['Endpoint']['Address'],
            port=inst['Endpoint']['Port'],
            id=inst['DBInstanceIdentifier'],
            region=rds.meta.region_name,
            engine=inst['Engine'],
        ))
    return out


##


@dc.dataclass(frozen=True)
class GcpServer(Server):
    id: str
    zone: str


def get_gcp_servers() -> list[GcpServer]:
    cfg = _get_secrets()
    creds = cfg.try_get('gcp_oauth2').reveal()

    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_info(json.loads(creds))

    from google.cloud import compute_v1
    instance_client = compute_v1.InstancesClient(credentials=credentials)
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = cfg.get('gcp_project_id').reveal()
    request.max_results = 50

    out: list[GcpServer] = []
    for zone, response in instance_client.aggregated_list(request=request):
        for instance in (response.instances or []):
            ip = check.single([ac.nat_i_p for ni in instance.network_interfaces for ac in ni.access_configs if ac.nat_i_p])  # noqa
            out.append(GcpServer(
                host=ip,
                id=instance.name,
                zone=zone,
            ))

    return out


##


@dc.dataclass(frozen=True)
class RunpodServer(Server):
    id: str


def get_runpod_servers() -> list[RunpodServer]:
    api_key = _get_secrets().get('runpod_api_key').reveal()
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
    api_key = _get_secrets().get('lambda_labs_api_key').reveal()
    resp = urllib3.request(
        'GET',
        'https://cloud.lambdalabs.com/api/v1/instances',
        headers=urllib3.make_headers(
            basic_auth=f'{api_key}:',
        ),
    )
    insts = json.loads(resp.data.decode('utf-8')).get('data', {})
    out: list[LambdaLabsServer] = []
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
    api_key = _get_secrets().get('digital_ocean_api_key').reveal()
    resp = urllib3.request(
        'GET',
        'https://api.digitalocean.com/v2/droplets',
        headers={
            'Authorization': f'Bearer {api_key}',
        },
    )
    droplets = json.loads(resp.data.decode('utf-8')).get('droplets', [])
    out: list[DigitalOceanServer] = []
    for droplet in droplets:
        net = check.single([n for n in droplet['networks']['v4'] if n['type'] == 'public'])
        out.append(DigitalOceanServer(
            host=net['ip_address'],
            id=droplet['id'],
        ))
    return out


##


def _main() -> None:
    rsrcs: list[Resource] = [
        *get_ec2_servers(),
        *get_rds_instances(),
        *get_gcp_servers(),
        *get_runpod_servers(),
        *get_lambda_labs_servers(),
        *get_digital_ocean_servers(),
    ]

    pprint.pprint(rsrcs)


if __name__ == '__main__':
    _main()
