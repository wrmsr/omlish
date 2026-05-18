# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
# BSD 3-Clause License
#
# Copyright (c) 2009, Daniele Varrazzo <daniele.varrazzo@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#    disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# https://github.com/dvarrazzo/py-setproctitle/tree/42a90422fe65be95d7d32c4cb6e441fcb26c8731
import abc
import ctypes as ct
import os
import sys
import threading
import typing as ta


##


class _ProcessTitleState:
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.RLock()

        self._setup_done = False
        self._setup_ok = False

        self._libc = self._load_libc()

        self._ps_addr = 0
        self._ps_size = 0

        self._current_title = self._join_sys_argv()

    def _load_libc(self) -> ta.Any:
        return ct.CDLL(None, use_errno=True)

    #

    @staticmethod
    def _join_sys_argv() -> str:
        return ' '.join(sys.argv)

    #

    @staticmethod
    def _is_debug() -> bool:
        return bool(os.environ.get('SPT_DEBUG', ''))

    def setup(self) -> None:
        with self._lock:
            if self._setup_done:
                return

            self._setup_done = True
            try:
                self._setup()
            except Exception as e:  # noqa
                self._setup_ok = False
                if self._is_debug():
                    print(f'failed to initialize setproctitle: {e}', file=sys.stderr)
            else:
                self._setup_ok = True

    def _setup(self) -> None:
        pass

    def _global_setup(self) -> None:
        pass

    #

    @staticmethod
    def _encode_title(title: str) -> bytes:
        if not isinstance(title, str):
            raise TypeError('title must be a string')
        if '\x00' in title:
            raise ValueError('embedded null character')
        return title.encode('utf-8')

    @staticmethod
    def _decode_title(title: bytes) -> str:
        return title.decode('utf-8', 'replace')

    #

    def set_process_title(self, title: str) -> None:
        title_b = self._encode_title(title)
        self.setup()
        with self._lock:
            self._current_title = title
            self._set_process_title(title_b)

    @abc.abstractmethod
    def _set_process_title(self, title_b: bytes) -> None:
        raise NotImplementedError

    #

    _PADDING: ta.ClassVar[bytes] = b'\x00'

    def get_process_title(self) -> str:
        self.setup()
        with self._lock:
            if self._ps_addr and self._ps_size:
                data = ct.string_at(
                    self._ps_addr,
                    self._ps_size,
                ).rstrip(self._PADDING)
                return self._decode_title(data)
            return self._current_title

    #

    def set_thread_title(self, title: str) -> None:
        title_b = self._encode_title(title)
        self._set_thread_title(title_b)

    def _set_thread_title(self, title_b: bytes) -> None:
        pass

    #

    def get_thread_title(self) -> str:
        return self._get_thread_title().decode('utf-8', 'replace')

    def _get_thread_title(self) -> bytes:
        return b''


#


class _UnsupportedProcesTitleState(_ProcessTitleState):
    def get_process_title(self) -> str:
        return ''

    #

    def _set_process_title(self, title_b: bytes) -> None:
        pass


#


class _ClobberProcessTitleState(_ProcessTitleState):
    def __init__(self) -> None:
        super().__init__()

        self._last_status_len = 0
        self._argv: ta.Optional[ta.Sequence[ta.Any]] = None

        self._environ_keepalive: ta.List[ta.Any] = []

    def _setup_clobber(self, argv: ta.Sequence[int]) -> None:
        if not argv:
            return

        initial_title = b' '.join(ct.string_at(int(a)) for a in argv if a)
        end = 0
        for i, addr in enumerate(argv):
            if not addr:
                continue
            if i == 0 or end + 1 == addr:
                end = int(addr) + len(ct.string_at(int(addr)))

        if not end:
            return

        if not os.environ.get('SPT_NOENV'):
            end = self._extend_with_environ(end)
            self._copy_environ()

        self._ps_addr = int(argv[0])
        self._ps_size = max(0, end - self._ps_addr)

        self._last_status_len = self._ps_size

        self._argv = argv

        self._current_title = self._decode_title(initial_title)

        self._write_clobbered_title(initial_title)

    def _write_clobbered_title(self, title_b: bytes) -> None:
        if not self._ps_addr or not self._ps_size:
            return

        n = min(len(title_b), max(0, self._ps_size - 1))
        if n:
            ct.memmove(self._ps_addr, title_b, n)
        ct.memset(self._ps_addr + n, 0, self._ps_size - n)
        self._last_status_len = n

    #

    @staticmethod
    def _get_environ(libc: ta.Any) -> ta.Optional[ta.Any]:
        try:
            return ct.POINTER(ct.c_void_p).in_dll(libc, 'environ')
        except ValueError:
            return None

    def _extend_with_environ(self, end: int) -> int:
        environ = self._get_environ(self._libc)
        if not environ:
            return end

        i = 0
        while environ[i]:
            addr = int(environ[i])
            if end + 1 == addr:
                end = addr + len(ct.string_at(addr))
            i += 1
        return end

    def _copy_environ(self) -> None:
        environ = self._get_environ(self._libc)
        if not environ:
            return

        bufs = []
        ptrs = []
        i = 0
        while environ[i]:
            buf = ct.create_string_buffer(ct.string_at(int(environ[i])))
            bufs.append(buf)
            ptrs.append(ct.cast(buf, ct.c_void_p).value)
            i += 1

        arr = (ct.c_void_p * (len(ptrs) + 1))()
        for i, ptr in enumerate(ptrs):
            arr[i] = ptr
        arr[len(ptrs)] = None

        environ_var = ct.c_void_p.in_dll(self._libc, 'environ')
        environ_var.value = ct.cast(arr, ct.c_void_p).value
        self._environ_keepalive = [arr, *bufs]


