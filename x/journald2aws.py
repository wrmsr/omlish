import dataclasses as dc
import time

import httpx

from omdev.secrets import load_secrets
from ominfra.clouds.aws.auth import V4AwsSigner
from ominfra.clouds.aws.logs import AwsLogEvent
from ominfra.clouds.aws.logs import AwsPutLogEventsRequest
from ominfra.clouds.aws.logs import AwsPutLogEventsResponse
from omlish.formats import json


##


def _main() -> None:
    secrets = load_secrets()

    payload = AwsPutLogEventsRequest(
        log_group_name='omlish',
        log_stream_name='test',
        log_events=[
            AwsLogEvent(
                timestamp=int(time.time() * 1000.),
                message=f'Test log message {time.time()}',
            ),
        ],
    )

    body = json.dumps_compact(payload.to_aws()).encode('utf-8')

    amz_target = 'Logs_20140328.PutLogEvents'
    url = 'https://logs.us-west-1.amazonaws.com/'

    creds = V4AwsSigner.Credentials(
        secrets.get('aws_access_key_id').reveal(),
        secrets.get('aws_secret_access_key').reveal(),

    )

    region_name = 'us-west-1'

    #

    req = V4AwsSigner.Request(
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

    sign_hdrs = V4AwsSigner(creds, region_name, 'logs').sign(req, sign_payload=False)
    req = dc.replace(req, headers={**req.headers, **sign_hdrs})

    resp = httpx.post(
        req.url,
        headers=[(k, v) for k, vs in req.headers.items() for v in vs],
        follow_redirects=True,
        content=req.payload,
    )

    print((resp, resp.content))

    response = AwsPutLogEventsResponse.from_aws(resp.json())
    print(response)


if __name__ == '__main__':
    _main()
