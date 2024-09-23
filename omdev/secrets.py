import os.path
import typing as ta

import yaml


SECRETS_PATH = os.getenv('SECRETS_PATH', os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml'))


def load_secrets() -> dict[str, ta.Any]:
    with open(SECRETS_PATH) as f:
        return yaml.safe_load(f)
