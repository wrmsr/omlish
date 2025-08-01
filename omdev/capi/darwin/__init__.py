import sys


if getattr(sys, 'platform') != 'darwin':
    raise OSError(sys.platform)
