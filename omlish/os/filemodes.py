# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import os
import typing as ta

from ..lite.check import check


@dc.dataclass(frozen=True)
class FileMode:
    """
    https://docs.python.org/3/library/functions.html#open

    'r' open for reading (default)
    'w' open for writing, truncating the file first
    'x' open for exclusive creation, failing if the file already exists
    'a' open for writing, appending to the end of file if it exists
    'b' binary mode
    't' text mode (default)
    '+' open for updating (reading and writing)

    ==

    https://en.cppreference.com/w/cpp/io/c/fopen

    "r"   read             Open a file for reading        read from start   return NULL and set error
    "w"   write            Create a file for writing     destroy contents  create new
    "a"   append           Append to a file              write to end      create new
    "r+"  read extended    Open a file for read/write    read from start   return NULL and set error
    "w+"  write extended   Create a file for read/write  destroy contents  create new
    "a+"  append extended  Open a file for read/write    write to end      create new

    ==

    a (prs): w a
    a (new): w
    a+ (prs): r w a
    a+ (new): r w

    x (new): w
    x+ (new): r w

    w (prs): w
    w (new): w
    w+ (prs): r w
    w+ (new): r w

    r (prs): r
    r+ (prs): r w
    """

    read: bool
    write: bool

    create: bool
    exists: ta.Literal['beginning', 'truncate', 'fail', 'append']

    binary: bool

    #

    def flags(self) -> int:
        return (
            (
                os.O_RDWR if self.read and self.write else
                os.O_WRONLY if self.write else
                os.O_RDONLY if self.read else
                0
            ) |
            (os.O_CREAT if self.create else 0) |
            (
                os.O_APPEND if self.exists == 'append' else
                os.O_EXCL if self.exists == 'fail' else
                os.O_TRUNC if self.exists == 'truncate' else
                0
            )
        )

    #

    def render(self) -> str:
        return ''.join([
            (
                'a' if self.exists == 'append' else
                'x' if self.exists == 'fail' else
                'w' if self.exists == 'truncate' else
                'r'
            ),
            '+' if self.read and self.write else '',
            'b' if self.binary else '',
        ])

    @classmethod
    def parse(cls, s: str) -> 'FileMode':
        rwxa: ta.Literal['r', 'w', 'x', 'a', None] = None
        tb: ta.Literal['t', 'b', None] = None
        p: bool | None = None

        for c in s:
            if c in 'rwxa':
                rwxa = check.replacing_none(rwxa, c)  # type: ignore[arg-type]
            elif c in 'tb':
                tb = check.replacing_none(tb, c)  # type: ignore[arg-type]
            elif c == '+':
                p = check.replacing_none(p, True)
            else:
                raise ValueError(c)

        if rwxa is None:
            rwxa = 'r'
        if tb is None:
            tb = 't'
        p = bool(p)

        return FileMode(
            read=rwxa == 'r' or p,
            write=rwxa != 'r' or p,
            create=rwxa != 'r',
            exists=(  # noqa
                'append' if rwxa == 'a' else
                'fail' if rwxa == 'x' else
                'truncate' if rwxa == 'w' else
                'beginning'
            ),
            binary=tb == 'b',
        )
