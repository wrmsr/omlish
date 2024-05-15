import configparser
import io
import os.path

import botocore.model
import botocore.session


def _main():
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

    json_model = loader.load_service_model(service_name, 'service-2')
    service_model = botocore.model.ServiceModel(json_model, service_name=service_name)

    for shape_name in service_model.shape_names:
        shape = service_model.shape_for(shape_name)
        print((shape_name, shape))

    for operation_name in service_model.operation_names:
        operation_model = service_model.operation_model(operation_name)
        print((operation_name, operation_model))

    request_dict = {
        'url_path': '/',
        'query_string': '',
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'User-Agent': 'Boto3/1.17.3 Python/3.7.9 Darwin/18.7.0 Botocore/1.20.3',
        },
        'body': {
            'Action': 'DescribeInstances',
            'Version': '2016-11-15',
        },
        'url': 'https://ec2.us-west-1.amazonaws.com/',
        'context': {
            'client_region': 'us-west-1',
            'client_config': None,
            'has_streaming_input': False,
            'auth_type': None,
        },
    }

    url = 'https://ec2.us-west-1.amazonaws.com/'
    method = 'POST'
    body = 'Action=DescribeInstances&Version=2016-11-15'
    headers = {
        'Content-Type': b'application/x-www-form-urlencoded; charset=utf-8',
        'User-Agent': b'Boto3/1.17.3 Python/3.7.9 Darwin/18.7.0 Botocore/1.20.3',
        'X-Amz-Date': b'20210218T095416Z',
        'Authorization': b'AWS4-HMAC-SHA256 Credential=' + access_key_id.encode('utf-8') + b'/20210218/us-west-1/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=...',
        'Content-Length': '43',
    }

    string_to_sign = """AWS4-HMAC-SHA256
20210218T100326Z
20210218/us-west-1/ec2/aws4_request
6290cb3a8b3b62508f80bcb9df7a46645afe85e9358160cfbb2755784e54445e"""

    def sign(key, msg, hex=False):
        import hmac
        import hashlib
        sig = hmac.new(key, msg.encode('utf-8'), hashlib.sha256)
        return sig.hexdigest() if hex else sig.digest()

    k_date = sign(('AWS4' + secret_access_key).encode('utf-8'), request.context['timestamp'][0:8])
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'aws4_request')
    auth = sign(k_signing, string_to_sign, hex=True)


if __name__ == '__main__':
    _main()
