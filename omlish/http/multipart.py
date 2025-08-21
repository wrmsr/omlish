"""
https://datatracker.ietf.org/doc/html/rfc7578
"""
import dataclasses as dc
import io
import typing as ta
import uuid

from .. import cached


MultipartData: ta.TypeAlias = ta.Any  # bytes | file


##


@dc.dataclass(frozen=True)
class MultipartField:
    data: MultipartData
    name: bytes | None = None
    file_name: bytes | None = None
    headers: ta.Sequence[tuple[bytes, bytes]] | None = None


class MultipartEncoder:
    def __init__(
            self,
            fields: ta.Sequence[MultipartField],
            *,
            boundary: bytes | None = None,
    ) -> None:
        super().__init__()

        self._fields = fields
        self._boundary = boundary or (b'----WebKitFormBoundary-' + uuid.uuid4().hex.encode('ascii'))

    class _Line(ta.NamedTuple):
        data: MultipartData
        sz: int

    @cached.function
    def _lines(self) -> ta.Sequence[_Line]:
        l: list[MultipartEncoder._Line] = []

        def add(d: MultipartData) -> None:
            if isinstance(d, bytes):
                sz = len(d)
            else:
                raise TypeError(d)
            l.append(MultipartEncoder._Line(d, sz))

        for f in self._fields:
            add(b'--%s' % (self._boundary,))
            ps = [b'form-data']
            if f.name is not None:
                ps.append(b'name="%s"' % (f.name,))
            if f.file_name is not None:
                ps.append(b'filename="%s"' % (f.file_name,))
            add(b'Content-Disposition: ' + b'; '.join(ps))
            for hk, hv in f.headers or ():
                add(b'%s: %s' % (hk, hv))
            add(b'')
            add(f.data)

        add(b'--%s--' % (self._boundary,))

        return l

    @cached.function
    def content_type(self) -> bytes:
        return b'multipart/form-data; boundary=%s' % (self._boundary,)

    @cached.function
    def content_length(self) -> int:
        return sum(l.sz + 2 for l in self._lines())

    @cached.function
    def content(self) -> bytes:
        buf = io.BytesIO()
        for l in self._lines():
            if isinstance(l.data, bytes):
                buf.write(l.data)
            else:
                raise TypeError(l.data)
            buf.write(b'\r\n')
        return buf.getvalue()
