"""
TODO:
 - sync/async...
"""
from ... import secrets as sec


class SqlFunctionSecrets(sec.Secrets):
    def _get_raw(self, key: str) -> str:
        raise NotImplementedError
