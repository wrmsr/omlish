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
new_tensor(data, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_full(size, fill_value, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_empty(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_empty_strided(size, stride, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_ones(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
new_zeros(size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False) -> Tensor
abs() -> Tensor
abs_() -> Tensor
absolute() -> Tensor
absolute_() -> Tensor
acos() -> Tensor
acos_() -> Tensor
arccos() -> Tensor
arccos_() -> Tensor
acosh() -> Tensor
acosh_() -> Tensor
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
sspaddmm(mat1, mat2, *, beta=1, alpha=1) -> Tensor
smm(mat) -> Tensor
addr(vec1, vec2, *, beta=1, alpha=1) -> Tensor
addr_(vec1, vec2, *, beta=1, alpha=1) -> Tensor
align_as(other) -> Tensor
all(dim=None, keepdim=False) -> Tensor
allclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor
angle() -> Tensor
any(dim=None, keepdim=False) -> Tensor
apply_(callable) -> Tensor
asin() -> Tensor
asin_() -> Tensor
arcsin() -> Tensor
arcsin_() -> Tensor
asinh() -> Tensor
asinh_() -> Tensor
arcsinh() -> Tensor
arcsinh_() -> Tensor
as_strided(size, stride, storage_offset=None) -> Tensor
as_strided_(size, stride, storage_offset=None) -> Tensor
atan() -> Tensor
atan_() -> Tensor
arctan() -> Tensor
arctan_() -> Tensor
atan2(other) -> Tensor
atan2_(other) -> Tensor
arctan2(other) -> Tensor
atan2_(other) -> Tensor
atanh() -> Tensor
atanh_(other) -> Tensor
arctanh() -> Tensor
arctanh_(other) -> Tensor
baddbmm(batch1, batch2, *, beta=1, alpha=1) -> Tensor
baddbmm_(batch1, batch2, *, beta=1, alpha=1) -> Tensor
bernoulli(*, generator=None) -> Tensor
bernoulli_(p=0.5, *, generator=None) -> Tensor
bincount(weights=None, minlength=0) -> Tensor
bitwise_not() -> Tensor
bitwise_not_() -> Tensor
bitwise_and() -> Tensor
bitwise_and_() -> Tensor
bitwise_or() -> Tensor
bitwise_or_() -> Tensor
bitwise_xor() -> Tensor
bitwise_xor_() -> Tensor
bitwise_left_shift(other) -> Tensor
bitwise_left_shift_(other) -> Tensor
bitwise_right_shift(other) -> Tensor
bitwise_right_shift_(other) -> Tensor
broadcast_to(shape) -> Tensor
logical_and() -> Tensor
logical_and_() -> Tensor
logical_not() -> Tensor
logical_not_() -> Tensor
logical_or() -> Tensor
logical_or_() -> Tensor
logical_xor() -> Tensor
logical_xor_() -> Tensor
bmm(batch2) -> Tensor
cauchy_(median=0, sigma=1, *, generator=None) -> Tensor
ceil() -> Tensor
ceil_() -> Tensor
cholesky(upper=False) -> Tensor
cholesky_solve(input2, upper=False) -> Tensor
cholesky_inverse(upper=False) -> Tensor
clamp(min=None, max=None) -> Tensor
clamp_(min=None, max=None) -> Tensor
clip(min=None, max=None) -> Tensor
clip_(min=None, max=None) -> Tensor
clone(*, memory_format=torch.preserve_format) -> Tensor
coalesce() -> Tensor
contiguous(memory_format=torch.contiguous_format) -> Tensor
copy_(src, non_blocking=False) -> Tensor
conj() -> Tensor
conj_physical() -> Tensor
conj_physical_() -> Tensor
resolve_conj() -> Tensor
resolve_neg() -> Tensor
copysign(other) -> Tensor
copysign_(other) -> Tensor
cos() -> Tensor
cos_() -> Tensor
cosh() -> Tensor
cosh_() -> Tensor
cpu(memory_format=torch.preserve_format) -> Tensor
count_nonzero(dim=None) -> Tensor
cov(*, correction=1, fweights=None, aweights=None) -> Tensor
corrcoef() -> Tensor
cross(other, dim=None) -> Tensor
cuda(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
ipu(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
xpu(device=None, non_blocking=False, memory_format=torch.preserve_format) -> Tensor
logcumsumexp(dim) -> Tensor
cummax(dim) -> (Tensor, Tensor)
cummin(dim) -> (Tensor, Tensor)
cumprod(dim, dtype=None) -> Tensor
cumprod_(dim, dtype=None) -> Tensor
cumsum(dim, dtype=None) -> Tensor
cumsum_(dim, dtype=None) -> Tensor
data_ptr() -> int
dequantize() -> Tensor
dense_dim() -> int
diag(diagonal=0) -> Tensor
diag_embed(offset=0, dim1=-2, dim2=-1) -> Tensor
diagflat(offset=0) -> Tensor
diagonal(offset=0, dim1=0, dim2=1) -> Tensor
diagonal_scatter(src, offset=0, dim1=0, dim2=1) -> Tensor
as_strided_scatter(src, size, stride, storage_offset=None) -> Tensor
fill_diagonal_(fill_value, wrap=False) -> Tensor
floor_divide(value) -> Tensor
floor_divide_(value) -> Tensor
diff(n=1, dim=-1, prepend=None, append=None) -> Tensor
digamma() -> Tensor
digamma_() -> Tensor
dim() -> int
dist(other, p=2) -> Tensor
div(value, *, rounding_mode=None) -> Tensor
div_(value, *, rounding_mode=None) -> Tensor
divide(value, *, rounding_mode=None) -> Tensor
divide_(value, *, rounding_mode=None) -> Tensor
dot(other) -> Tensor
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
exp_() -> Tensor
exp2() -> Tensor
exp2_() -> Tensor
expm1() -> Tensor
expm1_() -> Tensor
exponential_(lambd=1, *, generator=None) -> Tensor
fill_(value) -> Tensor
floor() -> Tensor
flip(dims) -> Tensor
fliplr() -> Tensor
flipud() -> Tensor
roll(shifts, dims) -> Tensor
floor_() -> Tensor
fmod(divisor) -> Tensor
fmod_(divisor) -> Tensor
frac() -> Tensor
frac_() -> Tensor
frexp(input) -> (Tensor mantissa, Tensor exponent)
flatten(start_dim=0, end_dim=-1) -> Tensor
gather(dim, index) -> Tensor
gcd(other) -> Tensor
gcd_(other) -> Tensor
ge(other) -> Tensor
ge_(other) -> Tensor
greater_equal(other) -> Tensor
greater_equal_(other) -> Tensor
geometric_(p, *, generator=None) -> Tensor
geqrf() -> (Tensor, Tensor)
ger(vec2) -> Tensor
inner(other) -> Tensor
outer(vec2) -> Tensor
hypot(other) -> Tensor
hypot_(other) -> Tensor
i0() -> Tensor
i0_() -> Tensor
igamma(other) -> Tensor
igamma_(other) -> Tensor
igammac(other) -> Tensor
igammac_(other) -> Tensor
indices() -> Tensor
get_device() -> Device ordinal (Integer)
values() -> Tensor
gt(other) -> Tensor
gt_(other) -> Tensor
greater(other) -> Tensor
greater_(other) -> Tensor
has_names
hardshrink(lambd=0.5) -> Tensor
heaviside(values) -> Tensor
heaviside_(values) -> Tensor
histc(bins=100, min=0, max=0) -> Tensor
histogram(input, bins, *, range=None, weight=None, density=False) -> (Tensor, Tensor)
index_add_(dim, index, source, *, alpha=1) -> Tensor
index_copy_(dim, index, tensor) -> Tensor
index_fill_(dim, index, value) -> Tensor
index_put_(indices, values, accumulate=False) -> Tensor
index_put(indices, values, accumulate=False) -> Tensor
index_reduce_(dim, index, source, reduce, *, include_self=True) -> Tensor
index_select(dim, index) -> Tensor
sparse_mask(mask) -> Tensor
inverse() -> Tensor
isnan() -> Tensor
isinf() -> Tensor
isposinf() -> Tensor
isneginf() -> Tensor
isfinite() -> Tensor
isclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor
isreal() -> Tensor
is_coalesced() -> bool
is_contiguous(memory_format=torch.contiguous_format) -> bool
is_pinned
is_floating_point() -> bool
is_complex() -> bool
is_inference() -> bool
is_conj() -> bool
is_neg() -> bool
is_signed() -> bool
is_set_to(tensor) -> bool
item() -> number
kron(other) -> Tensor
kthvalue(k, dim=None, keepdim=False) -> (Tensor, LongTensor)
ldexp(other) -> Tensor
ldexp_(other) -> Tensor
lcm(other) -> Tensor
lcm_(other) -> Tensor
le(other) -> Tensor
le_(other) -> Tensor
less_equal(other) -> Tensor
less_equal_(other) -> Tensor
lerp(end, weight) -> Tensor
lerp_(end, weight) -> Tensor
lgamma() -> Tensor
lgamma_() -> Tensor
log() -> Tensor
log_() -> Tensor
log10() -> Tensor
log10_() -> Tensor
log1p() -> Tensor
log1p_() -> Tensor
log2() -> Tensor
log2_() -> Tensor
logaddexp(other) -> Tensor
logaddexp2(other) -> Tensor
log_normal_(mean=1, std=2, *, generator=None)
logsumexp(dim, keepdim=False) -> Tensor
lt(other) -> Tensor
lt_(other) -> Tensor
lt(other) -> Tensor
less_(other) -> Tensor
lu_solve(LU_data, LU_pivots) -> Tensor
map_(tensor, callable)
masked_scatter_(mask, source)
masked_fill_(mask, value)
masked_select(mask) -> Tensor
matrix_power(n) -> Tensor
matrix_exp() -> Tensor
max(dim=None, keepdim=False) -> Tensor or (Tensor, Tensor)
amax(dim=None, keepdim=False) -> Tensor
maximum(other) -> Tensor
fmax(other) -> Tensor
argmax(dim=None, keepdim=False) -> LongTensor
argwhere() -> Tensor
mean(dim=None, keepdim=False, *, dtype=None) -> Tensor
nanmean(dim=None, keepdim=False, *, dtype=None) -> Tensor
median(dim=None, keepdim=False) -> (Tensor, LongTensor)
nanmedian(dim=None, keepdim=False) -> (Tensor, LongTensor)
min(dim=None, keepdim=False) -> Tensor or (Tensor, Tensor)
amin(dim=None, keepdim=False) -> Tensor
minimum(other) -> Tensor
aminmax(*, dim=None, keepdim=False) -> (Tensor min, Tensor max)
fmin(other) -> Tensor
argmin(dim=None, keepdim=False) -> LongTensor
mm(mat2) -> Tensor
mode(dim=None, keepdim=False) -> (Tensor, LongTensor)
movedim(source, destination) -> Tensor
moveaxis(source, destination) -> Tensor
mul(value) -> Tensor
mul_(value) -> Tensor
multiply(value) -> Tensor
multiply_(value) -> Tensor
multinomial(num_samples, replacement=False, *, generator=None) -> Tensor
mv(vec) -> Tensor
mvlgamma(p) -> Tensor
mvlgamma_(p) -> Tensor
narrow(dimension, start, length) -> Tensor
narrow_copy(dimension, start, length) -> Tensor
ndimension() -> int
nan_to_num(nan=0.0, posinf=None, neginf=None) -> Tensor
nan_to_num_(nan=0.0, posinf=None, neginf=None) -> Tensor
ne(other) -> Tensor
ne_(other) -> Tensor
not_equal(other) -> Tensor
not_equal_(other) -> Tensor
neg() -> Tensor
negative() -> Tensor
neg_() -> Tensor
negative_() -> Tensor
nelement() -> int
nextafter(other) -> Tensor
nextafter_(other) -> Tensor
nonzero() -> LongTensor
nonzero_static(input, *, size, fill_value=-1) -> Tensor
norm(p=2, dim=None, keepdim=False) -> Tensor
normal_(mean=0, std=1, *, generator=None) -> Tensor
numel() -> int
numpy(*, force=False) -> numpy.ndarray
orgqr(input2) -> Tensor
ormqr(input2, input3, left=True, transpose=False) -> Tensor
permute(*dims) -> Tensor
polygamma(n) -> Tensor
polygamma_(n) -> Tensor
positive() -> Tensor
pow(exponent) -> Tensor
pow_(exponent) -> Tensor
float_power(exponent) -> Tensor
float_power_(exponent) -> Tensor
prod(dim=None, keepdim=False, dtype=None) -> Tensor
put_(index, source, accumulate=False) -> Tensor
put(input, index, source, accumulate=False) -> Tensor
qr(some=True) -> (Tensor, Tensor)
qscheme() -> torch.qscheme
quantile(q, dim=None, keepdim=False, *, interpolation='linear') -> Tensor
nanquantile(q, dim=None, keepdim=False, *, interpolation='linear') -> Tensor
q_scale() -> float
q_zero_point() -> int
q_per_channel_scales() -> Tensor
q_per_channel_zero_points() -> Tensor
q_per_channel_axis() -> int
random_(from=0, to=None, *, generator=None) -> Tensor
rad2deg() -> Tensor
rad2deg_() -> Tensor
deg2rad() -> Tensor
deg2rad_() -> Tensor
ravel() -> Tensor
reciprocal() -> Tensor
reciprocal_() -> Tensor
record_stream(stream)
remainder(divisor) -> Tensor
remainder_(divisor) -> Tensor
renorm(p, dim, maxnorm) -> Tensor
renorm_(p, dim, maxnorm) -> Tensor
repeat(*sizes) -> Tensor
repeat_interleave(repeats, dim=None, *, output_size=None) -> Tensor
requires_grad_(requires_grad=True) -> Tensor
reshape(*shape) -> Tensor
reshape_as(other) -> Tensor
resize_(*sizes, memory_format=torch.contiguous_format) -> Tensor
resize_as_(tensor, memory_format=torch.contiguous_format) -> Tensor
rot90(k, dims) -> Tensor
round(decimals=0) -> Tensor
round_(decimals=0) -> Tensor
rsqrt() -> Tensor
rsqrt_() -> Tensor
scatter_(dim, index, src, reduce=None) -> Tensor
scatter_add_(dim, index, src) -> Tensor
scatter_reduce_(dim, index, src, reduce, *, include_self=True) -> Tensor
select(dim, index) -> Tensor
select_scatter(src, dim, index) -> Tensor
slice_scatter(src, dim=0, start=None, end=None, step=1) -> Tensor
set_(source=None, storage_offset=0, size=None, stride=None) -> Tensor
sigmoid() -> Tensor
sigmoid_() -> Tensor
logit() -> Tensor
logit_() -> Tensor
sign() -> Tensor
sign_() -> Tensor
signbit() -> Tensor
sgn() -> Tensor
sgn_() -> Tensor
sin() -> Tensor
sin_() -> Tensor
sinc() -> Tensor
sinc_() -> Tensor
sinh() -> Tensor
sinh_() -> Tensor
size(dim=None) -> torch.Size or int
shape() -> torch.Size
sort(dim=-1, descending=False) -> (Tensor, LongTensor)
msort() -> Tensor
argsort(dim=-1, descending=False) -> LongTensor
sparse_dim() -> int
sparse_resize_(size, sparse_dim, dense_dim) -> Tensor
sparse_resize_and_clear_(size, sparse_dim, dense_dim) -> Tensor
sqrt() -> Tensor
sqrt_() -> Tensor
square() -> Tensor
square_() -> Tensor
squeeze(dim=None) -> Tensor
squeeze_(dim=None) -> Tensor
std(dim=None, *, correction=1, keepdim=False) -> Tensor
storage_offset() -> int
untyped_storage() -> torch.UntypedStorage
stride(dim) -> tuple or int
sub(other, *, alpha=1) -> Tensor
sub_(other, *, alpha=1) -> Tensor
subtract(other, *, alpha=1) -> Tensor
subtract_(other, *, alpha=1) -> Tensor
sum(dim=None, keepdim=False, dtype=None) -> Tensor
nansum(dim=None, keepdim=False, dtype=None) -> Tensor
svd(some=True, compute_uv=True) -> (Tensor, Tensor, Tensor)
swapdims(dim0, dim1) -> Tensor
swapdims_(dim0, dim1) -> Tensor
swapaxes(axis0, axis1) -> Tensor
swapaxes_(axis0, axis1) -> Tensor
t() -> Tensor
t_() -> Tensor
tile(dims) -> Tensor
to(*args, **kwargs) -> Tensor
byte(memory_format=torch.preserve_format) -> Tensor
bool(memory_format=torch.preserve_format) -> Tensor
char(memory_format=torch.preserve_format) -> Tensor
bfloat16(memory_format=torch.preserve_format) -> Tensor
double(memory_format=torch.preserve_format) -> Tensor
float(memory_format=torch.preserve_format) -> Tensor
cdouble(memory_format=torch.preserve_format) -> Tensor
cfloat(memory_format=torch.preserve_format) -> Tensor
chalf(memory_format=torch.preserve_format) -> Tensor
half(memory_format=torch.preserve_format) -> Tensor
int(memory_format=torch.preserve_format) -> Tensor
int_repr() -> Tensor
long(memory_format=torch.preserve_format) -> Tensor
short(memory_format=torch.preserve_format) -> Tensor
take(indices) -> Tensor
take_along_dim(indices, dim) -> Tensor
tan() -> Tensor
tan_() -> Tensor
tanh() -> Tensor
softmax(dim) -> Tensor
tanh_() -> Tensor
tolist() -> list or number
topk(k, dim=None, largest=True, sorted=True) -> (Tensor, LongTensor)
to_dense(dtype=None, *, masked_grad=True) -> Tensor
to_sparse(sparseDims) -> Tensor
to_sparse_csr(dense_dim=None) -> Tensor
to_sparse_csc() -> Tensor
to_sparse_bsr(blocksize, dense_dim) -> Tensor
to_sparse_bsc(blocksize, dense_dim) -> Tensor
to_mkldnn() -> Tensor
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
fix() -> Tensor
trunc_() -> Tensor
fix_() -> Tensor
type(dtype=None, non_blocking=False, **kwargs) -> str or Tensor
type_as(tensor) -> Tensor
unfold(dimension, size, step) -> Tensor
uniform_(from=0, to=1, *, generator=None) -> Tensor
unsqueeze(dim) -> Tensor
unsqueeze_(dim) -> Tensor
var(dim=None, *, correction=1, keepdim=False) -> Tensor
vdot(other) -> Tensor
view(*shape) -> Tensor
view_as(other) -> Tensor
expand(*sizes) -> Tensor
expand_as(other) -> Tensor
sum_to_size(*size) -> Tensor
zero_() -> Tensor
matmul(tensor2) -> Tensor
chunk(chunks, dim=0) -> List of Tensors
unsafe_chunk(chunks, dim=0) -> List of Tensors
unsafe_split(split_size, dim=0) -> List of Tensors
tensor_split(indices_or_sections, dim=0) -> List of Tensors
hsplit(split_size_or_sections) -> List of Tensors
vsplit(split_size_or_sections) -> List of Tensors
dsplit(split_size_or_sections) -> List of Tensors
stft(frame_length, hop, fft_size=None, return_onesided=True, window=None, pad_end=0) -> Tensor
istft(n_fft, hop_length=None, win_length=None, window=None,
det() -> Tensor
where(condition, y) -> Tensor
logdet() -> Tensor
slogdet() -> (Tensor, Tensor)
unbind(dim=0) -> seq
pin_memory() -> Tensor
pinverse() -> Tensor
index_add(dim, index, source, *, alpha=1) -> Tensor
index_copy(dim, index, tensor2) -> Tensor
index_fill(dim, index, value) -> Tensor
scatter(dim, index, src) -> Tensor
scatter_add(dim, index, src) -> Tensor
scatter_reduce(dim, index, src, reduce, *, include_self=True) -> Tensor
masked_scatter(mask, tensor) -> Tensor
xlogy(other) -> Tensor
xlogy_(other) -> Tensor
masked_fill(mask, value) -> Tensor
grad
retain_grad() -> None
retains_grad
requires_grad
is_leaf
names
is_cuda
is_cpu
is_xla
is_ipu
is_xpu
is_quantized
is_meta
is_mps
is_sparse
is_sparse_csr
device
ndim
itemsize
nbytes
T
H
mT
mH
adjoint() -> Tensor
real
imag
as_subclass(cls) -> Tensor
crow_indices() -> IntTensor
col_indices() -> IntTensor
to_padded_tensor(padding, output_size=None) -> Tensor
"""