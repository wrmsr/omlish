import typing as ta

from omlish import lang


# fmt: off
if ta.TYPE_CHECKING:
    import tinygrad as tg  # noqa
    from tinygrad import nn  # noqa
else:
    tg = lang.proxy_import('tinygrad')
    nn = lang.proxy_import('tinygrad.nn')
# fmt: on


# mypy workaround
# Tensor = tg.Tensor  # type: ignore
# TinyJit = tg.TinyJit  # type: ignore
