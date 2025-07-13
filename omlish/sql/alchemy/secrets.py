"""
TODO:
 - sync/async...
"""
from ...secrets import all as sec


##


class SqlFunctionSecrets(sec.Secrets):
    def _get_raw(self, key: str) -> str:
        raise NotImplementedError
