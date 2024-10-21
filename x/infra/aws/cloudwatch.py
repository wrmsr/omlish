import boto3
import datetime

from omdev.secrets import load_secrets


def _main() -> None:
    secrets = load_secrets()

    # Initialize a session using Amazon CloudWatch
    cloudwatch = boto3.client(
        'logs',
        aws_access_key_id=secrets.get('aws_access_key_id').reveal(),
        aws_secret_access_key=secrets.get('aws_secret_access_key').reveal(),
        region_name=secrets.get('aws_region').reveal(),
    )

    # The name of the log group
    log_group_name = 'omlish'

    # The name of the log stream
    log_stream_name = 'test'

    # Message to be sent to CloudWatch
    message = 'Test log message'

    # Get the current timestamp
    timestamp = int(datetime.datetime.now().timestamp() * 1000)

    # Put log events in CloudWatch
    response = cloudwatch.put_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        logEvents=[
            {
                'timestamp': timestamp,
                'message': message
            },
        ],
    )

    print('Log sent to CloudWatch:', response)


if __name__ == '__main__':
    _main()
