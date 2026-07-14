"""
See:
- https://stackoverflow.com/a/75903610
- https://newosxbook.com/bonus/vol1ch16.html
"""
import ctypes as ct
import dataclasses as dc
import errno
import socket
import struct
import sys
import typing as ta

from .. import lang


##


@dc.dataclass(frozen=True)
class PeerCred:
    pid: int | None = None
    uid: int | None = None
    gid: int | None = None

    def __repr__(self) -> str:
        return ''.join([
            f'{self.__class__.__name__}(',
            ', '.join([f'{f}={v}' for f in ('pid', 'uid', 'gid') if (v := getattr(self, f)) is not None]),
            ')',
        ])


#


def _get_linux_socket_peer_cred(sock: socket.socket) -> PeerCred | None:
    # Linux: SO_PEERCRED => struct ucred { pid_t pid; uid_t uid; gid_t gid; }

    if not hasattr(socket, 'SO_PEERCRED'):
        return None

    try:
        raw = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('3i'))
    except OSError as e:
        if e.errno == errno.ENOTCONN:
            return None
        raise

    pid, uid, gid = struct.unpack('3i', raw)
    return PeerCred(
        pid=int(pid),
        uid=int(uid),
        gid=int(gid),
    )


#


@lang.cached_function
def _get_bsd_libc() -> ta.Any:
    libc = ct.CDLL(None, use_errno=True)

    if hasattr(libc, 'getpeereid'):
        libc.getpeereid.argtypes = [
            ct.c_int,
            ct.POINTER(ct.c_uint),
            ct.POINTER(ct.c_uint),
        ]
        libc.getpeereid.restype = ct.c_int

    return libc


class _BsdConsts(lang.Namespace):
    SOL_LOCAL = 1

    LOCAL_PEERCRED = 1
    LOCAL_PEERPID = 2
    LOCAL_PEEREPID = 3
    LOCAL_PEERUUID = 4
    LOCAL_PEEREUUID = 5
    LOCAL_PEERTOKEN = 6


def _get_bsd_socket_peer_cred(sock: socket.socket) -> PeerCred | None:
    # Darwin / BSD-ish path:
    # - try LOCAL_PEERPID for pid if exposed by Python's socket module
    # - try getpeereid() for euid/egid

    pid: int | None = None
    uid: int | None = None
    gid: int | None = None

    try:
        raw = sock.getsockopt(_BsdConsts.SOL_LOCAL, _BsdConsts.LOCAL_PEERPID, struct.calcsize('i'))
    except OSError as e:
        if e.errno == errno.ENOTCONN:
            return None
        raise

    [pid] = struct.unpack('i', raw)  # noqa

    libc = _get_bsd_libc()

    if hasattr(libc, 'getpeereid'):
        euid = ct.c_uint()
        egid = ct.c_uint()

        if rc := libc.getpeereid(sock.fileno(), ct.byref(euid), ct.byref(egid)):  # noqa
            if (err := ct.get_errno()) == errno.ENOTCONN:
                return None
            raise OSError(err, 'ctypes call failed')

        uid = int(euid.value)
        gid = int(egid.value)

    return PeerCred(
        pid=pid,
        uid=uid,
        gid=gid,
    )


#


def get_unix_socket_peer_cred(sock: socket.socket) -> PeerCred | None:
    if sock.family != socket.AF_UNIX:
        return None

    if sock.fileno() < 0:
        return None

    sys_platform = getattr(sys, 'platform')  # shuts up mypy

    # Linux: SO_PEERCRED => struct ucred { pid_t pid; uid_t uid; gid_t gid; }
    if sys_platform.startswith('linux'):
        return _get_linux_socket_peer_cred(sock)

    if (
            sys_platform == 'darwin' or
            sys_platform.startswith(('freebsd', 'openbsd', 'netbsd'))
    ):
        return _get_bsd_socket_peer_cred(sock)

    return None
