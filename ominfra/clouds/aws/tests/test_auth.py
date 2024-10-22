import datetime

from .. import auth


def test_auth():
    creds = auth.AwsSigner.Credentials(
        'BARFBARFBARFBARFBARF',
        'BARFBARFBARFBARFBARFBARFBARFBARFBARFBARF',
    )

    region_name = 'us-west-1'
    utcnow = datetime.datetime.strptime('20240827T194946Z', auth.AwsSigner.ISO8601)  # noqa

    user_agent = 'Botocore/1.35.6 ua/2.0 os/macos#21.6.0 md/arch#arm64 lang/python#3.12.5 md/pyimpl#CPython'

    sh = auth.V4AwsSigner(
        creds,
        region_name,
        'ec2',
    ).sign(
        auth.AwsSigner.Request(
            method='POST',
            url=f'https://ec2.{region_name}.amazonaws.com/',
            headers={
                'user-agent': [user_agent],
            },
            payload=b'&'.join([
                b'Action=DescribeInstances',
                b'Version=2016-11-15',
                b'Filter.1.Name=instance-state-name',
                b'Filter.1.Value.1=running',
            ]),
        ),
        utcnow=utcnow,
    )

    assert sh == {
        'Authorization': [(
            'AWS4-HMAC-SHA256 '
            'Credential=BARFBARFBARFBARFBARF/20240827/us-west-1/ec2/aws4_request, '
            'SignedHeaders=host;x-amz-date, '
            'Signature=8dbfbb53ea6dc918ad7a17d9a3a85f8430e78a0adba67f0d4d0f9bf5daf59960'
        )],
        'X-Amz-Date': ['20240827T194946Z'],
    }

    sh = auth.V4AwsSigner(
        creds,
        region_name,
        's3',
    ).sign(
        auth.AwsSigner.Request(
            method='GET',
            url=f'https://s3.{region_name}.amazonaws.com/?max-buckets=123',
            headers={
                'user-agent': [user_agent],
            },
        ),
        sign_payload=True,
        utcnow=utcnow,
    )

    assert sh == {
        'Authorization': [(
            'AWS4-HMAC-SHA256 '
            'Credential=BARFBARFBARFBARFBARF/20240827/us-west-1/s3/aws4_request, '
            'SignedHeaders=host;x-amz-content-sha256;x-amz-date, '
            'Signature=51a4af49085e1b78e4d018736bb32b222f5125f62932445f410c3866f68c6f1c'
        )],
        'X-Amz-Date': ['20240827T194946Z'],
        'X-Amz-Content-SHA256': ['e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'],
    }