#


class _LinuxProcessTitleState(_ClobberProcessTitleState):
    _ARG_MAX: ta.ClassVar[int] = 96 * 1024

    @classmethod
    def _find_argv_from_env(
            cls,
            libc: ta.Any,
            argc: int,
            arg0: bytes,
    ) -> ta.Optional[ta.List[int]]:
        if argc <= 0 or not arg0:
            return None

        environ = cls._get_environ(libc)
        if not environ or not environ[0]:
            return None

        argv = [0] * argc
        ptr = int(environ[0]) - 1
        limit = int(environ[0]) - cls._ARG_MAX

        def byte_at(addr: int) -> int:
            return ct.c_ubyte.from_address(addr).value

        for i in range(argc - 1, 0, -1):
            if byte_at(ptr) != 0:
                return None
            ptr -= 1
            while ptr > limit and byte_at(ptr) != 0:
                ptr -= 1
            if ptr <= limit:
                return None
            argv[i] = ptr + 1

        ptr -= len(arg0)
        if ptr <= limit:
            return None
        if ct.string_at(ptr, len(arg0)) != arg0:
            return None

        argv[0] = ptr
        return argv

    @staticmethod
    def _read_proc_args() -> ta.Tuple[int, bytes]:
        with open('/proc/self/cmdline', 'rb') as f:
            data = f.read()
        if not data:
            return 0, b''
        return data.count(b'\x00'), data.split(b'\x00', 1)[0]

    #

    def _setup(self) -> None:
        argc, arg0 = self._read_proc_args()
        argv = self._find_argv_from_env(self._libc, argc, arg0)
        if not argv:
            return
        self._setup_clobber(argv)

    #

    @staticmethod
    def _call_prctl(libc: ta.Any, option: int, arg: ta.Any) -> None:
        fn = getattr(libc, 'prctl', None)
        if fn is None:
            return
        fn.argtypes = [
            ct.c_int,
            ct.c_void_p,
            ct.c_ulong,
            ct.c_ulong,
            ct.c_ulong,
        ]
        fn.restype = ct.c_int

        if isinstance(arg, bytes):
            buf = ct.create_string_buffer(arg)
            ptr = ct.cast(buf, ct.c_void_p)
            fn(option, ptr, 0, 0, 0)
        else:
            ptr = ct.cast(arg, ct.c_void_p)
            fn(option, ptr, 0, 0, 0)

    _PR_SET_NAME: ta.ClassVar[int] = 15
    _PR_GET_NAME: ta.ClassVar[int] = 16

    def _set_process_title(self, title_b: bytes) -> None:
        self._write_clobbered_title(title_b)
        self._call_prctl(self._libc, self._PR_SET_NAME, title_b)

    def _get_thread_title(self) -> bytes:
        buf = ct.create_string_buffer(16)
        self._call_prctl(self._libc, self._PR_GET_NAME, buf)
        return buf.value

    def _set_thread_title(self, title_b: bytes) -> None:
        self._call_prctl(self._libc, self._PR_SET_NAME, title_b)


#


class _BsdProcessTitleState(_ProcessTitleState):
    def _setup(self) -> None:
        self._current_title = self._join_sys_argv()

    def _set_process_title(self, title_b: bytes) -> None:
        fn = getattr(self._libc, 'setproctitle', None)
        if fn is None:
            return
        fn.argtypes = [ct.c_char_p, ct.c_char_p]
        fn.restype = None
        fn(b'%s', title_b)


