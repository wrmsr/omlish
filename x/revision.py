"""
TODO:
 - https://github.com/python-versioneer/python-versioneer

git describe --match=NeVeRmAtCh --always --abbrev=40 --dirty > "$(DIST_BUILD_DIR)/$(PROJECT)/.revision"
"""
import errno
import importlib.resources
import typing as ta


def get_revision() -> ta.Optional[str]:
    global __revision__  # noqa
    try:
        return __revision__
    except NameError:
        pass
    try:
        __revision__ = importlib.resources.files(__package__).joinpath('.revision').read_text().strip()
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
