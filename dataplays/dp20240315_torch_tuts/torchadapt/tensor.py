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
acos_
acos_() -> Tensor
acosh
acosh() -> Tensor
acosh() -> Tensor
acosh_
acosh_() -> Tensor
acosh_() -> Tensor
add
add(other, *, alpha=1) -> Tensor
add_
add_(other, *, alpha=1) -> Tensor
addbmm
addbmm(batch1, batch2, *, beta=1, alpha=1) -> Tensor
addbmm_
addbmm_(batch1, batch2, *, beta=1, alpha=1) -> Tensor
addcdiv
addcdiv(tensor1, tensor2, *, value=1) -> Tensor
addcdiv_
addcdiv_(tensor1, tensor2, *, value=1) -> Tensor
addcmul
addcmul(tensor1, tensor2, *, value=1) -> Tensor
addcmul_
addcmul_(tensor1, tensor2, *, value=1) -> Tensor
addmm
addmm(mat1, mat2, *, beta=1, alpha=1) -> Tensor
addmm_
addmm_(mat1, mat2, *, beta=1, alpha=1) -> Tensor
addmv
addmv(mat, vec, *, beta=1, alpha=1) -> Tensor
addmv_
addmv_(mat, vec, *, beta=1, alpha=1) -> Tensor
addr
addr(vec1, vec2, *, beta=1, alpha=1) -> Tensor
addr_
addr_(vec1, vec2, *, beta=1, alpha=1) -> Tensor
adjoint
adjoint() -> Tensor
align_as
align_as(other) -> Tensor
align_to
all
all(dim=None, keepdim=False) -> Tensor
allclose
allclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor
amax
amax(dim=None, keepdim=False) -> Tensor
amin
amin(dim=None, keepdim=False) -> Tensor
aminmax
aminmax(*, dim=None, keepdim=False) -> (Tensor min, Tensor max)
angle
angle() -> Tensor
any
any(dim=None, keepdim=False) -> Tensor
apply_
apply_(callable) -> Tensor
arccos
arccos() -> Tensor
arccos_
arccos_() -> Tensor
arccosh
arccosh_
arcsin
arcsin() -> Tensor
arcsin_
arcsin_() -> Tensor
arcsinh
arcsinh() -> Tensor
arcsinh_
arcsinh_() -> Tensor
arctan
arctan() -> Tensor
arctan2
arctan2(other) -> Tensor
arctan2_
arctan_
arctan_() -> Tensor
arctanh
arctanh() -> Tensor
arctanh_
arctanh_(other) -> Tensor
argmax
argmax(dim=None, keepdim=False) -> LongTensor
argmin
argmin(dim=None, keepdim=False) -> LongTensor
argsort
argsort(dim=-1, descending=False) -> LongTensor
argwhere
argwhere() -> Tensor
as_strided
as_strided(size, stride, storage_offset=None) -> Tensor
as_strided_
as_strided_(size, stride, storage_offset=None) -> Tensor
as_strided_scatter
as_strided_scatter(src, size, stride, storage_offset=None) -> Tensor
as_subclass
as_subclass(cls) -> Tensor
asin
asin() -> Tensor
asin_
asin_() -> Tensor
asinh
asinh() -> Tensor
asinh_
asinh_() -> Tensor
atan
atan() -> Tensor
atan2
atan2(other) -> Tensor
atan2_
atan2_(other) -> Tensor
atan2_(other) -> Tensor
atan_
atan_() -> Tensor
atanh
atanh() -> Tensor
atanh_
atanh_(other) -> Tensor
backward
baddbmm
baddbmm(batch1, batch2, *, beta=1, alpha=1) -> Tensor
baddbmm_
baddbmm_(batch1, batch2, *, beta=1, alpha=1) -> Tensor
bernoulli
bernoulli(*, generator=None) -> Tensor
bernoulli_
bernoulli_(p=0.5, *, generator=None) -> Tensor
bfloat16
bfloat16(memory_format=torch.preserve_format) -> Tensor
bincount
bincount(weights=None, minlength=0) -> Tensor
bitwise_and
bitwise_and() -> Tensor
bitwise_and_
bitwise_and_() -> Tensor
bitwise_left_shift
bitwise_left_shift(other) -> Tensor
bitwise_left_shift_
bitwise_left_shift_(other) -> Tensor
bitwise_not
bitwise_not() -> Tensor
bitwise_not_
bitwise_not_() -> Tensor
bitwise_or
bitwise_or() -> Tensor
bitwise_or_
bitwise_or_() -> Tensor
bitwise_right_shift
bitwise_right_shift(other) -> Tensor
bitwise_right_shift_
bitwise_right_shift_(other) -> Tensor
bitwise_xor
bitwise_xor() -> Tensor
bitwise_xor_
bitwise_xor_() -> Tensor
bmm
bmm(batch2) -> Tensor
bool
bool(memory_format=torch.preserve_format) -> Tensor
broadcast_to
broadcast_to(shape) -> Tensor
byte
byte(memory_format=torch.preserve_format) -> Tensor
cauchy_
cauchy_(median=0, sigma=1, *, generator=None) -> Tensor
ccol_indices
cdouble
cdouble(memory_format=torch.preserve_format) -> Tensor
ceil
ceil() -> Tensor
ceil_
ceil_() -> Tensor
cfloat
cfloat(memory_format=torch.preserve_format) -> Tensor
chalf
chalf(memory_format=torch.preserve_format) -> Tensor
char
char(memory_format=torch.preserve_format) -> Tensor
cholesky
cholesky(upper=False) -> Tensor
cholesky_inverse
cholesky_inverse(upper=False) -> Tensor
cholesky_solve
cholesky_solve(input2, upper=False) -> Tensor
chunk
chunk(chunks, dim=0) -> List of Tensors
clamp
clamp(min=None, max=None) -> Tensor
clamp_
clamp_(min=None, max=None) -> Tensor
clamp_max
clamp_max_
clamp_min
clamp_min_
clip
clip(min=None, max=None) -> Tensor
clip_
clip_(min=None, max=None) -> Tensor
clone
clone(*, memory_format=torch.preserve_format) -> Tensor
coalesce
coalesce() -> Tensor
col_indices
col_indices() -> IntTensor
conj
conj() -> Tensor
conj_physical
conj_physical() -> Tensor
conj_physical_
conj_physical_() -> Tensor
contiguous
contiguous(memory_format=torch.contiguous_format) -> Tensor
copy_
copy_(src, non_blocking=False) -> Tensor
copysign
copysign(other) -> Tensor
copysign_
copysign_(other) -> Tensor
corrcoef
corrcoef() -> Tensor
cos
cos() -> Tensor
cos_
cos_() -> Tensor
cosh
cosh() -> Tensor
cosh_
cosh_() -> Tensor
count_nonzero
count_nonzero(dim=None) -> Tensor
cov
cov(*, correction=1, fweights=None, aweights=None) -> Tensor
cpu
cpu(memory_format=torch.preserve_format) -> Tensor
cross
cross(other, dim=None) -> Tensor
crow_indices
crow_indices() -> IntTensor
cuda
cuda(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
cummax
cummax(dim) -> (Tensor, Tensor)
cummin
cummin(dim) -> (Tensor, Tensor)
cumprod
cumprod(dim, dtype=None) -> Tensor
cumprod_
cumprod_(dim, dtype=None) -> Tensor
cumsum
cumsum(dim, dtype=None) -> Tensor
cumsum_
cumsum_(dim, dtype=None) -> Tensor
data
data_ptr
data_ptr() -> int
deg2rad
deg2rad() -> Tensor
deg2rad_
deg2rad_() -> Tensor
dense_dim
dense_dim() -> int
dequantize
dequantize() -> Tensor
det
det() -> Tensor
detach
detach_
device
device
diag
diag(diagonal=0) -> Tensor
diag_embed
diag_embed(offset=0, dim1=-2, dim2=-1) -> Tensor
diagflat
diagflat(offset=0) -> Tensor
diagonal
diagonal(offset=0, dim1=0, dim2=1) -> Tensor
diagonal_scatter
diagonal_scatter(src, offset=0, dim1=0, dim2=1) -> Tensor
diff
diff(n=1, dim=-1, prepend=None, append=None) -> Tensor
digamma
digamma() -> Tensor
digamma_
digamma_() -> Tensor
dim
dim() -> int
dim_order
dist
dist(other, p=2) -> Tensor
div
div(value, *, rounding_mode=None) -> Tensor
div_
div_(value, *, rounding_mode=None) -> Tensor
divide
divide(value, *, rounding_mode=None) -> Tensor
divide_
divide_(value, *, rounding_mode=None) -> Tensor
dot
dot(other) -> Tensor
double
double(memory_format=torch.preserve_format) -> Tensor
dsplit
dsplit(split_size_or_sections) -> List of Tensors
dtype
eig
element_size
element_size() -> int
eq
eq(other) -> Tensor
eq_
eq_(other) -> Tensor
equal
equal(other) -> bool
erf
erf() -> Tensor
erf_
erf_() -> Tensor
erfc
erfc() -> Tensor
erfc_
erfc_() -> Tensor
erfinv
erfinv() -> Tensor
erfinv_
erfinv_() -> Tensor
exp
exp() -> Tensor
exp2
exp2() -> Tensor
exp2_
exp2_() -> Tensor
exp_
exp_() -> Tensor
expand
expand(*sizes) -> Tensor
expand_as
expand_as(other) -> Tensor
expm1
expm1() -> Tensor
expm1_
expm1_() -> Tensor
exponential_
exponential_(lambd=1, *, generator=None) -> Tensor
fill_
fill_(value) -> Tensor
fill_diagonal_
fill_diagonal_(fill_value, wrap=False) -> Tensor
fix
fix() -> Tensor
fix_
fix_() -> Tensor
flatten
flatten(start_dim=0, end_dim=-1) -> Tensor
flip
flip(dims) -> Tensor
fliplr
fliplr() -> Tensor
flipud
flipud() -> Tensor
float
float(memory_format=torch.preserve_format) -> Tensor
float_power
float_power(exponent) -> Tensor
float_power_
float_power_(exponent) -> Tensor
floor
floor() -> Tensor
floor_
floor_() -> Tensor
floor_divide
floor_divide(value) -> Tensor
floor_divide_
floor_divide_(value) -> Tensor
fmax
fmax(other) -> Tensor
fmin
fmin(other) -> Tensor
fmod
fmod(divisor) -> Tensor
fmod_
fmod_(divisor) -> Tensor
frac
frac() -> Tensor
frac_
frac_() -> Tensor
frexp
frexp(input) -> (Tensor mantissa, Tensor exponent)
gather
gather(dim, index) -> Tensor
gcd
gcd(other) -> Tensor
gcd_
gcd_(other) -> Tensor
ge
ge(other) -> Tensor
ge_
ge_(other) -> Tensor
geometric_
geometric_(p, *, generator=None) -> Tensor
geqrf
geqrf() -> (Tensor, Tensor)
ger
ger(vec2) -> Tensor
get_device
get_device() -> Device ordinal (Integer)
grad
grad
grad_fn
greater
greater(other) -> Tensor
greater_
greater_(other) -> Tensor
greater_equal
greater_equal(other) -> Tensor
greater_equal_
greater_equal_(other) -> Tensor
gt
gt(other) -> Tensor
gt_
gt_(other) -> Tensor
half
half(memory_format=torch.preserve_format) -> Tensor
hardshrink
hardshrink(lambd=0.5) -> Tensor
has_names
has_names
heaviside
heaviside(values) -> Tensor
heaviside_
heaviside_(values) -> Tensor
histc
histc(bins=100, min=0, max=0) -> Tensor
histogram
histogram(input, bins, *, range=None, weight=None, density=False) -> (Tensor, Tensor)
hsplit
hsplit(split_size_or_sections) -> List of Tensors
hypot
hypot(other) -> Tensor
hypot_
hypot_(other) -> Tensor
i0
i0() -> Tensor
i0_
i0_() -> Tensor
igamma
igamma(other) -> Tensor
igamma_
igamma_(other) -> Tensor
igammac
igammac(other) -> Tensor
igammac_
igammac_(other) -> Tensor
imag
imag
index_add
index_add(dim, index, source, *, alpha=1) -> Tensor
index_add_
index_add_(dim, index, source, *, alpha=1) -> Tensor
index_copy
index_copy(dim, index, tensor2) -> Tensor
index_copy_
index_copy_(dim, index, tensor) -> Tensor
index_fill
index_fill(dim, index, value) -> Tensor
index_fill_
index_fill_(dim, index, value) -> Tensor
index_put
index_put(indices, values, accumulate=False) -> Tensor
index_put_
index_put_(indices, values, accumulate=False) -> Tensor
index_reduce
index_reduce_
index_reduce_(dim, index, source, reduce, *, include_self=True) -> Tensor
index_select
index_select(dim, index) -> Tensor
indices
indices() -> Tensor
inner
inner(other) -> Tensor
int
int(memory_format=torch.preserve_format) -> Tensor
int_repr
int_repr() -> Tensor
inverse
inverse() -> Tensor
ipu
ipu(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
is_coalesced
is_coalesced() -> bool
is_complex
is_complex() -> bool
is_conj
is_conj() -> bool
is_contiguous
is_contiguous(memory_format=torch.contiguous_format) -> bool
is_cpu
is_cpu
is_cuda
is_cuda
is_distributed
is_floating_point
is_floating_point() -> bool
is_inference
is_inference() -> bool
is_ipu
is_ipu
is_leaf
is_leaf
is_meta
is_meta
is_mkldnn
is_mps
is_mps
is_mtia
is_neg
is_neg() -> bool
is_nested
is_nonzero
is_ort
is_pinned
is_pinned
is_quantized
is_quantized
is_same_size
is_set_to
is_set_to(tensor) -> bool
is_shared
is_signed
is_signed() -> bool
is_sparse
is_sparse
is_sparse_csr
is_sparse_csr
is_vulkan
is_xla
is_xla
is_xpu
is_xpu
isclose
isclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor
isfinite
isfinite() -> Tensor
isinf
isinf() -> Tensor
isnan
isnan() -> Tensor
isneginf
isneginf() -> Tensor
isposinf
isposinf() -> Tensor
isreal
isreal() -> Tensor
istft
istft(n_fft, hop_length=None, win_length=None, window=None,
item
item() -> number
itemsize
itemsize
kron
kron(other) -> Tensor
kthvalue
kthvalue(k, dim=None, keepdim=False) -> (Tensor, LongTensor)
layout
lcm
lcm(other) -> Tensor
lcm_
lcm_(other) -> Tensor
ldexp
ldexp(other) -> Tensor
ldexp_
ldexp_(other) -> Tensor
le
le(other) -> Tensor
le_
le_(other) -> Tensor
lerp
lerp(end, weight) -> Tensor
lerp_
lerp_(end, weight) -> Tensor
less
less_
less_(other) -> Tensor
less_equal
less_equal(other) -> Tensor
less_equal_
less_equal_(other) -> Tensor
lgamma
lgamma() -> Tensor
lgamma_
lgamma_() -> Tensor
log
log() -> Tensor
log10
log10() -> Tensor
log10_
log10_() -> Tensor
log1p
log1p() -> Tensor
log1p_
log1p_() -> Tensor
log2
log2() -> Tensor
log2_
log2_() -> Tensor
log_
log_() -> Tensor
log_normal_
log_normal_(mean=1, std=2, *, generator=None)
log_softmax
logaddexp
logaddexp(other) -> Tensor
logaddexp2
logaddexp2(other) -> Tensor
logcumsumexp
logcumsumexp(dim) -> Tensor
logdet
logdet() -> Tensor
logical_and
logical_and() -> Tensor
logical_and_
logical_and_() -> Tensor
logical_not
logical_not() -> Tensor
logical_not_
logical_not_() -> Tensor
logical_or
logical_or() -> Tensor
logical_or_
logical_or_() -> Tensor
logical_xor
logical_xor() -> Tensor
logical_xor_
logical_xor_() -> Tensor
logit
logit() -> Tensor
logit_
logit_() -> Tensor
logsumexp
logsumexp(dim, keepdim=False) -> Tensor
long
long(memory_format=torch.preserve_format) -> Tensor
lstsq
lt
lt(other) -> Tensor
lt(other) -> Tensor
lt_
lt_(other) -> Tensor
lu
lu_solve
lu_solve(LU_data, LU_pivots) -> Tensor
mH
mH
mT
mT
map2_
map_
map_(tensor, callable)
masked_fill
masked_fill(mask, value) -> Tensor
masked_fill_
masked_fill_(mask, value)
masked_scatter
masked_scatter(mask, tensor) -> Tensor
masked_scatter_
masked_scatter_(mask, source)
masked_select
masked_select(mask) -> Tensor
matmul
matmul(tensor2) -> Tensor
matrix_exp
matrix_exp() -> Tensor
matrix_power
matrix_power(n) -> Tensor
max
max(dim=None, keepdim=False) -> Tensor or (Tensor, Tensor)
maximum
maximum(other) -> Tensor
mean
mean(dim=None, keepdim=False, *, dtype=None) -> Tensor
median
median(dim=None, keepdim=False) -> (Tensor, LongTensor)
min
min(dim=None, keepdim=False) -> Tensor or (Tensor, Tensor)
minimum
minimum(other) -> Tensor
mm
mm(mat2) -> Tensor
mode
mode(dim=None, keepdim=False) -> (Tensor, LongTensor)
moveaxis
moveaxis(source, destination) -> Tensor
movedim
movedim(source, destination) -> Tensor
msort
msort() -> Tensor
mul
mul(value) -> Tensor
mul_
mul_(value) -> Tensor
multinomial
multinomial(num_samples, replacement=False, *, generator=None) -> Tensor
multiply
multiply(value) -> Tensor
multiply_
multiply_(value) -> Tensor
mv
mv(vec) -> Tensor
mvlgamma
mvlgamma(p) -> Tensor
mvlgamma_
mvlgamma_(p) -> Tensor
name
names
names
nan_to_num
nan_to_num(nan=0.0, posinf=None, neginf=None) -> Tensor
nan_to_num_
nan_to_num_(nan=0.0, posinf=None, neginf=None) -> Tensor
nanmean
nanmean(dim=None, keepdim=False, *, dtype=None) -> Tensor
nanmedian
nanmedian(dim=None, keepdim=False) -> (Tensor, LongTensor)
nanquantile
nanquantile(q, dim=None, keepdim=False, *, interpolation='linear') -> Tensor
nansum
nansum(dim=None, keepdim=False, dtype=None) -> Tensor
narrow
narrow(dimension, start, length) -> Tensor
narrow_copy
narrow_copy(dimension, start, length) -> Tensor
nbytes
nbytes
ndim
ndim
ndimension
ndimension() -> int
ne
ne(other) -> Tensor
ne_
ne_(other) -> Tensor
neg
neg() -> Tensor
neg_
neg_() -> Tensor
negative
negative() -> Tensor
negative_
negative_() -> Tensor
nelement
nelement() -> int
new
new_empty
new_empty(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_empty_strided
new_empty_strided(size, stride, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_full
new_full(size, fill_value, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_ones
new_ones(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_tensor
new_tensor(data, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_zeros
new_zeros(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
nextafter
nextafter(other) -> Tensor
nextafter_
nextafter_(other) -> Tensor
nonzero
nonzero() -> LongTensor
nonzero_static
nonzero_static(input, *, size, fill_value=-1) -> Tensor
norm
norm(p=2, dim=None, keepdim=False) -> Tensor
normal_
normal_(mean=0, std=1, *, generator=None) -> Tensor
not_equal
not_equal(other) -> Tensor
not_equal_
not_equal_(other) -> Tensor
numel
numel() -> int
numpy
numpy(*, force=False) -> numpy.ndarray
orgqr
orgqr(input2) -> Tensor
ormqr
ormqr(input2, input3, left=True, transpose=False) -> Tensor
outer
outer(vec2) -> Tensor
output_nr
permute
permute(*dims) -> Tensor
pin_memory
pin_memory() -> Tensor
pinverse
pinverse() -> Tensor
polygamma
polygamma(n) -> Tensor
polygamma_
polygamma_(n) -> Tensor
positive
positive() -> Tensor
pow
pow(exponent) -> Tensor
pow_
pow_(exponent) -> Tensor
prelu
prod
prod(dim=None, keepdim=False, dtype=None) -> Tensor
put
put(input, index, source, accumulate=False) -> Tensor
put_
put_(index, source, accumulate=False) -> Tensor
q_per_channel_axis
q_per_channel_axis() -> int
q_per_channel_scales
q_per_channel_scales() -> Tensor
q_per_channel_zero_points
q_per_channel_zero_points() -> Tensor
q_scale
q_scale() -> float
q_zero_point
q_zero_point() -> int
qr
qr(some=True) -> (Tensor, Tensor)
qscheme
qscheme() -> torch.qscheme
quantile
quantile(q, dim=None, keepdim=False, *, interpolation='linear') -> Tensor
rad2deg
rad2deg() -> Tensor
rad2deg_
rad2deg_() -> Tensor
random_
random_(from=0, to=None, *, generator=None) -> Tensor
ravel
ravel() -> Tensor
real
real
reciprocal
reciprocal() -> Tensor
reciprocal_
reciprocal_() -> Tensor
record_stream
record_stream(stream)
refine_names
register_hook
register_post_accumulate_grad_hook
reinforce
relu
relu_
remainder
remainder(divisor) -> Tensor
remainder_
remainder_(divisor) -> Tensor
rename
rename_
renorm
renorm(p, dim, maxnorm) -> Tensor
renorm_
renorm_(p, dim, maxnorm) -> Tensor
repeat
repeat(*sizes) -> Tensor
repeat_interleave
repeat_interleave(repeats, dim=None, *, output_size=None) -> Tensor
requires_grad
requires_grad
requires_grad_
requires_grad_(requires_grad=True) -> Tensor
reshape
reshape(*shape) -> Tensor
reshape_as
reshape_as(other) -> Tensor
resize
resize_
resize_(*sizes, memory_format=torch.contiguous_format) -> Tensor
resize_as
resize_as_
resize_as_(tensor, memory_format=torch.contiguous_format) -> Tensor
resize_as_sparse_
resolve_conj
resolve_conj() -> Tensor
resolve_neg
resolve_neg() -> Tensor
retain_grad
retain_grad() -> None
retains_grad
retains_grad
roll
roll(shifts, dims) -> Tensor
rot90
rot90(k, dims) -> Tensor
round
round(decimals=0) -> Tensor
round_
round_(decimals=0) -> Tensor
row_indices
rsqrt
rsqrt() -> Tensor
rsqrt_
rsqrt_() -> Tensor
scatter
scatter(dim, index, src) -> Tensor
scatter_
scatter_(dim, index, src, reduce=None) -> Tensor
scatter_add
scatter_add(dim, index, src) -> Tensor
scatter_add_
scatter_add_(dim, index, src) -> Tensor
scatter_reduce
scatter_reduce(dim, index, src, reduce, *, include_self=True) -> Tensor
scatter_reduce_
scatter_reduce_(dim, index, src, reduce, *, include_self=True) -> Tensor
select
select(dim, index) -> Tensor
select_scatter
select_scatter(src, dim, index) -> Tensor
set_
set_(source=None, storage_offset=0, size=None, stride=None) -> Tensor
sgn
sgn() -> Tensor
sgn_
sgn_() -> Tensor
shape
shape() -> torch.Size
share_memory_
short
short(memory_format=torch.preserve_format) -> Tensor
sigmoid
sigmoid() -> Tensor
sigmoid_
sigmoid_() -> Tensor
sign
sign() -> Tensor
sign_
sign_() -> Tensor
signbit
signbit() -> Tensor
sin
sin() -> Tensor
sin_
sin_() -> Tensor
sinc
sinc() -> Tensor
sinc_
sinc_() -> Tensor
sinh
sinh() -> Tensor
sinh_
sinh_() -> Tensor
size
size(dim=None) -> torch.Size or int
slice_scatter
slice_scatter(src, dim=0, start=None, end=None, step=1) -> Tensor
slogdet
slogdet() -> (Tensor, Tensor)
smm
smm(mat) -> Tensor
softmax
softmax(dim) -> Tensor
solve
sort
sort(dim=-1, descending=False) -> (Tensor, LongTensor)
sparse_dim
sparse_dim() -> int
sparse_mask
sparse_mask(mask) -> Tensor
sparse_resize_
sparse_resize_(size, sparse_dim, dense_dim) -> Tensor
sparse_resize_and_clear_
sparse_resize_and_clear_(size, sparse_dim, dense_dim) -> Tensor
split
split_with_sizes
sqrt
sqrt() -> Tensor
sqrt_
sqrt_() -> Tensor
square
square() -> Tensor
square_
square_() -> Tensor
squeeze
squeeze(dim=None) -> Tensor
squeeze_
squeeze_(dim=None) -> Tensor
sspaddmm
sspaddmm(mat1, mat2, *, beta=1, alpha=1) -> Tensor
std
std(dim=None, *, correction=1, keepdim=False) -> Tensor
stft
stft(frame_length, hop, fft_size=None, return_onesided=True, window=None, pad_end=0) -> Tensor
storage
storage_offset
storage_offset() -> int
storage_type
stride
stride(dim) -> tuple or int
sub
sub(other, *, alpha=1) -> Tensor
sub_
sub_(other, *, alpha=1) -> Tensor
subtract
subtract(other, *, alpha=1) -> Tensor
subtract_
subtract_(other, *, alpha=1) -> Tensor
sum
sum(dim=None, keepdim=False, dtype=None) -> Tensor
sum_to_size
sum_to_size(*size) -> Tensor
svd
svd(some=True, compute_uv=True) -> (Tensor, Tensor, Tensor)
swapaxes
swapaxes(axis0, axis1) -> Tensor
swapaxes_
swapaxes_(axis0, axis1) -> Tensor
swapdims
swapdims(dim0, dim1) -> Tensor
swapdims_
swapdims_(dim0, dim1) -> Tensor
symeig
t
t() -> Tensor
t_
t_() -> Tensor
take
take(indices) -> Tensor
take_along_dim
take_along_dim(indices, dim) -> Tensor
tan
tan() -> Tensor
tan_
tan_() -> Tensor
tanh
tanh() -> Tensor
tanh_
tanh_() -> Tensor
tensor_split
tensor_split(indices_or_sections, dim=0) -> List of Tensors
tile
tile(dims) -> Tensor
to
to(*args, **kwargs) -> Tensor
to_dense
to_dense(dtype=None, *, masked_grad=True) -> Tensor
to_mkldnn
to_mkldnn() -> Tensor
to_padded_tensor
to_padded_tensor(padding, output_size=None) -> Tensor
to_sparse
to_sparse(sparseDims) -> Tensor
to_sparse_bsc
to_sparse_bsc(blocksize, dense_dim) -> Tensor
to_sparse_bsr
to_sparse_bsr(blocksize, dense_dim) -> Tensor
to_sparse_coo
to_sparse_csc
to_sparse_csc() -> Tensor
to_sparse_csr
to_sparse_csr(dense_dim=None) -> Tensor
tolist
tolist() -> list or number
topk
topk(k, dim=None, largest=True, sorted=True) -> (Tensor, LongTensor)
trace
trace() -> Tensor
transpose
transpose(dim0, dim1) -> Tensor
transpose_
transpose_(dim0, dim1) -> Tensor
triangular_solve
triangular_solve(A, upper=True, transpose=False, unitriangular=False) -> (Tensor, Tensor)
tril
tril(diagonal=0) -> Tensor
tril_
tril_(diagonal=0) -> Tensor
triu
triu(diagonal=0) -> Tensor
triu_
triu_(diagonal=0) -> Tensor
true_divide
true_divide(value) -> Tensor
true_divide_
true_divide_(value) -> Tensor
trunc
trunc() -> Tensor
trunc_
trunc_() -> Tensor
type
type(dtype=None, non_blocking=False, **kwargs) -> str or Tensor
type_as
type_as(tensor) -> Tensor
unbind
unbind(dim=0) -> seq
unflatten
unfold
unfold(dimension, size, step) -> Tensor
uniform_
uniform_(from=0, to=1, *, generator=None) -> Tensor
unique
unique_consecutive
unsafe_chunk
unsafe_chunk(chunks, dim=0) -> List of Tensors
unsafe_split
unsafe_split(split_size, dim=0) -> List of Tensors
unsafe_split_with_sizes
unsqueeze
unsqueeze(dim) -> Tensor
unsqueeze_
unsqueeze_(dim) -> Tensor
untyped_storage
untyped_storage() -> torch.UntypedStorage
values
values() -> Tensor
var
var(dim=None, *, correction=1, keepdim=False) -> Tensor
vdot
vdot(other) -> Tensor
view
view(*shape) -> Tensor
view_as
view_as(other) -> Tensor
volatile
vsplit
vsplit(split_size_or_sections) -> List of Tensors
where
where(condition, y) -> Tensor
xlogy
xlogy(other) -> Tensor
xlogy_
xlogy_(other) -> Tensor
xpu
xpu(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
zero_
zero_() -> Tensor
"""
