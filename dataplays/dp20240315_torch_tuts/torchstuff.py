"""
2.2.1
"""
import typing as ta

import torch.nn


Module: ta.TypeAlias = torch.nn.Module
Tensor: ta.TypeAlias = torch.Tensor
Parameter: ta.TypeAlias = torch.nn.Parameter

T = ta.TypeVar('T', bound=Module)


class ModuleProtocol(ta.Protocol):
    dump_patches: bool = False

    training: bool
    call_super_init: bool = False

    def forward(self, *input: ta.Any) -> None: ...

    def register_buffer(self, name: str, tensor: ta.Optional[Tensor], persistent: bool = True) -> None: ...

    def register_parameter(self, name: str, param: ta.Optional[Parameter]) -> None: ...

    def add_module(self, name: str, module: ta.Optional[Module]) -> None: ...

    def register_module(self, name: str, module: ta.Optional[Module]) -> None: ...

    def get_submodule(self, target: str) -> Module: ...

    def get_parameter(self, target: str) -> 'Parameter': ...

    def get_buffer(self, target: str) -> 'Tensor': ...

    def get_extra_state(self) -> ta.Any:

    def set_extra_state(self, state: ta.Any):

    def apply(self: T, fn: ta.Callable[[Module], None]) -> T:

    def cuda(self: T, device: ta.Optional[ta.Union[int, device]] = None) -> T:

    def ipu(self: T, device: ta.Optional[ta.Union[int, device]] = None) -> T:

    def xpu(self: T, device: ta.Optional[ta.Union[int, device]] = None) -> T:

    def cpu(self: T) -> T:

    def type(self: T, dst_type: ta.Union[dtype, str]) -> T:

    def float(self: T) -> T:

    def double(self: T) -> T:

    def half(self: T) -> T:

    def bfloat16(self: T) -> T:

    def to_empty(self: T, *, device: ta.Optional[DeviceLikeType], recurse: bool = True) -> T:

    @ta.overload
    def to(self, device: ta.Optional[DeviceLikeType] = ..., dtype: ta.Optional[ta.Union[dtype, str]] = ...,
           non_blocking: bool = ...) -> Self:
        ...

    @ta.overload
    def to(self, dtype: ta.Union[dtype, str], non_blocking: bool = ...) -> Self:
        ...

    @ta.overload
    def to(self, tensor: Tensor, non_blocking: bool = ...) -> Self:
        ...

    def to(self, *args, **kwargs):

    def register_full_backward_pre_hook(
            self,
            hook: ta.Callable[[Module, _grad_t], ta.Union[None, _grad_t]],
            prepend: bool = False,
    ) -> RemovableHandle:

    def register_full_backward_hook(
            self,
            hook: ta.Callable[[Module, _grad_t, _grad_t], ta.Union[None, _grad_t]],
            prepend: bool = False,
    ) -> RemovableHandle:


    def register_forward_pre_hook(
            self,
            hook: ta.Union[
                ta.Callable[[T, tuple[ta.Any, ...]], ta.Optional[ta.Any]],
                ta.Callable[[T, tuple[ta.Any, ...], dict[str, ta.Any]], ta.Optional[tuple[ta.Any, dict[str, ta.Any]]]],
            ],
            *,
            prepend: bool = False,
            with_kwargs: bool = False,
    ) -> RemovableHandle:

    def register_forward_hook(
            self,
            hook: ta.Union[
                ta.Callable[[T, tuple[ta.Any, ...], ta.Any], ta.Optional[ta.Any]],
                ta.Callable[[T, tuple[ta.Any, ...], dict[str, ta.Any], ta.Any], ta.Optional[ta.Any]],
            ],
            *,
            prepend: bool = False,
            with_kwargs: bool = False,
            always_call: bool = False,
    ) -> RemovableHandle:

    __call__ : ta.Callable[..., ta.Any] = _wrapped_call_impl

    def register_state_dict_pre_hook(self, hook):

    # The user can pass an optional arbitrary mappable object to `state_dict`, in which case `state_dict` returns
    # back that same object. But if they pass nothing, an `OrderedDict` is created and returned.
    T_destination = TypeVar('T_destination', bound=dict[str, ta.Any])

    @ta.overload
    def state_dict(self, *, destination: T_destination, prefix: str = ..., keep_vars: bool = ...) -> T_destination:
        ...

    @ta.overload
    def state_dict(self, *, prefix: str = ..., keep_vars: bool = ...) -> dict[str, ta.Any]:
        ...

    def state_dict(self, *args, destination=None, prefix='', keep_vars=False):

    def register_load_state_dict_post_hook(self, hook):

    def load_state_dict(
            self,
            state_dict: ta.Mapping[str, ta.Any],
            strict: bool = True,
            assign: bool = False,
    ) -> None:

    def parameters(self, recurse: bool = True) -> ta.Iterator[Parameter]:

    def named_parameters(
            self,
            prefix: str = '',
            recurse: bool = True,
            remove_duplicate: bool = True
    ) -> ta.Iterator[tuple[str, Parameter]]:

    def buffers(self, recurse: bool = True) -> ta.Iterator[Tensor]:

    def named_buffers(self, prefix: str = '', recurse: bool = True, remove_duplicate: bool = True) -> ta.Iterator[tuple[str, Tensor]]:

    def children(self) -> ta.Iterator[Module]:

    def named_children(self) -> ta.Iterator[tuple[str, Module]]:

    def modules(self) -> ta.Iterator[Module]:

    def named_modules(self, memo: ta.Optional[Set[Module]] = None, prefix: str = '', remove_duplicate: bool = True):

    def train(self: T, mode: bool = True) -> T:

    def eval(self: T) -> T:

    def requires_grad_(self: T, requires_grad: bool = True) -> T:

    def zero_grad(self, set_to_none: bool = True) -> None:

    def share_memory(self: T) -> T:

    def extra_repr(self) -> str:

    def compile(self, *args, **kwargs):
