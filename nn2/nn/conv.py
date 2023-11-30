import math

from ..helpers import all_int
from ..helpers import prod
from ..tensor import Tensor


# TODO: these Conv lines are terrible
def Conv1d(
        in_channels,
        out_channels,
        kernel_size,
        stride=1,
        padding=0,
        dilation=1,
        groups=1,
        bias=True,
):
    return Conv2d(
        in_channels,
        out_channels,
        (kernel_size,),
        stride,
        padding,
        dilation,
        groups,
        bias,
    )


class Conv2d:
    def __init__(
            self,
            in_channels,
            out_channels,
            kernel_size,
            stride=1,
            padding=0,
            dilation=1,
            groups=1,
            bias=True,
    ) -> None:
        super().__init__()

        self.kernel_size = (
            (kernel_size, kernel_size)
            if isinstance(kernel_size, int)
            else tuple(kernel_size)
        )

        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.groups = groups

        self.weight = self.initialize_weight(out_channels, in_channels, groups)
        assert all_int(self.weight.shape), "does not support symbolic shape"

        bound = 1 / math.sqrt(prod(self.weight.shape[1:]))
        self.bias = (
            Tensor.uniform(out_channels, low=-bound, high=bound) if bias else None
        )

    def __call__(self, x: Tensor):
        return x.conv2d(
            self.weight,
            self.bias,
            padding=self.padding,
            stride=self.stride,
            dilation=self.dilation,
            groups=self.groups,
        )

    def initialize_weight(self, out_channels, in_channels, groups):
        return Tensor.kaiming_uniform(
            out_channels, in_channels // groups, *self.kernel_size, a=math.sqrt(5)
        )


def ConvTranspose1d(
        in_channels,
        out_channels,
        kernel_size,
        stride=1,
        padding=0,
        output_padding=0,
        dilation=1,
        groups=1,
        bias=True,
):
    return ConvTranspose2d(
        in_channels,
        out_channels,
        (kernel_size,),
        stride,
        padding,
        output_padding,
        dilation,
        groups,
        bias,
    )


class ConvTranspose2d(Conv2d):
    def __init__(
            self,
            in_channels,
            out_channels,
            kernel_size,
            stride=1,
            padding=0,
            output_padding=0,
            dilation=1,
            groups=1,
            bias=True,
    ) -> None:
        super().__init__(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding,
            dilation,
            groups,
            bias,
        )
        self.output_padding = output_padding

    def __call__(self, x: Tensor):
        return x.conv_transpose2d(
            self.weight,
            self.bias,
            padding=self.padding,
            output_padding=self.output_padding,
            stride=self.stride,
            dilation=self.dilation,
            groups=self.groups,
        )

    def initialize_weight(self, out_channels, in_channels, groups):
        return Tensor.kaiming_uniform(
            in_channels, out_channels // groups, *self.kernel_size, a=math.sqrt(5)
        )
