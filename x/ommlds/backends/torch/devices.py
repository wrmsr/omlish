import typing as ta

import torch.backends
from torch import nn


##


def get_best_device() -> str | None:
    if torch.cuda.is_available():
        return 'cuda'
    elif torch.backends.mps.is_available():
        return 'mps'
    else:
        return None


CanMoveToDevice: ta.TypeAlias = ta.Union[torch.Tensor, nn.Module]  # noqa
CanMoveToDeviceT = ta.TypeVar('CanMoveToDeviceT', bound=CanMoveToDevice)


def to(o: CanMoveToDeviceT, device: str | None) -> CanMoveToDeviceT:
    if isinstance(o, torch.Tensor):
        if device is not None:
            return o.to(device)  # type: ignore
        else:
            return o

    elif isinstance(o, nn.Module):
        if device is not None:
            o.to(device)
        return o

    else:
        raise TypeError(o)
