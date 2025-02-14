# ruff: noqa: ANN201 N801 N802
import ctypes as ct
import errno
import platform
import signal
import socket
import sys
import typing as ta


LINUX_PLATFORMS = ('linux',)
DARWIN_PLATFORMS = ('darwin',)

LINUX = False
DARWIN = False

if sys.platform in LINUX_PLATFORMS:
    libc = ct.CDLL('libc.so.6')
    LINUX = True

elif sys.platform in DARWIN_PLATFORMS:
    libc = ct.CDLL('/usr/lib/libc.dylib')
    DARWIN = True

else:
    raise OSError('Unsupported platform')


##


libc.errno = ct.cast(libc.errno, ct.POINTER(ct.c_int))  # type: ignore


def lasterr() -> tuple[int, str]:
    err = libc.errno.contents.value  # type: ignore
    return err, errno.errorcode[err]


# int raise(int sig);
libc._raise = libc['raise']  # type: ignore  # noqa
libc._raise.restype = ct.c_int  # noqa
libc._raise.argtypes = [ct.c_int]  # noqa
_raise = libc._raise  # noqa


def sigtrap() -> None:
    libc._raise(signal.SIGTRAP)  # noqa


##


libc.malloc = libc['malloc']  # type: ignore
libc.malloc.restype = ct.c_void_p
libc.malloc.argtypes = [ct.c_size_t]


libc.free = libc['free']  # type: ignore
libc.free.restype = None
libc.free.argtypes = [ct.c_void_p]


class Malloc:
    def __init__(self, sz: int) -> None:
        super().__init__()

        self._sz = sz
        self._base: int | None = None

    def __enter__(self) -> ta.Self:
        base = self._base = libc.malloc(self._sz)
        return base

    def __exit__(self, et, e, tb) -> None:
        if self._base is not None:
            libc.free(self._base)
        self._base = None

    def __int__(self) -> int:
        if self._base is None:
            raise ValueError
        return int(self._base)


##


# void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
libc.mmap.restype = ct.c_void_p
libc.mmap.argtypes = [
    ct.c_void_p,
    ct.c_size_t,
    ct.c_int,
    ct.c_int,
    ct.c_int,
    ct.c_size_t,
]
mmap = libc.mmap

PROT_NONE = 0x0   # Page can not be accessed.
PROT_READ = 0x1   # Page can be read.
PROT_WRITE = 0x2  # Page can be written.
PROT_EXEC = 0x4   # Page can be executed.

MAP_FAILED = -1

if LINUX:
    MAP_SHARED = 0x01         # Share changes.
    MAP_PRIVATE = 0x02        # Changes are private.
    MAP_ANONYMOUS = 0x20      # Don't use a file.
    MAP_GROWSDOWN = 0x00100   # Stack-like segment.
    MAP_DENYWRITE = 0x00800   # ETXTBSY
    MAP_EXECUTABLE = 0x01000  # Mark it as an executable.
    MAP_LOCKED = 0x02000      # Lock the mapping.
    MAP_NORESERVE = 0x04000   # Don't check for reservations.
    MAP_POPULATE = 0x08000    # Populate (prefault) pagetables.
    MAP_NONBLOCK = 0x10000    # Do not block on IO.
    MAP_STACK = 0x20000       # Allocation is for a stack.
    MAP_HUGETLB = 0x40000     # create a huge page mapping

elif DARWIN:
    MAP_SHARED = 0x0001        # [MF|SHM] share changes
    MAP_PRIVATE = 0x0002       # [MF|SHM] changes are private
    MAP_FIXED = 0x0010         # [MF|SHM] interpret addr exactly
    MAP_RENAME = 0x0020        # Sun: rename private pages to file
    MAP_NORESERVE = 0x0040     # Sun: don't reserve needed swap area
    MAP_RESERVED0080 = 0x0080  # previously unimplemented MAP_INHERIT
    MAP_NOEXTEND = 0x0100      # for MAP_FILE, don't change file size
    MAP_HASSEMAPHORE = 0x0200  # region may contain semaphores
    MAP_NOCACHE = 0x0400       # don't cache pages for this mapping
    MAP_JIT = 0x0800           # Allocate a region that will be used for JIT purposes
    MAP_FILE = 0x0000          # map from file (default)
    MAP_ANON = 0x1000          # allocated from memory, swap space


# int munmap(void *addr, size_t length);
libc.munmap.restype = ct.c_int
libc.munmap.argtypes = [
    ct.c_void_p,
    ct.c_size_t,
]
munmap = libc.munmap


# int mprotect(const void *addr, size_t len, int prot);
libc.mprotect.restype = ct.c_int
libc.mprotect.argtypes = [
    ct.c_void_p,
    ct.c_size_t,
    ct.c_int,
]
mprotect = libc.mprotect

