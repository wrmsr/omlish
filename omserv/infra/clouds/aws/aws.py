"""
aws \
    --region us-east-1 \
    pricing get-products \
    --service-code AmazonEC2 \
    --filters \
        "Type=TERM_MATCH,Field=instanceType,Value=m5.xlarge" \
        "Type=TERM_MATCH,Field=regionCode,Value=us-east-1" \
    | jq -C '.PriceList[] | fromjson' | less -R
"""
import boto3


def _main() -> None:
    ec2 = boto3.client('ec2')
    insts = ec2.describe_instances()
    print(insts)

    pri = boto3.client('pricing')
    pl = pri.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            dict(Type='TERM_MATCH', Field='regionCode', Value='us-east-1'),
            dict(Type='TERM_MATCH', Field='instanceType', Value='m5.xlarge'),
        ],
    )
    print(pl)


if __name__ == '__main__':
    _main()
