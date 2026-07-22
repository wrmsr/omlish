import os
import unittest


##


TAG_ENV_VAR_PREFIX = 'OM_UNITTEST_'

SKIP_IF_ENV_VAR_PREFIX = TAG_ENV_VAR_PREFIX + 'SKIP_'


def unittest_mark(tag):
    def outer(fn):
        key = SKIP_IF_ENV_VAR_PREFIX + tag.upper()
        return unittest.skipIf(key in os.environ, tag)(fn)
    return outer
