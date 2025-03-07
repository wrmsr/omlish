import os.path
import typing as ta

from omlish import lang
from omlish.secrets import all as sec

from .paths import get_home_paths


if ta.TYPE_CHECKING:
    import yaml
else:
    yaml = lang.proxy_import('yaml')


##


SECRETS_FILE_ENV_VAR = 'OMLISH_SECRETS'
DEFAULT_SECRETS_FILE_NAME = 'secrets.yml'


def get_secrets_file() -> str:
    return os.path.expanduser(
        os.getenv(
            SECRETS_FILE_ENV_VAR,
            os.path.join(get_home_paths().config_dir, DEFAULT_SECRETS_FILE_NAME),
        ),
    )


def load_secrets() -> sec.Secrets:
    dct: dict[str, sec.Secret] = {}
    try:
        with open(get_secrets_file()) as f:
            for k, v in yaml.safe_load(f).items():
                if isinstance(v, str):
                    dct[k] = sec.Secret(key=k, value=v)
    except FileNotFoundError:
        pass
    return sec.MappingSecrets(dct)