#


class _DarwinProcessTitleState(_ClobberProcessTitleState):
    def __init__(self) -> None:
        super().__init__()

        self._argv_keepalive: ta.List[ta.Any] = []

    def _load_libc(self) -> ta.Any:
        return ct.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)

    #

    @staticmethod
    def _copy_argv(argv: ta.Sequence[int]) -> ta.Tuple[ta.Any, ta.List[ta.Any]]:
        bufs = []
        arr = (ct.c_void_p * (len(argv) + 1))()
        for i, addr in enumerate(argv):
            addr1 = int(addr)
            buf = ct.create_string_buffer(ct.string_at(addr1))
            bufs.append(buf)
            arr[i] = ct.cast(buf, ct.c_void_p).value
        arr[len(argv)] = None
        return arr, bufs

    def _setup(self) -> None:
        libc = self._libc
        ns_get_argc = libc._NSGetArgc  # noqa
        ns_get_argc.restype = ct.POINTER(ct.c_int)
        ns_get_argc.argtypes = []
        ns_get_argv = libc._NSGetArgv  # noqa
        ns_get_argv.restype = ct.POINTER(ct.POINTER(ct.c_void_p))
        ns_get_argv.argtypes = []

        argc_p = ns_get_argc()
        argv_pp = ns_get_argv()
        if not argc_p or not argv_pp:
            return

        argc = int(argc_p.contents.value)
        argv_p = argv_pp.contents
        argv = [int(argv_p[i]) for i in range(argc)]
        self._setup_clobber(argv)

        new_argv, keepalive = self._copy_argv(argv)
        argv_pp.contents = ct.cast(
            new_argv,
            ct.POINTER(ct.c_void_p),
        )
        self._argv_keepalive.extend(keepalive)
        self._argv_keepalive.append(new_argv)

    def _global_setup(self) -> None:
        self.get_process_title()

    #

    class _CheckedIn(ta.NamedTuple):
        cf: ta.Any
        app: ta.Any

        asn_fn: ta.Any
        set_info_fn: ta.Any

        key_p: ta.Any

    _CORE_FOUNDATION_PATH: ta.ClassVar[str] = (
        '/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation'
    )

    _APPLICATION_SERVICES_PATH: ta.ClassVar[str] = (
        '/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices'
    )

    def _configure_core_foundation(self, cf: ta.Any) -> None:
        cf.CFStringCreateWithCString.argtypes = [
            ct.c_void_p,
            ct.c_char_p,
            ct.c_uint32,
        ]
        cf.CFStringCreateWithCString.restype = ct.c_void_p
        cf.CFRelease.argtypes = [ct.c_void_p]
        cf.CFRelease.restype = None

    def _configure_launch_services(self, app: ta.Any) -> bool:
        asn_fn = getattr(app, '_LSGetCurrentApplicationASN', None)
        set_info_fn = getattr(app, '_LSSetApplicationInformationItem', None)
        if asn_fn is None or set_info_fn is None:
            return False

        asn_fn.argtypes = []
        asn_fn.restype = ct.c_void_p
        set_info_fn.argtypes = [
            ct.c_int,
            ct.c_void_p,
            ct.c_void_p,
            ct.c_void_p,
            ct.c_void_p,
        ]
        set_info_fn.restype = ct.c_int
        return True

    def _do_check_in(self) -> ta.Optional[_CheckedIn]:
        cf = ct.CDLL(self._CORE_FOUNDATION_PATH)
        app = ct.CDLL(self._APPLICATION_SERVICES_PATH)
        self._configure_core_foundation(cf)
        if not self._configure_launch_services(app):
            return None

        asn_fn = getattr(app, '_LSGetCurrentApplicationASN', None)
        set_info_fn = getattr(app, '_LSSetApplicationInformationItem', None)
        if asn_fn is None or set_info_fn is None:
            return None

        try:
            key_p = ct.c_void_p.in_dll(app, '_kLSDisplayNameKey')
        except ValueError:
            return None

        conn_fn = getattr(
            app,
            '_LSSetApplicationLaunchServicesServerConnectionStatus',
            None,
        )
        check_in_fn = getattr(app, '_LSApplicationCheckIn', None)
        if conn_fn is None or check_in_fn is None:
            return None

        try:
            cf.CFBundleGetMainBundle.argtypes = []
            cf.CFBundleGetMainBundle.restype = ct.c_void_p
            cf.CFBundleGetInfoDictionary.argtypes = [ct.c_void_p]
            cf.CFBundleGetInfoDictionary.restype = ct.c_void_p
            cf.CFDictionaryCreateMutableCopy.argtypes = [
                ct.c_void_p,
                ct.c_int,
                ct.c_void_p,
            ]
            cf.CFDictionaryCreateMutableCopy.restype = ct.c_void_p
            cf.CFDictionaryAddValue.argtypes = [
                ct.c_void_p,
                ct.c_void_p,
                ct.c_void_p,
            ]
            cf.CFDictionaryAddValue.restype = None
            true_p = ct.c_void_p.in_dll(cf, 'kCFBooleanTrue')
        except (AttributeError, ValueError):
            return None

        conn_fn.argtypes = [ct.c_uint64, ct.c_void_p]
        conn_fn.restype = None
        check_in_fn.argtypes = [ct.c_int, ct.c_void_p]
        check_in_fn.restype = ct.c_void_p

        conn_fn(0, None)
        info = cf.CFBundleGetInfoDictionary(cf.CFBundleGetMainBundle())
        mutable_info = cf.CFDictionaryCreateMutableCopy(None, 0, info)
        if not mutable_info:
            return None

        key = cf.CFStringCreateWithCString(
            None,
            b'LSUIElement',
            self._CF_STRING_ENCODING_UTF8,
        )
        if not key:
            cf.CFRelease(mutable_info)
            return None
        try:
            cf.CFDictionaryAddValue(mutable_info, key, true_p.value)
            check_in_fn(-2, mutable_info)
        finally:
            cf.CFRelease(key)
            cf.CFRelease(mutable_info)

        return self._CheckedIn(
            cf,
            app,

            asn_fn,
            set_info_fn,

            key_p,
        )

    _checked_in: ta.Optional[_CheckedIn]

    def _check_in(self) -> ta.Optional[_CheckedIn]:
        try:
            return self._checked_in
        except AttributeError:
            pass

        with self._lock:
            try:
                return self._checked_in
            except AttributeError:
                pass

            try:
                ci = self._do_check_in()
            except Exception as e:  # noqa
                if self._is_debug():
                    print(f'failed to initialize darwin setproctitle: {e}', file=sys.stderr)
                ci = None

            self._checked_in = ci
            return ci

    #

    _CF_STRING_ENCODING_UTF8: ta.ClassVar[int] = 0x08000100

    def _set_darwin_process_title(self, title_b: bytes) -> None:
        if (ci := self._check_in()) is None:
            return

        asn = ci.asn_fn()
        if not asn or not ci.key_p.value:
            return

        cf_title = ci.cf.CFStringCreateWithCString(
            None,
            title_b,
            self._CF_STRING_ENCODING_UTF8,
        )
        if not cf_title:
            return
        try:
            ci.set_info_fn(-2, asn, ci.key_p.value, cf_title, None)
        finally:
            ci.cf.CFRelease(cf_title)

    def _call_pthread_setname_np(self, title_b: bytes) -> None:
        fn = getattr(self._libc, 'pthread_setname_np', None)
        if fn is None:
            return
        fn.argtypes = [ct.c_char_p]
        fn.restype = ct.c_int
        fn(title_b)

    def _set_process_title(self, title_b: bytes) -> None:
        self._write_clobbered_title(title_b)
        self._set_darwin_process_title(title_b)
        self._call_pthread_setname_np(title_b[:63])

    def _set_thread_title(self, title_b: bytes) -> None:
        self._call_pthread_setname_np(title_b[:63])


#


_PROCESS_TITLE_STATE: _ProcessTitleState
if sys.platform == 'darwin':
    _PROCESS_TITLE_STATE = _DarwinProcessTitleState()
elif 'bsd' in sys.platform:
    _PROCESS_TITLE_STATE = _BsdProcessTitleState()
elif sys.platform.startswith('linux'):
    _PROCESS_TITLE_STATE = _LinuxProcessTitleState()
else:
    _PROCESS_TITLE_STATE = _UnsupportedProcesTitleState()


_PROCESS_TITLE_STATE._global_setup()  # noqa


##


def setproctitle(title: str) -> None:
    """Change the process title."""

    _PROCESS_TITLE_STATE.set_process_title(title)


def getproctitle() -> str:
    """Get the current process title."""

    return _PROCESS_TITLE_STATE.get_process_title()


def setthreadtitle(title: str) -> None:
    """Change the current thread title."""

    _PROCESS_TITLE_STATE.set_thread_title(title)


def getthreadtitle() -> str:
    """Return the current thread title."""

    return _PROCESS_TITLE_STATE.get_thread_title()


##


# print(os.getpid())
# input()
# setproctitle('Hello, world!')
# input()
