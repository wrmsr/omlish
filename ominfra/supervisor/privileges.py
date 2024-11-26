# ruff: noqa: UP006 UP007
import grp
import os
import pwd
import typing as ta


def drop_privileges(user: ta.Union[int, str, None]) -> ta.Optional[str]:
    """
    Drop privileges to become the specified user, which may be a username or uid. Called for supervisord startup and
    when spawning subprocesses. Returns None on success or a string error message if privileges could not be dropped.
    """

    if user is None:
        return 'No user specified to setuid to!'

    # get uid for user, which can be a number or username
    try:
        uid = int(user)
    except ValueError:
        try:
            pwrec = pwd.getpwnam(user)  # type: ignore
        except KeyError:
            return f"Can't find username {user!r}"
        uid = pwrec[2]
    else:
        try:
            pwrec = pwd.getpwuid(uid)
        except KeyError:
            return f"Can't find uid {uid!r}"

    current_uid = os.getuid()

    if current_uid == uid:
        # do nothing and return successfully if the uid is already the current one. this allows a supervisord running as
        # an unprivileged user "foo" to start a process where the config has "user=foo" (same user) in it.
        return None

    if current_uid != 0:
        return "Can't drop privilege as nonroot user"

    gid = pwrec[3]
    if hasattr(os, 'setgroups'):
        user = pwrec[0]
        groups = [grprec[2] for grprec in grp.getgrall() if user in grprec[3]]

        # always put our primary gid first in this list, otherwise we can lose group info since sometimes the first
        # group in the setgroups list gets overwritten on the subsequent setgid call (at least on freebsd 9 with
        # python 2.7 - this will be safe though for all unix /python version combos)
        groups.insert(0, gid)
        try:
            os.setgroups(groups)
        except OSError:
            return 'Could not set groups of effective user'

    try:
        os.setgid(gid)
    except OSError:
        return 'Could not set group id of effective user'

    os.setuid(uid)

    return None
