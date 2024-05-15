import configparser
import io
import os.path

import boto3
import botocore.model
import botocore.session


def _main() -> None:
    with open(os.path.expanduser('~/.aws/credentials'), 'r') as f:
        txt = f.read()

    config = configparser.ConfigParser()
    config.read_file(io.StringIO(txt))
    cred_cfg = {k.lower(): v for k, v in config.items('default')}

    session = botocore.session.get_session()
    loader = session.get_component('data_loader')

    service_name = 'ec2'
    region_name = 'us-west-1'
    access_key_id = cred_cfg['aws_access_key_id']
    secret_access_key = cred_cfg['aws_secret_access_key']

    ##

    ec2 = boto3.resource(
        'ec2',
        region_name=region_name,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
    )

    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}],
    )

    for instance in instances:
        print(instance.id, instance.instance_type)

    ##

    session = botocore.session.Session()

    ec2_client = session.create_client(
        'ec2',
        region_name=region_name,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
    )

    response = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}],
    )

    running_instances = [
        instance
        for reservation in response['Reservations']
        for instance in reservation['Instances']
        if instance['State']['Name'] == 'running'
    ]

    for instance in running_instances:
        print(instance['InstanceId'], instance['InstanceType'])


if __name__ == '__main__':
    _main()
