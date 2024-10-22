import dataclasses as dc
import time

import httpx

from omdev.secrets import load_secrets
from ominfra.clouds.aws.auth import AwsSigner
from ominfra.clouds.aws.logs import AwsPutLogEventsResponse

from .aws import AwsLogMessagePoster


##


@dc.dataclass(frozen=True)
class Journald2AwsConfig:
    log_group_name: str
    log_stream_name: str

    aws_batch_size: int = 1_000
    aws_flush_interval_s: float = 1.


##


def _main() -> None:
    secrets = load_secrets()

    mp = AwsLogMessagePoster(
        log_group_name='omlish',
        log_stream_name='test',
        region_name='us-west-1',
        credentials=AwsSigner.Credentials(
            secrets.get('aws_access_key_id').reveal(),
            secrets.get('aws_secret_access_key').reveal(),
        ),
    )

    [post] = mp.feed([mp.Message(
        message=f'Test log message {time.time()}',
        ts_ms=int(time.time() * 1000.),
    )])

    resp = httpx.post(
        post.url,
        headers=post.headers,
        follow_redirects=True,
        content=post.data,
    )

    print((resp, resp.content))

    response = AwsPutLogEventsResponse.from_aws(resp.json())
    print(response)


if __name__ == '__main__':
    _main()
