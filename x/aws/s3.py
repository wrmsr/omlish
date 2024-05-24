import io
import time

import boto3
import botocore.client


def _main():
    # [(host, port)] = harness[DockerManager].get_container_tcp_endpoints([('minio', 9000)]).values()
    #
    # with open(os.path.join(os.path.dirname(__file__), '../../docker/docker-compose.yml'), 'r') as f:
    #     dct = yaml.safe_load(f.read())
    # cfg = {
    #     k: dct['services']['omnibus-minio']['environment']['MINIO_' + k.upper()]
    #     for k in ['access_key', 'secret_key']
    # }

    port = 35226

    s3 = boto3.client(
        's3',
        endpoint_url=f'http://localhost:{port}',
        # aws_access_key_id=cfg['access_key'],
        # aws_secret_access_key=cfg['secret_key'],
        config=botocore.client.Config(signature_version='s3v4'),
        region_name='us-east-1',
    )

    bucket = 'abucket'
    try:
        s3.head_bucket(Bucket=bucket)
    except botocore.client.ClientError:
        s3.create_bucket(Bucket=bucket)

    # s3.put_object(Bucket=bucket, Key='afile', Body=b'hi')

    buf = io.BytesIO()
    buf.write(f'hi: {time.time()}'.encode('utf-8'))
    buf.seek(0)
    s3.upload_fileobj(Fileobj=buf, Bucket=bucket, Key='afile')

    print(s3.get_object(Bucket=bucket, Key='afile')['Body'].read())


if __name__ == '__main__':
    _main()
