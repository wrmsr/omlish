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

    ##

    """
    result = {Config} <botocore.config.Config object at 0x144977610>
 NON_LEGACY_OPTION_DEFAULTS = {dict: 1} {'connect_timeout': None}
 OPTION_DEFAULTS = {OrderedDict: 24} OrderedDict([('region_name', None), ('signature_version', None), ('user_agent', None), ('user_agent_extra', None), ('user_agen..., None), ('request_min_compression_size_bytes', None), ('disable_request_compression', None), ('client_context_params', None)])
 client_cert = {NoneType} None
 client_context_params = {NoneType} None
 connect_timeout = {int} 60
 defaults_mode = {NoneType} None
 disable_request_compression = {bool} False
 endpoint_discovery_enabled = {NoneType} None
 ignore_configured_endpoint_urls = {NoneType} None
 inject_host_prefix = {bool} True
 max_pool_connections = {int} 10
 parameter_validation = {bool} True
 proxies = {NoneType} None
 proxies_config = {NoneType} None
 read_timeout = {int} 60
 region_name = {str} 'us-west-1'
 request_min_compression_size_bytes = {int} 10240
 retries = {dict: 1} {'mode': 'legacy'}
 s3 = {NoneType} None
 signature_version = {str} 'v4'
 tcp_keepalive = {NoneType} None
 use_dualstack_endpoint = {NoneType} None
 use_fips_endpoint = {NoneType} None
 user_agent = {str} 'Botocore/1.34.69 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.11.9 md/pyimpl#CPython'
 user_agent_appid = {NoneType} None
 user_agent_extra = {NoneType} None
    """

    """
    {
        'auth_type': None,
        'client_config': <botocore.config.Config object at 0x144977610 >,
        'client_region': 'us-west-1',
        'has_streaming_input': False,
    }
    
    {'Filters': [{'Name': 'instance-state-name', 'Values': ['running']}]}
    
    endpoint_url = 'https://ec2.us-west-1.amazonaws.com'
    additional_headers = {}
    properties = {}
    
    request_dict = {
        'url_path': '/',
        'query_string': '',
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'User-Agent': 'Botocore/1.34.69 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.11.9 md/pyimpl#CPython cfg/retry-mode#legacy',
        },
        'body': {
            'Action': 'DescribeInstances',
            'Version': '2016-11-15',
            'Filter.1.Name': 'instance-state-name',
            'Filter.1.Value.1': 'running',
        },
        'url': 'https://ec2.us-west-1.amazonaws.com/',
        'context': {
            'client_region': 'us-west-1',
            'client_config': <botocore.config.Config object at 0x144977610>,
            'has_streaming_input': False,
            'auth_type': None,
        },
    }
    
    service_id = 'ec2'
    """


if __name__ == '__main__':
    _main()
