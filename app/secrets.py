import logging

from omlish import inject as inj
from omlish import secrets as sec
from omserv.dbs import get_db_url


log = logging.getLogger(__name__)


def bind_secrets() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(sec.Secrets, to_const=sec.LoggingSecrets(sec.SimpleSecrets({
            'session_secret_key': 'secret-key-goes-here',  # noqa
            'db_url': get_db_url(),
        }))),
    )