if LINUX:
    PROT_GROWSDOWN = 0x01000000  # Extend change to start of growsdown vma (mprotect only).
    PROT_GROWSUP = 0x02000000    # Extend change to start of growsup vma (mprotect only).


if LINUX:
    # void *mremap(void *old_address, size_t old_size, size_t new_size, int flags);
    libc.mremap.restype = ct.c_void_p
    libc.mremap.argtypes = [
        ct.c_void_p,
        ct.c_size_t,
        ct.c_size_t,
        ct.c_int,
    ]
    mremap = libc.mremap

    MREMAP_MAYMOVE = 1
    MREMAP_FIXED = 2


class Mmap:
    def __init__(
            self,
            length: int,
            *,
            prot: int = PROT_READ | PROT_WRITE,
            flags: int | None = None,
            fd: int = -1,
            offset: int = 0,
            desired_base: int = 0,
    ) -> None:
        super().__init__()

        if flags is None:
            if LINUX:
                flags = MAP_SHARED | MAP_ANONYMOUS
            elif DARWIN:
                flags = MAP_SHARED | MAP_ANON
            else:
                raise OSError

        self._length = length
        self._prot = prot
        self._flags = flags
        self._fd = fd
        self._offset = offset
        self._desired_base = desired_base

        self._base = None
        self._is_mapped = False

    @property
    def base(self) -> int | None:
        return self._base

    def __enter__(self) -> 'Mmap':
        base = mmap(
            self._desired_base,
            self._length,
            self._prot,
            self._flags,
            self._fd,
            self._offset,
        )
        if base == MAP_FAILED:
            err, msg = lasterr()
            raise OSError(err, 'mmap failed: ' + msg)
        self._base = base
        self._is_mapped = True
        return self

    def __exit__(self, et, e, tb) -> None:
        if self._is_mapped:
            res = munmap(self._base, self._length)
            if res != 0:
                err, msg = lasterr()
                raise OSError(err, 'munmap failed: ' + msg)
            self._is_mapped = False


##


if LINUX:
    # int prctl(int option, unsigned long arg2, unsigned long arg3, unsigned long arg4, unsigned long arg5);
    libc.prctl.restype = ct.c_int
    libc.prctl.argtypes = [ct.c_int, ct.c_ulong, ct.c_ulong, ct.c_ulong, ct.c_ulong]

    prctl = libc.prctl

    # Values to pass as first argument to prctl()

    PR_SET_PDEATHSIG = 1  # Second arg is a signal
    PR_GET_PDEATHSIG = 2  # Second arg is a ptr to return the signal

    # Get/set current->mm->dumpable
    PR_GET_DUMPABLE = 3
    PR_SET_DUMPABLE = 4

    # Get/set unaligned access control bits (if meaningful)
    PR_GET_UNALIGN = 5
    PR_SET_UNALIGN = 6
    PR_UNALIGN_NOPRINT = 1  # silently fix up unaligned user accesses
    PR_UNALIGN_SIGBUS = 2  # generate SIGBUS on unaligned user access

    # Get/set whether or not to drop capabilities on setuid() away from uid 0 (as per security/commoncap.c)
    PR_GET_KEEPCAPS = 7
    PR_SET_KEEPCAPS = 8

    # Get/set floating-point emulation control bits (if meaningful)
    PR_GET_FPEMU = 9
    PR_SET_FPEMU = 10
    PR_FPEMU_NOPRINT = 1  # silently emulate fp operations accesses
    PR_FPEMU_SIGFPE = 2  # don't emulate fp operations, send SIGFPE instead

    # Get/set floating-point exception mode (if meaningful)
    PR_GET_FPEXC = 11
    PR_SET_FPEXC = 12
    PR_FP_EXC_SW_ENABLE = 0x80  # Use FPEXC for FP exception enables
    PR_FP_EXC_DIV = 0x010000    # floating point divide by zero
    PR_FP_EXC_OVF = 0x020000    # floating point overflow
    PR_FP_EXC_UND = 0x040000    # floating point underflow
    PR_FP_EXC_RES = 0x080000    # floating point inexact result
    PR_FP_EXC_INV = 0x100000    # floating point invalid operation
    PR_FP_EXC_DISABLED = 0      # FP exceptions disabled
    PR_FP_EXC_NONRECOV = 1      # async non-recoverable exc. mode
    PR_FP_EXC_ASYNC = 2         # async recoverable exception mode
    PR_FP_EXC_PRECISE = 3       # precise exception mode

    # Get/set whether we use statistical process timing or accurate timestamp process timing
    PR_SET_NAME = 15  # Set process name
    PR_GET_NAME = 16  # Get process name

    # Get/set process endian
    PR_GET_ENDIAN = 19
    PR_SET_ENDIAN = 20
    PR_ENDIAN_BIG = 0
    PR_ENDIAN_LITTLE = 1      # True little endian mode
    PR_ENDIAN_PPC_LITTLE = 2  # "PowerPC" pseudo little endian

    # Get/set process seccomp mode
    PR_GET_SECCOMP = 21
    PR_SET_SECCOMP = 22

    # Get/set the capability bounding set (as per security/commoncap.c)
    PR_CAPBSET_READ = 23
    PR_CAPBSET_DROP = 24

    # Get/set the process' ability to use the timestamp counter instruction
    PR_GET_TSC = 25
    PR_SET_TSC = 26
    PR_TSC_ENABLE = 1   # allow the use of the timestamp counter
    PR_TSC_SIGSEGV = 2  # throw a SIGSEGV instead of reading the TSC

    # Get/set securebits (as per security/commoncap.c)
    PR_GET_SECUREBITS = 27
    PR_SET_SECUREBITS = 28

    # Get/set the timerslack as used by poll/select/nanosleep. A value of 0 means "use default"
    PR_SET_TIMERSLACK = 29
    PR_GET_TIMERSLACK = 30

    PR_TASK_PERF_EVENTS_DISABLE = 31
    PR_TASK_PERF_EVENTS_ENABLE = 32

    # Set early/late kill mode for hwpoison memory corruption. This influences when the process gets killed on a memory
    # corruption.
    PR_MCE_KILL = 33
    PR_MCE_KILL_CLEAR = 0
    PR_MCE_KILL_SET = 1

    PR_MCE_KILL_LATE = 0
    PR_MCE_KILL_EARLY = 1
    PR_MCE_KILL_DEFAULT = 2

    PR_MCE_KILL_GET = 34


