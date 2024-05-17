import configparser
import io
import os.path
import uuid

import boto3
import botocore.model
import botocore.session


"""
context = {
    'auth_type': None,
    'client_config': <botocore.config.Config object at 0x14f356390>,
    'client_region': 'us-west-1',
    'has_streaming_input': False,
    'retries': {
        'attempt': 1,
        'invocation-id': str(uuid.uuid4()),
    },
    'timestamp': '20240515T212015Z',
}
data = {
    'Action': 'DescribeInstances',
    'Filter.1.Name': 'instance-state-name',
    'Filter.1.Value.1': 'running',
    'Version': '2016-11-15',
}

Config:
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

    context = {
        'auth_type': None,
        'client_region': 'us-west-1',
        'has_streaming_input': False,
        'retries': {
            'attempt': 1,
            'invocation-id': str(uuid.uuid4()),
        },
        'timestamp': '20240515T212015Z',
    }
    data = {
        'Action': 'DescribeInstances',
        'Filter.1.Name': 'instance-state-name',
        'Filter.1.Value.1': 'running',
        'Version': '2016-11-15',
    }

    body = b'Action=DescribeInstances&Version=2016-11-15&Filter.1.Name=instance-state-name&Filter.1.Value.1=running'

    from .auth import Request
    from .auth import HttpHeaders

    headers = HttpHeaders()
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
    headers['User-Agent'] = 'Boto3/1.34.106 md/Botocore#1.34.69 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.11.9 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.34.69 Resource'

    request = Request(
        method='POST',
        url='https://ec2.us-west-1.amazonaws.com/',
        headers=headers,
        data=data,
        params={},
        context=context,
        body=body,
    )

    from .auth import RequestSignerV4
    from .auth import Credentials
    signer = RequestSignerV4(
        Credentials(
            access_key=access_key_id,
            secret_key=secret_access_key,
        ),
        service_name=service_name,
        region_name=region_name,
    )

    signer.add_auth(request)

    import urllib.request
    req = urllib.request.Request(
        request.url,
        data=request.body,
        headers=dict(request.headers),
    )

    import urllib.parse
    with urllib.request.urlopen(req) as f:
        print(f.read().decode('utf-8'))


if __name__ == '__main__':
    _main()
