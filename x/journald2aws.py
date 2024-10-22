import dataclasses as dc
import time

import httpx

from omdev.secrets import load_secrets
from ominfra.clouds.aws import auth
from omlish.formats import json


def _main() -> None:
    secrets = load_secrets()

    payload = {
        "logGroupName": "omlish",
        "logStreamName": "test",
        "logEvents": [
            {"timestamp": int(time.time() * 1000.), "message": "Test log message 2"},
        ],
    }
    body = json.dumps_compact(payload).encode('utf-8')

    amz_target = 'Logs_20140328.PutLogEvents'
    url = 'https://logs.us-west-1.amazonaws.com/'

    creds = auth.Credentials(
        secrets.get('aws_access_key_id').reveal(),
        secrets.get('aws_secret_access_key').reveal(),

    )

    region_name = 'us-west-1'

    #

    req = auth.Request(
        method='POST',
        url=url,
        headers={
            'User-Agent': ['Botocore/1.35.6 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.12.5 md/pyimpl#CPython'],
            'Content-Type': ['application/x-amz-json-1.1'],
            'X-Amz-Target': [amz_target],
        },
        payload=body,
    )

    #

    sign_hdrs = auth.V4AwsSigner(creds, region_name, 'logs').sign(req, sign_payload=False)
    req = dc.replace(req, headers={**req.headers, **sign_hdrs})

    resp = httpx.post(
        req.url,
        headers=[(k, v) for k, vs in req.headers.items() for v in vs],
        follow_redirects=True,
    )

    print((resp, resp.content))


if __name__ == '__main__':
    _main()
