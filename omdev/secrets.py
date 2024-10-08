import os.path

import yaml

from omlish import secrets as sec


SECRETS_PATH = os.getenv('SECRETS_PATH', os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml'))


def load_secrets() -> sec.Secrets:
    dct: dict[str, sec.Secret] = {}
    with open(SECRETS_PATH) as f:
        for k, v in yaml.safe_load(f).items():
            if isinstance(v, str):
                dct[k] = sec.Secret(key=k, value=v)
    return sec.MappingSecrets(dct)
