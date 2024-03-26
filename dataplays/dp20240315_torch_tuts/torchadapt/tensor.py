"""
2.2.1
"""
import typing as ta

import torch.utils.hooks


DeviceLikeType: ta.TypeAlias = ta.Union[str, torch.device, int]
Parameter: ta.TypeAlias = torch.nn.Parameter
RemovableHandle: ta.TypeAlias = torch.utils.hooks.RemovableHandle
Tensor: ta.TypeAlias = torch.Tensor
device: ta.TypeAlias = torch.device
dtype: ta.TypeAlias = torch.dtype


class TensorProtocol(ta.Protocol):
    pass


"""
H
T
__abs__
__add__
__and__
__array__
__array_priority__
__array_wrap__
__bool__
__class__
__complex__
__contains__
__cuda_array_interface__
__deepcopy__
__delattr__
__delitem__
__dict__
__dir__
__div__
__dlpack__
__dlpack_device__
__doc__
__eq__
__float__
__floordiv__
__format__
__ge__
__getattribute__
__getitem__
__getstate__
__gt__
__hash__
__iadd__
__iand__
__idiv__
__ifloordiv__
__ilshift__
__imod__
__imul__
__index__
__init__
__init_subclass__
__int__
__invert__
__ior__
__ipow__
__irshift__
__isub__
__iter__
__itruediv__
__ixor__
__le__
__len__
__long__
__lshift__
__lt__
__matmul__
__mod__
__module__
__mul__
__ne__
__neg__
__new__
__nonzero__
__or__
__pos__
__pow__
__radd__
__rand__
__rdiv__
__reduce__
__reduce_ex__
__repr__
__reversed__
__rfloordiv__
__rlshift__
__rmatmul__
__rmod__
__rmul__
__ror__
__rpow__
__rrshift__
__rshift__
__rsub__
__rtruediv__
__rxor__
__setattr__
__setitem__
__setstate__
__sizeof__
__str__
__sub__
__subclasshook__
__torch_dispatch__
__torch_function__
__truediv__
__weakref__
__xor__
_addmm_activation
_autocast_to_full_precision
_autocast_to_reduced_precision
_backward_hooks
_base
_cdata
_coalesced_
_conj
_conj_physical
_dimI
_dimV
_fix_weakref
_grad
_grad_fn
_has_symbolic_sizes_strides
_indices
_is_all_true
_is_any_true
_is_view
_is_zerotensor
_make_subclass
_make_wrapper_subclass
_neg_view
_nested_tensor_size
_nested_tensor_storage_offsets
_nested_tensor_strides
_nnz
_post_accumulate_grad_hooks
_python_dispatch
_reduce_ex_internal
_sparse_mask_projection
_to_dense
_to_sparse
_to_sparse_bsc
_to_sparse_bsr
_to_sparse_csc
_to_sparse_csr
_typed_storage
_update_names
_values
_version
_view_func
_view_func_unsafe
abs() -> Tensor
abs_() -> Tensor
absolute() -> Tensor
absolute_() -> Tensor
acos() -> Tensor
acos_() -> Tensor
acosh() -> Tensor
acosh_() -> Tensor
add(other, *, alpha=1) -> Tensor
add_(other, *, alpha=1) -> Tensor
addbmm(batch1, batch2, *, beta=1, alpha=1) -> Tensor
addbmm_(batch1, batch2, *, beta=1, alpha=1) -> Tensor
addcdiv(tensor1, tensor2, *, value=1) -> Tensor
addcdiv_(tensor1, tensor2, *, value=1) -> Tensor
addcmul(tensor1, tensor2, *, value=1) -> Tensor
addcmul_(tensor1, tensor2, *, value=1) -> Tensor
addmm(mat1, mat2, *, beta=1, alpha=1) -> Tensor
addmm_(mat1, mat2, *, beta=1, alpha=1) -> Tensor
addmv(mat, vec, *, beta=1, alpha=1) -> Tensor
addmv_(mat, vec, *, beta=1, alpha=1) -> Tensor
addr(vec1, vec2, *, beta=1, alpha=1) -> Tensor
addr_(vec1, vec2, *, beta=1, alpha=1) -> Tensor
adjoint() -> Tensor
align_as(other) -> Tensor
align_to
all(dim=None, keepdim=False) -> Tensor
allclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor
amax(dim=None, keepdim=False) -> Tensor
amin(dim=None, keepdim=False) -> Tensor
aminmax(*, dim=None, keepdim=False) -> (Tensor min, Tensor max)
angle() -> Tensor
any(dim=None, keepdim=False) -> Tensor
apply_(callable) -> Tensor
arccos() -> Tensor
arccos_() -> Tensor
arccosh
arccosh_
arcsin() -> Tensor
arcsin_() -> Tensor
arcsinh() -> Tensor
arcsinh_() -> Tensor
arctan() -> Tensor
arctan2(other) -> Tensor
arctan2_
arctan_() -> Tensor
arctanh() -> Tensor
arctanh_(other) -> Tensor
argmax(dim=None, keepdim=False) -> LongTensor
argmin(dim=None, keepdim=False) -> LongTensor
argsort(dim=-1, descending=False) -> LongTensor
argwhere() -> Tensor
as_strided(size, stride, storage_offset=None) -> Tensor
as_strided_(size, stride, storage_offset=None) -> Tensor
as_strided_scatter(src, size, stride, storage_offset=None) -> Tensor
as_subclass(cls) -> Tensor
asin() -> Tensor
asin_() -> Tensor
asinh() -> Tensor
asinh_() -> Tensor
atan() -> Tensor
atan2(other) -> Tensor
atan2_(other) -> Tensor
atan_() -> Tensor
atanh() -> Tensor
atanh_(other) -> Tensor
backward
baddbmm(batch1, batch2, *, beta=1, alpha=1) -> Tensor
baddbmm_(batch1, batch2, *, beta=1, alpha=1) -> Tensor
bernoulli(*, generator=None) -> Tensor
bernoulli_(p=0.5, *, generator=None) -> Tensor
bfloat16(memory_format=torch.preserve_format) -> Tensor
bincount(weights=None, minlength=0) -> Tensor
bitwise_and() -> Tensor
bitwise_and_() -> Tensor
bitwise_left_shift(other) -> Tensor
bitwise_left_shift_(other) -> Tensor
bitwise_not() -> Tensor
bitwise_not_() -> Tensor
bitwise_or() -> Tensor
bitwise_or_() -> Tensor
bitwise_right_shift(other) -> Tensor
bitwise_right_shift_(other) -> Tensor
bitwise_xor() -> Tensor
bitwise_xor_() -> Tensor
bmm(batch2) -> Tensor
bool(memory_format=torch.preserve_format) -> Tensor
broadcast_to(shape) -> Tensor
byte(memory_format=torch.preserve_format) -> Tensor
cauchy_(median=0, sigma=1, *, generator=None) -> Tensor
ccol_indices
cdouble(memory_format=torch.preserve_format) -> Tensor
ceil() -> Tensor
ceil_() -> Tensor
cfloat(memory_format=torch.preserve_format) -> Tensor
chalf(memory_format=torch.preserve_format) -> Tensor
char(memory_format=torch.preserve_format) -> Tensor
cholesky(upper=False) -> Tensor
cholesky_inverse(upper=False) -> Tensor
cholesky_solve(input2, upper=False) -> Tensor
chunk(chunks, dim=0) -> List of Tensors
clamp(min=None, max=None) -> Tensor
clamp_(min=None, max=None) -> Tensor
clamp_max_
clamp_min_
clip(min=None, max=None) -> Tensor
clip_(min=None, max=None) -> Tensor
clone(*, memory_format=torch.preserve_format) -> Tensor
coalesce() -> Tensor
col_indices() -> IntTensor
conj() -> Tensor
conj_physical() -> Tensor
conj_physical_() -> Tensor
contiguous(memory_format=torch.contiguous_format) -> Tensor
copy_(src, non_blocking=False) -> Tensor
copysign(other) -> Tensor
copysign_(other) -> Tensor
corrcoef() -> Tensor
cos() -> Tensor
cos_() -> Tensor
cosh() -> Tensor
cosh_() -> Tensor
count_nonzero(dim=None) -> Tensor
cov(*, correction=1, fweights=None, aweights=None) -> Tensor
cpu(memory_format=torch.preserve_format) -> Tensor
cross(other, dim=None) -> Tensor
crow_indices() -> IntTensor
cuda(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
cummax(dim) -> (Tensor, Tensor)
cummin(dim) -> (Tensor, Tensor)
cumprod(dim, dtype=None) -> Tensor
cumprod_(dim, dtype=None) -> Tensor
cumsum(dim, dtype=None) -> Tensor
cumsum_(dim, dtype=None) -> Tensor
data
data_ptr() -> int
deg2rad() -> Tensor
deg2rad_() -> Tensor
dense_dim() -> int
dequantize() -> Tensor
det() -> Tensor
detach_
device
diag(diagonal=0) -> Tensor
diag_embed(offset=0, dim1=-2, dim2=-1) -> Tensor
diagflat(offset=0) -> Tensor
diagonal(offset=0, dim1=0, dim2=1) -> Tensor
diagonal_scatter(src, offset=0, dim1=0, dim2=1) -> Tensor
diff(n=1, dim=-1, prepend=None, append=None) -> Tensor
digamma() -> Tensor
digamma_() -> Tensor
dim() -> int
dim_order
dist(other, p=2) -> Tensor
div(value, *, rounding_mode=None) -> Tensor
div_(value, *, rounding_mode=None) -> Tensor
divide(value, *, rounding_mode=None) -> Tensor
divide_(value, *, rounding_mode=None) -> Tensor
dot(other) -> Tensor
double(memory_format=torch.preserve_format) -> Tensor
dsplit(split_size_or_sections) -> List of Tensors
dtype
eig
element_size() -> int
eq(other) -> Tensor
eq_(other) -> Tensor
equal(other) -> bool
erf() -> Tensor
erf_() -> Tensor
erfc() -> Tensor
erfc_() -> Tensor
erfinv() -> Tensor
erfinv_() -> Tensor
exp() -> Tensor
exp2() -> Tensor
exp2_() -> Tensor
exp_() -> Tensor
expand(*sizes) -> Tensor
expand_as(other) -> Tensor
expm1() -> Tensor
expm1_() -> Tensor
exponential_(lambd=1, *, generator=None) -> Tensor
fill_(value) -> Tensor
fill_diagonal_(fill_value, wrap=False) -> Tensor
fix() -> Tensor
fix_() -> Tensor
flatten(start_dim=0, end_dim=-1) -> Tensor
flip(dims) -> Tensor
fliplr() -> Tensor
flipud() -> Tensor
float(memory_format=torch.preserve_format) -> Tensor
float_power(exponent) -> Tensor
float_power_(exponent) -> Tensor
floor() -> Tensor
floor_() -> Tensor
floor_divide(value) -> Tensor
floor_divide_(value) -> Tensor
fmax(other) -> Tensor
fmin(other) -> Tensor
fmod(divisor) -> Tensor
fmod_(divisor) -> Tensor
frac() -> Tensor
frac_() -> Tensor
frexp(input) -> (Tensor mantissa, Tensor exponent)
gather(dim, index) -> Tensor
gcd(other) -> Tensor
gcd_(other) -> Tensor
ge(other) -> Tensor
ge_(other) -> Tensor
geometric_(p, *, generator=None) -> Tensor
geqrf() -> (Tensor, Tensor)
ger(vec2) -> Tensor
get_device() -> Device ordinal (Integer)
grad
grad_fn
greater(other) -> Tensor
greater_(other) -> Tensor
greater_equal(other) -> Tensor
greater_equal_(other) -> Tensor
gt(other) -> Tensor
gt_(other) -> Tensor
half(memory_format=torch.preserve_format) -> Tensor
hardshrink(lambd=0.5) -> Tensor
has_names
heaviside(values) -> Tensor
heaviside_(values) -> Tensor
histc(bins=100, min=0, max=0) -> Tensor
histogram(input, bins, *, range=None, weight=None, density=False) -> (Tensor, Tensor)
hsplit(split_size_or_sections) -> List of Tensors
hypot(other) -> Tensor
hypot_(other) -> Tensor
i0() -> Tensor
i0_() -> Tensor
igamma(other) -> Tensor
igamma_(other) -> Tensor
igammac(other) -> Tensor
igammac_(other) -> Tensor
imag
index_add(dim, index, source, *, alpha=1) -> Tensor
index_add_(dim, index, source, *, alpha=1) -> Tensor
index_copy(dim, index, tensor2) -> Tensor
index_copy_(dim, index, tensor) -> Tensor
index_fill(dim, index, value) -> Tensor
index_fill_(dim, index, value) -> Tensor
index_put(indices, values, accumulate=False) -> Tensor
index_put_(indices, values, accumulate=False) -> Tensor
index_reduce
index_reduce_(dim, index, source, reduce, *, include_self=True) -> Tensor
index_select(dim, index) -> Tensor
indices() -> Tensor
inner(other) -> Tensor
int(memory_format=torch.preserve_format) -> Tensor
int_repr() -> Tensor
inverse() -> Tensor
ipu(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
is_coalesced() -> bool
is_complex() -> bool
is_conj() -> bool
is_contiguous(memory_format=torch.contiguous_format) -> bool
is_cpu
is_cuda
is_distributed
is_floating_point() -> bool
is_inference() -> bool
is_ipu
is_leaf
is_meta
is_mkldnn
is_mps
is_mtia
is_neg() -> bool
is_nested
is_nonzero
is_ort
is_pinned
is_quantized
is_same_size
is_set_to(tensor) -> bool
is_shared
is_signed() -> bool
is_sparse
is_sparse_csr
is_vulkan
is_xla
is_xpu
isclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor
isfinite() -> Tensor
isinf() -> Tensor
isnan() -> Tensor
isneginf() -> Tensor
isposinf() -> Tensor
isreal() -> Tensor
istft(n_fft, hop_length=None, win_length=None, window=None,
item() -> number
itemsize
kron(other) -> Tensor
kthvalue(k, dim=None, keepdim=False) -> (Tensor, LongTensor)
layout
lcm(other) -> Tensor
lcm_(other) -> Tensor
ldexp(other) -> Tensor
ldexp_(other) -> Tensor
le(other) -> Tensor
le_(other) -> Tensor
lerp(end, weight) -> Tensor
lerp_(end, weight) -> Tensor
less
less_(other) -> Tensor
less_equal(other) -> Tensor
less_equal_(other) -> Tensor
lgamma() -> Tensor
lgamma_() -> Tensor
log() -> Tensor
log10() -> Tensor
log10_() -> Tensor
log1p() -> Tensor
log1p_() -> Tensor
log2() -> Tensor
log2_() -> Tensor
log_() -> Tensor
log_normal_(mean=1, std=2, *, generator=None)
log_softmax
logaddexp(other) -> Tensor
logaddexp2(other) -> Tensor
logcumsumexp(dim) -> Tensor
logdet() -> Tensor
logical_and() -> Tensor
logical_and_() -> Tensor
logical_not() -> Tensor
logical_not_() -> Tensor
logical_or() -> Tensor
logical_or_() -> Tensor
logical_xor() -> Tensor
logical_xor_() -> Tensor
logit() -> Tensor
logit_() -> Tensor
logsumexp(dim, keepdim=False) -> Tensor
long(memory_format=torch.preserve_format) -> Tensor
lstsq
lt(other) -> Tensor
lt_(other) -> Tensor
lu
lu_solve(LU_data, LU_pivots) -> Tensor
mH
mT
map2_
map_(tensor, callable)
masked_fill(mask, value) -> Tensor
masked_fill_(mask, value)
masked_scatter(mask, tensor) -> Tensor
masked_scatter_(mask, source)
masked_select(mask) -> Tensor
matmul(tensor2) -> Tensor
matrix_exp() -> Tensor
matrix_power(n) -> Tensor
max(dim=None, keepdim=False) -> Tensor or (Tensor, Tensor)
maximum(other) -> Tensor
mean(dim=None, keepdim=False, *, dtype=None) -> Tensor
median(dim=None, keepdim=False) -> (Tensor, LongTensor)
min(dim=None, keepdim=False) -> Tensor or (Tensor, Tensor)
minimum(other) -> Tensor
mm(mat2) -> Tensor
mode(dim=None, keepdim=False) -> (Tensor, LongTensor)
moveaxis(source, destination) -> Tensor
movedim(source, destination) -> Tensor
msort() -> Tensor
mul(value) -> Tensor
mul_(value) -> Tensor
multinomial(num_samples, replacement=False, *, generator=None) -> Tensor
multiply(value) -> Tensor
multiply_(value) -> Tensor
mv(vec) -> Tensor
mvlgamma(p) -> Tensor
mvlgamma_(p) -> Tensor
name
names
nan_to_num(nan=0.0, posinf=None, neginf=None) -> Tensor
nan_to_num_(nan=0.0, posinf=None, neginf=None) -> Tensor
nanmean(dim=None, keepdim=False, *, dtype=None) -> Tensor
nanmedian(dim=None, keepdim=False) -> (Tensor, LongTensor)
nanquantile(q, dim=None, keepdim=False, *, interpolation='linear') -> Tensor
nansum(dim=None, keepdim=False, dtype=None) -> Tensor
narrow(dimension, start, length) -> Tensor
narrow_copy(dimension, start, length) -> Tensor
nbytes
ndim
ndimension() -> int
ne(other) -> Tensor
ne_(other) -> Tensor
neg() -> Tensor
neg_() -> Tensor
negative() -> Tensor
negative_() -> Tensor
nelement() -> int
new
new_empty(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_empty_strided(size, stride, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_full(size, fill_value, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_ones(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_tensor(data, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_zeros(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
nextafter(other) -> Tensor
nextafter_(other) -> Tensor
nonzero() -> LongTensor
nonzero_static(input, *, size, fill_value=-1) -> Tensor
norm(p=2, dim=None, keepdim=False) -> Tensor
normal_(mean=0, std=1, *, generator=None) -> Tensor
not_equal(other) -> Tensor
not_equal_(other) -> Tensor
numel() -> int
numpy(*, force=False) -> numpy.ndarray
orgqr(input2) -> Tensor
ormqr(input2, input3, left=True, transpose=False) -> Tensor
outer(vec2) -> Tensor
output_nr
permute(*dims) -> Tensor
pin_memory() -> Tensor
pinverse() -> Tensor
polygamma(n) -> Tensor
polygamma_(n) -> Tensor
positive() -> Tensor
pow(exponent) -> Tensor
pow_(exponent) -> Tensor
prelu
prod(dim=None, keepdim=False, dtype=None) -> Tensor
put(input, index, source, accumulate=False) -> Tensor
put_(index, source, accumulate=False) -> Tensor
q_per_channel_axis() -> int
q_per_channel_scales() -> Tensor
q_per_channel_zero_points() -> Tensor
q_scale() -> float
q_zero_point() -> int
qr(some=True) -> (Tensor, Tensor)
qscheme() -> torch.qscheme
quantile(q, dim=None, keepdim=False, *, interpolation='linear') -> Tensor
rad2deg() -> Tensor
rad2deg_() -> Tensor
random_(from=0, to=None, *, generator=None) -> Tensor
ravel() -> Tensor
real
reciprocal() -> Tensor
reciprocal_() -> Tensor
record_stream(stream)
refine_names
register_hook
register_post_accumulate_grad_hook
reinforce
relu
relu_
remainder(divisor) -> Tensor
remainder_(divisor) -> Tensor
rename_
renorm(p, dim, maxnorm) -> Tensor
renorm_(p, dim, maxnorm) -> Tensor
repeat(*sizes) -> Tensor
repeat_interleave(repeats, dim=None, *, output_size=None) -> Tensor
requires_grad
requires_grad_(requires_grad=True) -> Tensor
reshape(*shape) -> Tensor
reshape_as(other) -> Tensor
resize_
resize_(*sizes, memory_format=torch.contiguous_format) -> Tensor
resize_as
resize_as_(tensor, memory_format=torch.contiguous_format) -> Tensor
resize_as_sparse_
resolve_conj() -> Tensor
resolve_neg() -> Tensor
retain_grad() -> None
retains_grad
roll(shifts, dims) -> Tensor
rot90(k, dims) -> Tensor
round(decimals=0) -> Tensor
round_(decimals=0) -> Tensor
row_indices
rsqrt() -> Tensor
rsqrt_() -> Tensor
scatter(dim, index, src) -> Tensor
scatter_(dim, index, src, reduce=None) -> Tensor
scatter_add(dim, index, src) -> Tensor
scatter_add_(dim, index, src) -> Tensor
scatter_reduce(dim, index, src, reduce, *, include_self=True) -> Tensor
scatter_reduce_(dim, index, src, reduce, *, include_self=True) -> Tensor
select(dim, index) -> Tensor
select_scatter(src, dim, index) -> Tensor
set_(source=None, storage_offset=0, size=None, stride=None) -> Tensor
sgn() -> Tensor
sgn_() -> Tensor
shape() -> torch.Size
share_memory_
short(memory_format=torch.preserve_format) -> Tensor
sigmoid() -> Tensor
sigmoid_() -> Tensor
sign() -> Tensor
sign_() -> Tensor
signbit() -> Tensor
sin() -> Tensor
sin_() -> Tensor
sinc() -> Tensor
sinc_() -> Tensor
sinh() -> Tensor
sinh_() -> Tensor
size(dim=None) -> torch.Size or int
slice_scatter(src, dim=0, start=None, end=None, step=1) -> Tensor
slogdet() -> (Tensor, Tensor)
smm(mat) -> Tensor
softmax(dim) -> Tensor
solve
sort(dim=-1, descending=False) -> (Tensor, LongTensor)
sparse_dim() -> int
sparse_mask(mask) -> Tensor
sparse_resize_(size, sparse_dim, dense_dim) -> Tensor
sparse_resize_and_clear_(size, sparse_dim, dense_dim) -> Tensor
split
split_with_sizes
sqrt() -> Tensor
sqrt_() -> Tensor
square() -> Tensor
square_() -> Tensor
squeeze(dim=None) -> Tensor
squeeze_(dim=None) -> Tensor
sspaddmm(mat1, mat2, *, beta=1, alpha=1) -> Tensor
std(dim=None, *, correction=1, keepdim=False) -> Tensor
stft(frame_length, hop, fft_size=None, return_onesided=True, window=None, pad_end=0) -> Tensor
storage
storage_offset() -> int
storage_type
stride(dim) -> tuple or int
sub(other, *, alpha=1) -> Tensor
sub_(other, *, alpha=1) -> Tensor
subtract(other, *, alpha=1) -> Tensor
subtract_(other, *, alpha=1) -> Tensor
sum(dim=None, keepdim=False, dtype=None) -> Tensor
sum_to_size(*size) -> Tensor
svd(some=True, compute_uv=True) -> (Tensor, Tensor, Tensor)
swapaxes(axis0, axis1) -> Tensor
swapaxes_(axis0, axis1) -> Tensor
swapdims(dim0, dim1) -> Tensor
swapdims_(dim0, dim1) -> Tensor
symeig
t() -> Tensor
t_() -> Tensor
take(indices) -> Tensor
take_along_dim(indices, dim) -> Tensor
tan() -> Tensor
tan_() -> Tensor
tanh() -> Tensor
tanh_() -> Tensor
tensor_split(indices_or_sections, dim=0) -> List of Tensors
tile(dims) -> Tensor
to(*args, **kwargs) -> Tensor
to_dense(dtype=None, *, masked_grad=True) -> Tensor
to_mkldnn() -> Tensor
to_padded_tensor(padding, output_size=None) -> Tensor
to_sparse(sparseDims) -> Tensor
to_sparse_bsc(blocksize, dense_dim) -> Tensor
to_sparse_bsr(blocksize, dense_dim) -> Tensor
to_sparse_coo
to_sparse_csc() -> Tensor
to_sparse_csr(dense_dim=None) -> Tensor
tolist() -> list or number
topk(k, dim=None, largest=True, sorted=True) -> (Tensor, LongTensor)
trace() -> Tensor
transpose(dim0, dim1) -> Tensor
transpose_(dim0, dim1) -> Tensor
triangular_solve(A, upper=True, transpose=False, unitriangular=False) -> (Tensor, Tensor)
tril(diagonal=0) -> Tensor
tril_(diagonal=0) -> Tensor
triu(diagonal=0) -> Tensor
triu_(diagonal=0) -> Tensor
true_divide(value) -> Tensor
true_divide_(value) -> Tensor
trunc() -> Tensor
trunc_() -> Tensor
type(dtype=None, non_blocking=False, **kwargs) -> str or Tensor
type_as(tensor) -> Tensor
unbind(dim=0) -> seq
unflatten
unfold(dimension, size, step) -> Tensor
uniform_(from=0, to=1, *, generator=None) -> Tensor
unique
unique_consecutive
unsafe_chunk(chunks, dim=0) -> List of Tensors
unsafe_split(split_size, dim=0) -> List of Tensors
unsafe_split_with_sizes
unsqueeze(dim) -> Tensor
unsqueeze_(dim) -> Tensor
untyped_storage() -> torch.UntypedStorage
values() -> Tensor
var(dim=None, *, correction=1, keepdim=False) -> Tensor
vdot(other) -> Tensor
view(*shape) -> Tensor
view_as(other) -> Tensor
volatile
vsplit(split_size_or_sections) -> List of Tensors
where(condition, y) -> Tensor
xlogy(other) -> Tensor
xlogy_(other) -> Tensor
xpu(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
zero_() -> Tensor
"""
