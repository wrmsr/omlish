"""
TODO:
 - sync/async...
"""
from .. import secrets as sec


class SqlFunctionSecrets(sec.Secrets):
    def get(self, key: str) -> str:
        raise NotImplementedError
