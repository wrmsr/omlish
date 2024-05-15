import configparser
import io
import os.path

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


if __name__ == '__main__':
    _main()
