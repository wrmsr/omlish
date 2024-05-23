import pprint

from omlish import dataclasses as dc


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


def _main() -> None:
    svrs = get_aws_servers()

    pprint.pprint(svrs)


if __name__ == '__main__':
    _main()