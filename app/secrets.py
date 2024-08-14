import logging
import os

from omlish import inject as inj
from omlish import secrets as sec
from omserv.dbs import get_db_url


log = logging.getLogger(__name__)


def bind_secrets() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(sec.Secrets, to_fn=lambda: sec.LoggingSecrets(sec.SimpleSecrets({
            'session_secret_key': 'secret-key-goes-here',  # noqa
            'db_url': get_db_url(),

            'sd_auth_token': os.environ.get('SD_AUTH_TOKEN', ''),
            'sd2_url': os.environ.get('SD2_URL', ''),
        }))),
    )
