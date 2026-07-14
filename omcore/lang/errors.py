class DuplicateKeyError(Exception):
    """*Not* a `KeyError`, as that conventionally means 'not present', whereas this means 'already present'."""
