# ruff: noqa: UP006 UP007
# @omlish-lite
"""
https://man7.org/linux/man-pages/man8/lsof.8.html
"""
import dataclasses as dc
import enum
import typing as ta

from ..lite.check import check
from ..lite.dataclasses import dataclass_repr_omit_falsey
from ..lite.marshal import OBJ_MARSHALER_OMIT_IF_NONE
from ..subprocesses.run import SubprocessRun
from ..subprocesses.run import SubprocessRunnable
from ..subprocesses.run import SubprocessRunOutput


##


# FIXME: ??
# https://unix.stackexchange.com/a/86011
class LsofItemMode(enum.Enum):
    SOLARIS_NFS_LOCK = 'N'
    READ_LOCK_PARTIAL = 'r'
    READ_LOCK_FULL = 'R'
    WRITE_LOCK_PARTIAL = 'w'
    WRITE_LOCK_FULL = 'W'
    READ_WRITE_LOCK = 'u'
    UNKNOWN_LOCK_TYPE = 'U'
    XENIX_LOCK_PARTIAL = 'x'
    XENIX_LOCK_FULL = 'X'


@dc.dataclass(frozen=True)
class _LsofFieldMeta:
    prefix: str
    process: bool = False
    variadic: bool = False

    @classmethod
    def make(cls, *args, **kwargs):
        return {
            cls: cls(*args, **kwargs),
            OBJ_MARSHALER_OMIT_IF_NONE: True,
        }


@dc.dataclass(frozen=True)
class LsofItem:
    __repr__ = dataclass_repr_omit_falsey

    class _PREFIX:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    class _PROCESS:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    pid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('p', process=True))
    pgid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('g', process=True))
    ppid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('R', process=True))
    cmd: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('c', process=True))

    uid: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('u', process=True))
    login_name: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('L', process=True))

    # FD is the File Descriptor number of the file or:
    #   cwd  current working directory;
    #   Lnn  library references (AIX);
    #   ctty character tty;
    #   DEL  deleted file;
    #   err  FD information error (see NAME column);
    #   fp.  Fileport (Darwin);
    #   jld  jail directory (FreeBSD);
    #   ltx  shared library text (code and data);
    #   Mxx  hex memory-mapped type number xx.
    #   m86  DOS Merge mapped file;
    #   mem  memory-mapped file;
    #   mmap memory-mapped device;
    #   NOFD for a Linux /proc/<PID>/fd directory that can't be opened -- the directory path appears in the NAME column,
    #     followed by an error message;
    #   pd   parent directory;
    #   Rnn  unknown pregion number (HP-UX);
    #   rtd  root directory;
    #   twd  per task current working directory;
    #   txt  program text (code and data);
    #   v86  VP/ix mapped file;
    #
    # FD is followed by one of these characters, describing the mode under which the file is open:
    #   r for read access;
    #   w for write access;
    #   u for read and write access;
    #   space if mode unknown and no lock
    #   character follows;
    #   `-' if mode unknown and lock
    #   character follows.
    #
    # The mode character is followed by one of these lock characters, describing the type of lock applied to the file:
    #   N for a Solaris NFS lock of unknown type;
    #   r for read lock on part of the file;
    #   R for a read lock on the entire file;
    #   w for a write lock on part of the file;
    #   W for a write lock on the entire file;
    #   u for a read and write lock of any length;
    #   U for a lock of unknown type;
    #   x for an SCO OpenServer Xenix lock on part of the file;
    #   X for an SCO OpenServer Xenix lock on the entire file;
    #   space if there is no lock.
    #
    fd: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('f'))

    inode: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('i'))
    name: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('n'))

    # r = read; w = write; u = read/write
    access: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('a'))

    # r/R = read; w/W = write; u = read/write
    lock: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('l'))

    file_flags: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('G'))
    file_type: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('t'))
    file_size: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('s'))
    file_offset: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('o'))  # as 0t<dec> or 0x<hex>

    device_character_code: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('d'))
    device_number: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('D'))  # as 0x<hex>
    raw_device_number: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('r'))  # as 0x<hex>

    share_count: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('C'))
    link_count: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('k'))

    stream_info: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('S'))
    protocol_name: ta.Optional[str] = dc.field(default=None, metadata=_LsofFieldMeta.make('P'))

    tcp_tpi_info: ta.Optional[ta.Sequence[str]] = dc.field(
        default=None,
        metadata=_LsofFieldMeta.make('T', variadic=True),
    )

    # 'K':  'task_id',  # unknown field
    # 'M':  'task_command_name',  # unknown field

    _FIELDS_BY_PREFIX: ta.ClassVar[ta.Mapping[str, dc.Field]]
    _DEFAULT_PREFIXES: ta.ClassVar[str]

    @classmethod
    def from_prefixes(cls, dct: ta.Mapping[str, ta.Any]) -> 'LsofItem':
        kw: ta.Dict[str, ta.Any] = {
            fld.name: val
            for pfx, val in dct.items()
            if (fld := cls._FIELDS_BY_PREFIX.get(pfx)) is not None
        }

        return cls(**kw)

    @classmethod
    def from_prefix_lines(cls, lines: ta.Iterable[str]) -> ta.List['LsofItem']:
        proc_dct: ta.Dict[str, ta.Any] = {}
        file_dct: ta.Dict[str, ta.Any] = {}
        out: ta.List[LsofItem] = []

        def emit() -> None:
            if file_dct:
                out.append(cls.from_prefixes({**proc_dct, **file_dct}))

        for line in lines:
            pfx, val = line[0], line[1:]
            try:
                fld = cls._FIELDS_BY_PREFIX[pfx]
            except KeyError:
                continue
            meta: _LsofFieldMeta = fld.metadata[_LsofFieldMeta]

            if pfx == 'p':
                emit()
                proc_dct = {}
                file_dct = {}
            elif pfx == 'f':
                emit()
                file_dct = {}

            if meta.process:
                dct = proc_dct
            else:
                dct = file_dct

            if meta.variadic:
                dct.setdefault(pfx, []).append(val)
            else:
                if pfx in dct:
                    raise KeyError(pfx)
                dct[pfx] = val

        emit()

        return out


