import typing as ta

from tinygrad import Device
from tinygrad import Tensor
from tinygrad import dtypes

from omlish import check


##


_SAMPLE_ALPHA_COUNTER: ta.Any = None


# standard openai sampling
def sample(
        logits: Tensor,
        temp: float,
        k: int,
        p: float,
        af: float,
        ap: float,
):
    check.arg(logits.ndim == 1, 'only works on 1d tensors')
    check.arg(0 <= p <= 1, 'p must be between 0 and 1')
    check.arg(0 <= k <= logits.numel(), 'k must be between 0 and numel')

    # if temperature is very low just use argmax
    if temp < 1e-6:
        return logits.argmax()

    logits = logits.to(Device.DEFAULT)

    # alpha sampling
    global _SAMPLE_ALPHA_COUNTER
    if af or ap:
        if _SAMPLE_ALPHA_COUNTER is None:
            _SAMPLE_ALPHA_COUNTER = Tensor.zeros_like(logits, dtype=dtypes.int32).contiguous()
        logits = logits - (_SAMPLE_ALPHA_COUNTER * af + (_SAMPLE_ALPHA_COUNTER > 0) * ap)

    # replace NaNs with -inf
    logits = (
        (logits != logits)  # noqa
        .where(-float('inf'), logits)
    )

    # softmax
    t = (logits / temp).softmax()

    counter, counter2 = (
        Tensor.arange(t.numel(), device=logits.device).contiguous(),
        Tensor.arange(t.numel() - 1, -1, -1, device=logits.device).contiguous(),
    )
    # top k
    if k:
        output, output_indices = (
            Tensor.zeros(k, device=logits.device).contiguous(),
            Tensor.zeros(k, device=logits.device, dtype=dtypes.int32).contiguous(),
        )
        for i in range(k):
            t_argmax = (
                t.numel() - ((t == (t_max := t.max())) * counter2).max() - 1
            ).cast(dtypes.default_int)
            output = output + t_max.unsqueeze(0).pad(((i, k - i - 1),))
            output_indices = output_indices + t_argmax.unsqueeze(0).pad(
                ((i, k - i - 1),),
            )
            t = (counter == t_argmax).where(0, t)

        # approximate top p
        # because we are already limited to top k elements we can do top p "without sorting"
        output_cumsum = output[::-1].cumsum()[::-1] + t.sum()
        output = (output_cumsum >= (1 - p)) * output
        output_indices = (output_cumsum >= (1 - p)) * output_indices

        # sample
        output_idx = output.multinomial()
        output_token = output_indices[output_idx]

    else:
        output_token = t.multinomial()

    # increase alpha counter
    if af or ap:
        _SAMPLE_ALPHA_COUNTER = (counter == output_token).where(_SAMPLE_ALPHA_COUNTER + 1, _SAMPLE_ALPHA_COUNTER)

    return output_token
