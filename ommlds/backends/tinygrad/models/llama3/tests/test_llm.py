import pytest

from ..fetch import fetch_model
from ..llm import Llama3Llm


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_llama3_llm():
    from tinygrad import Tensor

    Tensor.no_grad = True
    Tensor.manual_seed(42)

    llm = Llama3Llm(
        fetch_model(size := '1B'),
        size=size,
    )

    prompt = [
        llm.tokenizer.bos_id,
        *llm.encode_message('system', 'You are an helpful assistant.'),
    ]

    start_pos = llm.prefill(prompt)

    toks = llm.encode_message('user', 'Is water wet?') + llm.encode_role('assistant')

    start_pos = llm.prefill(toks[:-1], start_pos=start_pos)
    last_tok = toks[-1]
    while True:
        tok = llm.feed(
            [last_tok],
            start_pos,
        )
        tok = tok.item()

        start_pos += 1
        last_tok = tok
        if tok in llm.tokenizer.stop_tokens:
            break

        print(llm.tokenizer.decode([tok]), end='', flush=True)

    print(flush=True)