LsofItem._FIELDS_BY_PREFIX = {  # noqa
    meta.prefix: fld
    for fld in dc.fields(LsofItem)  # noqa
    if (meta := fld.metadata.get(_LsofFieldMeta)) is not None  # noqa
}

LsofItem._DEFAULT_PREFIXES = ''.join(LsofItem._FIELDS_BY_PREFIX)  # noqa


##


@dc.dataclass(frozen=True)
class LsofCommand(SubprocessRunnable[ta.List[LsofItem]]):
    pid: ta.Optional[int] = None
    file: ta.Optional[str] = None

    prefixes: ta.Optional[ta.Sequence[str]] = None

    def make_run(self) -> SubprocessRun:
        if (prefixes := self.prefixes) is None:
            prefixes = LsofItem._DEFAULT_PREFIXES  # noqa

        return SubprocessRun.of(
            'lsof',
            '-F', ''.join(prefixes),
            *(['-p', str(self.pid)] if self.pid is not None else []),
            *([self.file] if self.file is not None else []),

            stdout='pipe',
            stderr='devnull',
            check=True,
        )

    def handle_run_output(self, output: SubprocessRunOutput) -> ta.List[LsofItem]:
        lines = [s for l in check.not_none(output.stdout).decode().splitlines() if (s := l.strip())]
        return LsofItem.from_prefix_lines(lines)


##


if __name__ == '__main__':
    def _main() -> None:
        argparse = __import__('argparse')
        parser = argparse.ArgumentParser()
        parser.add_argument('--pid', '-p', type=int)
        parser.add_argument('file', nargs='?')
        args = parser.parse_args()

        importlib = __import__('importlib')
        subprocesses = importlib.import_module('..subprocesses.sync', package=__package__).subprocesses
        items = LsofCommand(
            pid=args.pid,
            file=args.file,
        ).run(subprocesses)

        json = __import__('json')
        marshal_obj = importlib.import_module('..lite.marshal', package=__package__).marshal_obj
        print(json.dumps(marshal_obj(items), indent=2))

    _main()
