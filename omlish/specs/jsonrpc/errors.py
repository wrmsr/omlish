from ... import dataclasses as dc
from ... import lang


##


@dc.dataclass(frozen=True)
class KnownError:
    code: int
    message: str
    meaning: str


class KnownErrors(lang.Namespace):
    PARSE_ERROR = KnownError(-32700, 'Parse error', 'Invalid JSON was received by the server.')
    INVALID_REQUEST = KnownError(-32600, 'Invalid Request', 'The JSON sent is not a valid Request object.')
    METHOD_NOT_FOUND = KnownError(-32601, 'Method not found', 'The method does not exist / is not available.')
    INVALID_PARAMS = KnownError(-32602, 'Invalid params', 'Invalid method parameter(s).')
    INTERNAL_ERROR = KnownError(-32603, 'Internal error', 'Internal JSON-RPC error.')


CUSTOM_ERROR_BASE = -32000
