import time

from omserv.secrets import load_secrets


def _main():
    cfg = load_secrets()
    import boto3
    session = boto3.Session(
        aws_access_key_id=cfg['aws_access_key_id'],
        aws_secret_access_key=cfg['aws_secret_access_key'],
        region_name=cfg['aws_region'],
    )
    client = session.client('logs')
    response = client.put_log_events(
        logGroupName='omlish',
        logStreamName='test',
        logEvents=[
            {
                'timestamp': int(time.time() * 1_000),
                'message': 'hi cloudwatch'
            },
        ],
    )
    print(response)


if __name__ == '__main__':
    _main()
