"""Utility functions for manipulating directories and directory trees."""
import errno
import os

from omlish.logs import all as logs

from .errors import DistutilsFileError
from .errors import DistutilsInternalError


log = logs.get_module_logger(globals())


##


# cache for by mkpath() -- in addition to cheapening redundant calls, eliminates redundant "creating /foo/bar/baz"
# messages in dry-run mode
_path_created: dict[str, int] = {}


def mkpath(name, mode=0o777, verbose=1, dry_run=False) -> list[str]:  # noqa: C901
    """Create a directory and any missing ancestor directories.

    If the directory already exists (or if 'name' is the empty string, which means the current directory, which of
    course exists), then do nothing. Raise DistutilsFileError if unable to create some directory along the way (eg. some
    sub-path exists, but is a file rather than a directory). If 'verbose' is true, print a one-line summary of each
    mkdir to stdout. Return the list of directories actually created.

    os.makedirs is not used because:

    a) It's new to Python 1.5.2, and
    b) it blows up if the directory already exists (in which case it should silently succeed).
    """

    # Detect a common bug -- name is None
    if not isinstance(name, str):
        raise DistutilsInternalError(f"mkpath: 'name' must be a string (got {name!r})")

    # what's the better way to handle verbosity? print as we create each directory in the path (the current behaviour),
    # or only announce the creation of the whole path? (quite easy to do the latter since we're not using a recursive
    # algorithm)

    name = os.path.normpath(name)
    created_dirs: list[str] = []
    if os.path.isdir(name) or name == '':
        return created_dirs
    if _path_created.get(os.path.abspath(name)):
        return created_dirs

    (head, tail) = os.path.split(name)
    tails = [tail]  # stack of lone dirs to create

    while head and tail and not os.path.isdir(head):
        (head, tail) = os.path.split(head)
        tails.insert(0, tail)  # push next higher dir onto stack

    # now 'head' contains the deepest directory that already exists (that is, the child of 'head' in 'name' is the
    # highest directory that does *not* exist)
    for d in tails:
        # print "head = %s, d = %s: " % (head, d),
        head = os.path.join(head, d)
        abs_head = os.path.abspath(head)

        if _path_created.get(abs_head):
            continue

        if verbose >= 1:
            log.info('creating %s', head)

        if not dry_run:
            try:
                os.mkdir(head, mode)
            except OSError as exc:
                if not (exc.errno == errno.EEXIST and os.path.isdir(head)):
                    raise DistutilsFileError(f"could not create '{head}': {exc.args[-1]}") from None
            created_dirs.append(head)

        _path_created[abs_head] = 1
    return created_dirs
