import abc
import typing as ta

from torch import Tensor
from torch import nn


class BaseVAE(nn.Module):

    def __init__(self) -> None:
        super().__init__()

    def encode(self, input: Tensor) -> list[Tensor]:
        raise NotImplementedError

    def decode(self, input: Tensor) -> ta.Any:
        raise NotImplementedError

    def sample(self, batch_size: int, current_device: int, **kwargs) -> Tensor:
        raise NotImplementedError

    def generate(self, x: Tensor, **kwargs) -> Tensor:
        raise NotImplementedError

    @abc.abstractmethod
    def forward(self, *inputs: Tensor) -> Tensor:
        pass

    @abc.abstractmethod
    def loss_function(self, *inputs: ta.Any, **kwargs) -> Tensor:
        pass
