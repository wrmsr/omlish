import configparser
import dataclasses as dc
import io
import os.path

import httpx

from .. import auth


def demo_ec2(
        creds: auth.AwsSigner.Credentials,
        region_name: str,
) -> None:
    req = auth.AwsSigner.Request(
        method='POST',
        url=f'https://ec2.{region_name}.amazonaws.com/',
        headers={
            'user-agent': ['Botocore/1.35.6 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.12.5 md/pyimpl#CPython'],
        },
        payload=b'&'.join([
            b'Action=DescribeInstances',
            b'Version=2016-11-15',
            b'Filter.1.Name=instance-state-name',
            b'Filter.1.Value.1=running',
        ]),
    )

    #

    sign_hdrs = auth.V4AwsSigner(creds, region_name, 'ec2').sign(req)
    req = dc.replace(req, headers={**req.headers, **sign_hdrs})

    resp = httpx.post(
        req.url,
        headers=[(k, v) for k, vs in req.headers.items() for v in vs],
        content=req.payload,
        follow_redirects=True,
    )

    print((resp, resp.content))


def demo_s3(
        creds: auth.AwsSigner.Credentials,
        region_name: str,
) -> None:
    req = auth.AwsSigner.Request(
        method='GET',
        url=f'https://s3.{region_name}.amazonaws.com/?max-buckets=123',
        headers={
            'user-agent': ['Botocore/1.35.6 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.12.5 md/pyimpl#CPython'],
        },
    )

    #

    sign_hdrs = auth.V4AwsSigner(creds, region_name, 's3').sign(req, sign_payload=True)
    req = dc.replace(req, headers={**req.headers, **sign_hdrs})

    resp = httpx.get(
        req.url,
        headers=[(k, v) for k, vs in req.headers.items() for v in vs],
        follow_redirects=True,
    )

    print((resp, resp.content))


def _main() -> None:
    with open(os.path.expanduser('~/.aws/credentials')) as f:
        txt = f.read()

    config = configparser.ConfigParser()
    config.read_file(io.StringIO(txt))
    cred_cfg = {k.lower(): v for k, v in config.items('default')}

    region_name = 'us-west-1'
    creds = auth.AwsSigner.Credentials(
        cred_cfg['aws_access_key_id'],
        cred_cfg['aws_secret_access_key'],
    )

    demo_ec2(creds, region_name)
    demo_s3(creds, region_name)


if __name__ == '__main__':
    _main()
