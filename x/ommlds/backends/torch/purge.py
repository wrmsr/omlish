"""
TODO:
 - fix mps
 - fallback to .set_(cpu_zero) or smth
 - return stats
"""
import typing as ta

import torch
from torch import nn


##


class Purger:
    def __init__(
            self,
            *,
            resize_storage: bool = True,
            detach_tensors: bool = True,
            overwrite_tensors: bool = True,
    ) -> None:
        super().__init__()

        self._resize_storage = resize_storage
        self._detach_tensors = detach_tensors
        self._overwrite_tensors = overwrite_tensors

    def _purge_untyped_storage(self, s: torch.storage.UntypedStorage) -> None:
        if self._resize_storage:
            if s.device.type != 'mps':
                s.resize_(0)

    def _purge_tensor(self, t: torch.Tensor) -> None:
        if t.grad is not None:
            self.purge(t.grad)

        if self._detach_tensors:
            t.detach_()

        self.purge(t.untyped_storage())

        if self._overwrite_tensors:
            z = torch.zeros(
                (0,),
                dtype=t.dtype,
                device=t.device,
                requires_grad=False,
            )

            t.set_(z.untyped_storage())

    def _purge_module(self, m: nn.Module) -> None:
        for c in m.children():
            self.purge(c)

        for p in m.parameters(recurse=False):
            self.purge(p)

        for b in m.buffers(recurse=False):
            self.purge(b)

    def purge(self, o: ta.Any) -> None:
        if isinstance(o, torch.storage.UntypedStorage):
            self._purge_untyped_storage(o)

        elif isinstance(o, torch.Tensor):
            self._purge_tensor(o)

        elif isinstance(o, nn.Module):
            self._purge_module(o)

        else:
            raise TypeError(o)


def purge(obj: ta.Any, **kwargs: ta.Any) -> None:
    Purger(**kwargs).purge(obj)
