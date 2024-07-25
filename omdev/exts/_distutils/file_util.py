"""Utility functions for operating on single files."""
import contextlib
import logging
import os

from .errors import DistutilsFileError


log = logging.getLogger(__name__)


# for generating verbose output in 'copy_file()'
_copy_action = {None: 'copying', 'hard': 'hard linking', 'sym': 'symbolically linking'}


def _copy_file_contents(src, dst, buffer_size=16 * 1024):  # noqa: C901
    """
    Copy the file 'src' to 'dst'; both must be filenames.  Any error opening either file, reading from 'src', or writing
    to 'dst', raises DistutilsFileError.  Data is read/written in chunks of 'buffer_size' bytes (default 16k).  No
    attempt is made to handle anything apart from regular files.
    """
    # Stolen from shutil module in the standard library, but with custom error-handling added.
    fsrc = None
    fdst = None
    try:
        try:
            fsrc = open(src, 'rb')  # noqa
        except OSError as e:
            raise DistutilsFileError(f"could not open '{src}': {e.strerror}") from None

        if os.path.exists(dst):
            try:
                os.unlink(dst)
            except OSError as e:
                raise DistutilsFileError(f"could not delete '{dst}': {e.strerror}") from None

        try:
            fdst = open(dst, 'wb')  # noqa
        except OSError as e:
            raise DistutilsFileError(f"could not create '{dst}': {e.strerror}") from None

        while True:
            try:
                buf = fsrc.read(buffer_size)
            except OSError as e:
                raise DistutilsFileError(f"could not read from '{src}': {e.strerror}") from None

            if not buf:
                break

            try:
                fdst.write(buf)
            except OSError as e:
                raise DistutilsFileError(f"could not write to '{dst}': {e.strerror}") from None

    finally:
        if fdst:
            fdst.close()
        if fsrc:
            fsrc.close()


def copy_file(  # noqa: C901
        src,
        dst,
        preserve_mode=1,
        preserve_times=1,
        update=0,
        link=None,
        verbose=1,
        dry_run=False,
):
    """
    Copy a file 'src' to 'dst'.  If 'dst' is a directory, then 'src' is copied there with the same name; otherwise, it
    must be a filename.  (If the file exists, it will be ruthlessly clobbered.)  If 'preserve_mode' is true (the
    default), the file's mode (type and permission bits, or whatever is analogous on the current platform) is copied.
    If 'preserve_times' is true (the default), the last-modified and last-access times are copied as well.  If 'update'
    is true, 'src' will only be copied if 'dst' does not exist, or if 'dst' does exist but is older than 'src'.

    'link' allows you to make hard links (os.link) or symbolic links (os.symlink) instead of copying: set it to "hard"
    or "sym"; if it is None (the default), files are copied.  Don't set 'link' on systems that don't support it:
    'copy_file()' doesn't check if hard or symbolic linking is available. If hardlink fails, falls back to
    _copy_file_contents().

    Under Mac OS, uses the native file copy function in macostools; on other systems, uses '_copy_file_contents()' to
    copy file contents.

    Return a tuple (dest_name, copied): 'dest_name' is the actual name of the output file, and 'copied' is true if the
    file was copied (or would have been copied, if 'dry_run' true).
    """
    # if the destination file already exists, we clobber it if copying, but blow up if linking.  Hmmm.  And I don't know
    # what macostools.copyfile() does.  Should definitely be consistent, and should probably blow up if destination
    # exists and we would be changing it (ie. it's not already a hard/soft link to src OR (not update) and (src newer
    # than dst).
    from stat import S_IMODE
    from stat import ST_ATIME
    from stat import ST_MODE
    from stat import ST_MTIME

    from .modified import newer

    if not os.path.isfile(src):
        raise DistutilsFileError(f"can't copy '{src}': doesn't exist or not a regular file")

    if os.path.isdir(dst):
        dir = dst  # noqa
        dst = os.path.join(dst, os.path.basename(src))
    else:
        dir = os.path.dirname(dst)  # noqa

    if update and not newer(src, dst):
        if verbose >= 1:
            log.debug('not copying %s (output up-to-date)', src)
        return (dst, 0)

    try:
        action = _copy_action[link]
    except KeyError:
        raise ValueError(f"invalid value '{link}' for 'link' argument") from None

    if verbose >= 1:
        if os.path.basename(dst) == os.path.basename(src):
            log.info('%s %s -> %s', action, src, dir)
        else:
            log.info('%s %s -> %s', action, src, dst)

    if dry_run:
        return (dst, 1)

    # If linking (hard or symbolic), use the appropriate system call (Unix only, of course, but that's the caller's
    # responsibility)
    elif link == 'hard':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            try:
                os.link(src, dst)
            except OSError:
                # If hard linking fails, fall back on copying file (some special filesystems don't support hard linking
                # even under Unix, see issue #8876).
                pass
            else:
                return (dst, 1)
    elif link == 'sym':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            os.symlink(src, dst)
            return (dst, 1)

    # Otherwise (non-Mac, not linking), copy the file contents and (optionally) copy the times and mode.
    _copy_file_contents(src, dst)
    if preserve_mode or preserve_times:
        st = os.stat(src)

        # According to David Ascher <da@ski.org>, utime() should be done before chmod() (at least under NT).
        if preserve_times:
            os.utime(dst, (st[ST_ATIME], st[ST_MTIME]))
        if preserve_mode:
            os.chmod(dst, S_IMODE(st[ST_MODE]))

    return (dst, 1)


# I suspect this is Unix-specific -- need porting help!
def move_file(src, dst, verbose=1, dry_run=False):  # noqa: C901
    """
    Move a file 'src' to 'dst'.  If 'dst' is a directory, the file will be moved into it with the same name; otherwise,
    'src' is just renamed to 'dst'.  Return the new full name of the file.

    Handles cross-device moves on Unix using 'copy_file()'.  What about other systems???
    """
    import errno
    from os.path import basename
    from os.path import dirname
    from os.path import exists
    from os.path import isdir
    from os.path import isfile

    if verbose >= 1:
        log.info('moving %s -> %s', src, dst)

    if dry_run:
        return dst

    if not isfile(src):
        raise DistutilsFileError(f"can't move '{src}': not a regular file")

    if isdir(dst):
        dst = os.path.join(dst, basename(src))
    elif exists(dst):
        raise DistutilsFileError(f"can't move '{src}': destination '{dst}' already exists")

    if not isdir(dirname(dst)):
        raise DistutilsFileError(f"can't move '{src}': destination '{dst}' not a valid path")

    copy_it = False
    try:
        os.rename(src, dst)
    except OSError as e:
        (num, msg) = e.args
        if num == errno.EXDEV:
            copy_it = True
        else:
            raise DistutilsFileError(f"couldn't move '{src}' to '{dst}': {msg}") from None

    if copy_it:
        copy_file(src, dst, verbose=verbose)
        try:
            os.unlink(src)
        except OSError as e:
            (num, msg) = e.args
            with contextlib.suppress(OSError):
                os.unlink(dst)
            raise DistutilsFileError(
                f"couldn't move '{src}' to '{dst}' by copy/delete: "
                f"delete '{src}' failed: {msg}",
            ) from None

    return dst
