import bz2
import os.path
import typing as ta

from omcore import lang
from omcore import marshal as msh
from omcore.argparse import all as ap
from omcore.formats.json import all as json
from omcore.secrets import all as sec
from omdev.home.secrets import load_secrets

from .cache import load_instance_types


if ta.TYPE_CHECKING:
    import boto3
else:
    boto3 = lang.proxy_import('boto3')


##


@lang.cached_function
def _get_secrets() -> sec.Secrets:
    return load_secrets()


##


def fetch_ec2_instance_types(session: boto3.Session) -> dict[str, dict[str, ta.Any]]:
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


##


def sanitize_ec2_instance_types(instance_types: dict[str, dict[str, ta.Any]]) -> None:
    def mask_match(v, p):
        return len(v) == len(p) and all(pe is None or ve == pe for ve, pe in zip(v, p))

    def rec(path: tuple[str | int, ...], obj: dict[str, ta.Any] | list[ta.Any]) -> None:
        if mask_match(path, (None, 'GpuInfo', 'Gpus', None)):
            if wl := obj.get('Workloads'):  # type: ignore[union-attr]
                wl.sort()

        elif isinstance(obj, dict):
            for k, v in obj.items():
                rec((*path, k), v)

        elif isinstance(obj, list):
            for i, c in enumerate(obj):
                rec((*path, i), c)

    rec((), instance_types)


##


class Cli(ap.Cli):
    @ap.cmd()
    def fetch(self) -> None:
        cfg = _get_secrets()

        session = boto3.Session(
            aws_access_key_id=cfg.get('aws_access_key_id').reveal(),
            aws_secret_access_key=cfg.get('aws_secret_access_key').reveal(),
            region_name=cfg.get('aws_region').reveal(),
        )

        instance_types = fetch_ec2_instance_types(session)

        sanitize_ec2_instance_types(instance_types)

        compressed = bz2.compress(json.dumps_compact(instance_types).encode('utf-8'))

        cache_file = os.path.join(os.path.dirname(__file__), 'cache.json.bz2')
        with open(cache_file, 'wb') as f:
            f.write(compressed)

    @ap.cmd(
        ap.arg('-m', '--marshal', action='store_true'),
    )
    def dump(self) -> None:
        dct: ta.Any = load_instance_types()

        if self.args.marshal:
            from ..models.services.ec2 import InstanceTypeInfo

            val = msh.unmarshal(dct, dict[str, InstanceTypeInfo])

            dct = msh.marshal(val)

        print(json.dumps_pretty(dct))


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
