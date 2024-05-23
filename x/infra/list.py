import json
import pprint
import typing as ta
import urllib3

from omlish import dataclasses as dc
from omlish import check
from omlish import lang
from omserv.secrets import load_secrets


@lang.cached_nullary
def _get_secrets() -> dict[str, ta.Any]:
    return load_secrets()


@dc.dataclass(frozen=True)
class Server:
    host: str


@dc.dataclass(frozen=True)
class AwsServer(Server):
    id: str
    region: str


def get_aws_servers() -> list[Server]:
    import boto3
    ec2 = boto3.client('ec2')
    resp = ec2.describe_instances()
    lst = []
    for res in resp.get('Reservations', []):
        for inst in res.get('Instances', []):
            lst.append(AwsServer(
                host=inst['PublicIpAddress'],
                id=inst['InstanceId'],
                region=ec2.meta.region_name,
            ))
    return lst


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
    lst = []
    for pod in dct.get('pods', []):
        ssh = check.single([p for p in pod['runtime']['ports'] if p['isIpPublic'] and p['privatePort'] == 22])
        lst.append(RunpodServer(
            host=f'{ssh["ip"]}:{ssh["publicPort"]}',
            id=pod['id'],
        ))
    return lst


def _main() -> None:
    svrs = [
        *get_aws_servers(),
        *get_runpod_servers(),
    ]

    pprint.pprint(svrs)


if __name__ == '__main__':
    _main()
