import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    import torch.backends
    import torch.nn
else:
    torch = lang.proxy_import('torch', extras=['backends', 'nn'])


def get_best_device() -> str | None:
    if torch.cuda.is_available():
        return 'cuda'
    elif torch.backends.mps.is_available():
        return 'mps'
    else:
        return None


CanMoveToDevice: ta.TypeAlias = ta.Union['torch.Tensor', 'torch.nn.Module']
CanMoveToDeviceT = ta.TypeVar('CanMoveToDeviceT', bound=CanMoveToDevice)


def to(o: CanMoveToDeviceT, device: str | None) -> CanMoveToDeviceT:
    if isinstance(o, torch.Tensor):
        if device is not None:
            return o.to(device)  # type: ignore
        else:
            return o  # type: ignore

    elif isinstance(o, torch.nn.Module):
        if device is not None:
            o.to(device)
        return o

    else:
        raise TypeError(o)
