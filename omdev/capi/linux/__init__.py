import sys


if getattr(sys, 'platform') != 'linux':
    raise OSError(sys.platform)
