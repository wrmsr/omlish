# ruff: noqa: UP007
import dataclasses as dc
import grp
import pwd


##


def name_to_uid(name: str) -> int:
    try:
        uid = int(name)
    except ValueError:
        try:
            pwdrec = pwd.getpwnam(name)
        except KeyError:
            raise ValueError(f'Invalid user name {name}')  # noqa
        uid = pwdrec[2]
    else:
        try:
            pwd.getpwuid(uid)  # check if uid is valid
        except KeyError:
            raise ValueError(f'Invalid user id {name}')  # noqa
    return uid


def name_to_gid(name: str) -> int:
    try:
        gid = int(name)
    except ValueError:
        try:
            grprec = grp.getgrnam(name)
        except KeyError:
            raise ValueError(f'Invalid group name {name}')  # noqa
        gid = grprec[2]
    else:
        try:
            grp.getgrgid(gid)  # check if gid is valid
        except KeyError:
            raise ValueError(f'Invalid group id {name}')  # noqa
    return gid


def gid_for_uid(uid: int) -> int:
    pwrec = pwd.getpwuid(uid)
    return pwrec[3]


##


@dc.dataclass(frozen=True)
class User:
    name: str
    uid: int
    gid: int


def get_user(name: str) -> User:
    return User(
        name=name,
        uid=(uid := name_to_uid(name)),
        gid=gid_for_uid(uid),
    )
