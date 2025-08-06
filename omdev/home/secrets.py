import os.path
import typing as ta

from omlish import lang
from omlish.os.environ import EnvVar
from omlish.secrets import all as sec

from .paths import get_home_paths


if ta.TYPE_CHECKING:
    import yaml
else:
    yaml = lang.proxy_import('yaml')


##


SECRETS_FILE_ENV_VAR = EnvVar('OMLISH_SECRETS')
DEFAULT_SECRETS_FILE_NAME = 'secrets.yml'


def get_secrets_file() -> str:
    return os.path.expanduser(
        SECRETS_FILE_ENV_VAR.get(lambda: os.path.join(get_home_paths().config_dir, DEFAULT_SECRETS_FILE_NAME)),
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


##


def install_env_secrets(
        *keys: str | tuple[str, str],
        secrets: sec.Secrets | None = None,
        environ: ta.MutableMapping[str, str] | None = None,
        non_strict: bool = False,
) -> None:
    """This should not be used outside of being forced to interact with external code."""

    if not keys:
        raise ValueError('Must specify keys')

    sk_ek_tups: list[tuple[str, str]] = []
    for k in keys:
        if isinstance(k, tuple):
            sk, ek = k

        elif isinstance(k, str):
            if k.lower() == k:
                sk, ek = k, k.upper()
            elif k.upper() == k:
                sk, ek = k.lower(), k
            else:
                raise ValueError(k)

        else:
            raise TypeError(k)

        sk_ek_tups.append((sk, ek))

    if secrets is None:
        secrets = load_secrets()

    if environ is None:
        environ = os.environ

    for sk, ek in sk_ek_tups:
        try:
            sv = secrets.get(sk)
        except KeyError:
            if non_strict:
                continue
            raise

        environ[ek] = sv.reveal()