##


if LINUX or DARWIN:
    SCM_RIGHTS = 1

    ct.c_ssize_t = ct.c_size_t  # type: ignore

    class iovec(ct.Structure):
        pass

    iovec._fields_ = [
        ('iov_base', ct.c_void_p),  # Pointer to data.
        ('iov_len', ct.c_size_t),   # Length of data.
    ]

    class msghdr(ct.Structure):
        pass

    msghdr._fields_ = [
        ('msg_name', ct.c_void_p),        # Address to send to/receive from.
        ('msg_namelen', ct.c_uint),       # Length of address data.
        ('msg_iov', ct.POINTER(iovec)),   # Vector of data to send/receive into.
        ('msg_iovlen', ct.c_size_t),      # Number of elements in the vector.
        ('msg_control', ct.c_void_p),     # Ancillary data (eg BSD filedesc passing).
        ('msg_controllen', ct.c_size_t),  # Ancillary data buffer length. !! The type should be
        # socklen_t but the definition of the kernel is incompatible with this
        ('msg_flags', ct.c_int),          # Flags on received message.
    ]

    class cmsghdr(ct.Structure):
        pass

    cmsghdr._fields_ = [
        ('cmsg_len', ct.c_size_t),  # Length of data in cmsg_data plus length
        # of cmsghdr structure. !! The type should be socklen_t but the definition of the kernel is incompatible with
        # this.
        ('cmsg_level', ct.c_int),   # Originating protocol.
        ('cmsg_type', ct.c_int),    # Protocol specific type.
    ]

    # ssize_t sendmsg(int sockfd, const struct msghdr *msg, int flags);
    libc.sendmsg.restype = ct.c_ssize_t
    libc.sendmsg.argtypes = [ct.c_int, ct.POINTER(msghdr), ct.c_int]

    # ssize_t recvmsg(int sockfd, struct msghdr *msg, int flags);
    libc.sendmsg.restype = ct.c_ssize_t
    libc.sendmsg.argtypes = [ct.c_int, ct.POINTER(msghdr), ct.c_int]

    def CMSG_ALIGN(sz):
        i = ct.sizeof(ct.c_size_t)
        return ((sz + i - 1) // i) * i

    def CMSG_SPACE(sz):
        return CMSG_ALIGN(sz) + CMSG_ALIGN(ct.sizeof(cmsghdr))

    def CMSG_LEN(sz):
        return CMSG_ALIGN(ct.sizeof(cmsghdr)) + sz

    def sendfd(sock, fd, data='.'):
        """
        Note: stdlib as of 3.7:

          https://github.com/python/cpython/blob/84ed9a68bd9a13252b376b21a9167dabae254325/Lib/multiprocessing/reduction.py#L141

        But still kept around due to other use of cmsg machinery.
        """  # noqa

        if not data:
            raise ValueError(data)

        iov = iovec()
        iov.iov_base = ct.cast(ct.c_char_p(data), ct.c_void_p)  # noqa
        iov.iov_len = len(data)

        cmsg_size = CMSG_SPACE(ct.sizeof(ct.c_int))
        msg_control = (ct.c_char * cmsg_size)()  # noqa

        msgh = msghdr()
        msgh.msg_name = None
        msgh.msg_namelen = 0
        msgh.msg_iov = ct.cast(ct.addressof(iov), ct.POINTER(iovec))
        msgh.msg_iovlen = 1
        msgh.msg_control = ct.cast(ct.addressof(msg_control), ct.c_void_p)
        msgh.msg_controllen = cmsg_size
        msgh.msg_flags = 0

        h = ct.cast(ct.addressof(msg_control), ct.POINTER(cmsghdr))
        h.contents.cmsg_len = CMSG_LEN(ct.sizeof(ct.c_int))
        h.contents.cmsg_level = socket.SOL_SOCKET
        h.contents.cmsg_type = SCM_RIGHTS

        p_fd = ct.cast(
            ct.addressof(msg_control) + ct.sizeof(cmsghdr),
            ct.POINTER(ct.c_int))
        p_fd.contents = ct.c_int(fd)

        return libc.sendmsg(sock, msgh, 0)

    def recvfd(sock, buf_len=4096):
        """See sendfd."""

        if buf_len < 1:
            raise ValueError(buf_len)

        cmsg_size = CMSG_SPACE(ct.sizeof(ct.c_int))
        cmsg_buf = (ct.c_char * cmsg_size)()  # noqa
        data_buf = (ct.c_char * buf_len)()  # noqa

        iov = iovec()
        iov.iov_base = ct.cast(ct.addressof(data_buf), ct.c_void_p)
        iov.iov_len = buf_len

        msgh = msghdr()
        msgh.msg_name = None
        msgh.msg_namelen = 0
        msgh.msg_iov = ct.cast(ct.addressof(iov), ct.POINTER(iovec))
        msgh.msg_iovlen = 1
        msgh.msg_control = ct.cast(ct.addressof(cmsg_buf), ct.c_void_p)
        msgh.msg_controllen = cmsg_size
        msgh.msg_flags = 0

        recv_len = libc.recvmsg(sock, ct.cast(ct.addressof(msgh), ct.POINTER(msghdr)), 0)
        if recv_len < 0:
            return recv_len, None

        h = ct.cast(ct.addressof(cmsg_buf), ct.POINTER(cmsghdr))
        if (h.contents.cmsg_len != CMSG_LEN(ct.sizeof(ct.c_int))) or \
                (h.contents.cmsg_level != socket.SOL_SOCKET) or \
                (h.contents.cmsg_type != SCM_RIGHTS):
            return -2, None

        p_fd = ct.cast(
            ct.addressof(cmsg_buf) + ct.sizeof(cmsghdr),
            ct.POINTER(ct.c_int))
        fd = p_fd.contents.value
        if fd < 0:
            return -3, None

        return fd, data_buf[:recv_len]


##


if LINUX:
    dl = ct.CDLL('libdl.so.2')

    dl.dlopen.restype = ct.c_void_p
    dl.dlopen.argtypes = [ct.c_char_p, ct.c_int]
    dlopen = dl.dlopen

    dl.dlsym.restype = ct.c_void_p
    dl.dlsym.argtypes = [ct.c_void_p, ct.c_char_p]
    dlsym = dl.dlsym

    dl.dlerror.restype = ct.c_char_p
    dl.dlerror.argtypes = []
    dlerror = dl.dlerror

    dl.dlclose.restype = ct.c_int
    dl.dlclose.argtypes = [ct.c_void_p]
    dlclose = dl.dlclose

elif DARWIN:
    libc.dlopen.restype = ct.c_void_p
    libc.dlopen.argtypes = [ct.c_char_p, ct.c_int]
    dlopen = libc.dlopen

    libc.dlsym.restype = ct.c_void_p
    libc.dlsym.argtypes = [ct.c_void_p, ct.c_char_p]
    dlsym = libc.dlsym

    libc.dlerror.restype = ct.c_char_p
    libc.dlerror.argtypes = []
    dlerror = libc.dlerror

    libc.dlclose.restype = ct.c_int
    libc.dlclose.argtypes = [ct.c_void_p]
    dlclose = libc.dlclose


##


if LINUX:
    F_SETPIPE_SZ = 1031


##


if LINUX:
    SO_PASSCRED = 16  # noqa
    SO_PEERCRED = 17

elif DARWIN:
    SOL_LOCAL = 1
    LOCAL_PEERCRED = 1


##


if LINUX:
    def gettid() -> int:
        syscalls = {
            'i386': 224,  # unistd_32.h: #define __NR_gettid 224
            'x86_64': 186,  # unistd_64.h: #define __NR_gettid 186
            'aarch64': 178,  # asm-generic/unistd.h: #define __NR_gettid 178
        }
        try:
            tid = libc.syscall(syscalls[platform.machine()])
        except Exception:  # noqa
            tid = -1
        return tid
