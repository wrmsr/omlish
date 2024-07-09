"""
TODO:
 - https://github.com/python-versioneer/python-versioneer

git describe --match=NeVeRmAtCh --always --abbrev=40 --dirty > "$(DIST_BUILD_DIR)/$(PROJECT)/.revision"
"""
import errno
import typing as ta

import pkg_resources


def get_revision() -> ta.Optional[str]:
    global __revision__  # noqa
    try:
        return __revision__
    except NameError:
        pass
    try:
        __revision__ = pkg_resources.resource_string(__package__, '.revision').decode('utf-8').strip()
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        __revision__ = None
    return __revision__


if __name__ == '__main__':
    revision = get_revision()
    if revision is not None:
        print(revision)
        exit(0)
    else:
        exit(1)
