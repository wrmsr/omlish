import os.path
import typing as ta

from omlish import lang
from omlish.secrets import all as sec


if ta.TYPE_CHECKING:
    import yaml
else:
    yaml = lang.proxy_import('yaml')


SECRETS_FILE = os.getenv('SECRETS_FILE', '~/.omlish/secrets.yml')


def load_secrets() -> sec.Secrets:
    dct: dict[str, sec.Secret] = {}
    with open(os.path.expanduser(SECRETS_FILE)) as f:
        for k, v in yaml.safe_load(f).items():
            if isinstance(v, str):
                dct[k] = sec.Secret(key=k, value=v)
    return sec.MappingSecrets(dct)
