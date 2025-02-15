import datetime
import gzip
import os.path
import typing as ta

from omdev.home.secrets import load_secrets
from omlish import lang
from omlish.argparse import all as ap
from omlish.formats import json
from omlish.secrets import all as sec

from .cache import load_instance_types


if ta.TYPE_CHECKING:
    import boto3
else:
    boto3 = lang.proxy_import('boto3')


# Use a hardcoded gz mtime to prevent the gz file from changing when the contents don't. We still have the git metadata
# to track modifications.
FIXED_CACHE_TIMESTAMP = datetime.datetime(2025, 1, 1, tzinfo=datetime.UTC).timestamp()


@lang.cached_function
def _get_secrets() -> sec.Secrets:
    return load_secrets()


def get_ec2_instance_types(session: boto3.Session) -> dict[str, dict[str, ta.Any]]:
    ec2 = session.client('ec2')
    next_token = None
    dct = {}
    while True:
        resp = ec2.describe_instance_types(**(dict(NextToken=next_token) if next_token else {}))
        for instance_type in resp['InstanceTypes']:
            name = instance_type['InstanceType']
            dct[name] = instance_type
        next_token = resp.get('NextToken')
        if not next_token:
            break
    dct = dict(sorted(dct.items(), key=lambda t: t[0]))
    return dct


class Cli(ap.Cli):
    @ap.cmd()
    def fetch(self) -> None:
        cfg = _get_secrets()

        session = boto3.Session(
            aws_access_key_id=cfg.get('aws_access_key_id').reveal(),
            aws_secret_access_key=cfg.get('aws_secret_access_key').reveal(),
            region_name=cfg.get('aws_region').reveal(),
        )

        instance_types = get_ec2_instance_types(session)

        cache_file = os.path.join(os.path.dirname(__file__), 'cache.json.gz')
        with open(cache_file, 'wb') as f:
            with gzip.GzipFile(
                    fileobj=f,
                    mode='w',
                    mtime=FIXED_CACHE_TIMESTAMP,
            ) as gf:
                gf.write(json.dumps_compact(instance_types).encode('utf-8'))

    @ap.cmd()
    def dump(self) -> None:
        dct = load_instance_types()
        print(json.dumps_pretty(dct))


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
