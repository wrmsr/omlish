import typing as ta

from omlish import check
from omlish import lang

if ta.TYPE_CHECKING:
    from . import buffers
    from . import ops
else:
    buffers = lang.proxy_import('.buffers', __package__)
    ops = lang.proxy_import('.ops', __package__)


class Lazy(lang.Abstract):

    def as_op(self) -> 'ops.Op':
        return check.isinstance(self, ops.Op)

    def as_buffer(self) -> 'buffers.Buffer':
        return check.isinstance(self, buffers.Buffer)
