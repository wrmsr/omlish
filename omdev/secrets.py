import os.path

import yaml

from omlish import secrets as sec


SECRETS_FILE = os.getenv('SECRETS_FILE', '~/Dropbox/.dotfiles/secrets.yml')


def load_secrets() -> sec.Secrets:
    dct: dict[str, sec.Secret] = {}
    with open(os.path.expanduser(SECRETS_FILE)) as f:
        for k, v in yaml.safe_load(f).items():
            if isinstance(v, str):
                dct[k] = sec.Secret(key=k, value=v)
    return sec.MappingSecrets(dct)
