import pathlib
import typing as ta

from tinygrad import Device
from tinygrad import GlobalCounters
from tinygrad import Tensor
from tinygrad.helpers import tqdm
from tinygrad.nn.state import get_parameters

from .loading import build_transformer
from .tokenization import Tokenizer


##


class Llama3Llm:
    def __init__(
            self,
            model_path: pathlib.Path,
            *,
            size: str = '1B',
            quantize: str | None = None,
            shard: int = 1,

            # default settings
            temperature: float = 0.95,
            top_k: int = 0,
            top_p: float = 0.0,
            alpha_f: float = 0.0,
            alpha_p: float = 0.0,
    ) -> None:
        super().__init__()

        self.model_path = model_path

        self.size = size
        self.quantize = quantize
        self.shard = shard

        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.alpha_f = alpha_f
        self.alpha_p = alpha_p

        self.tokenizer = Tokenizer(
            str((model_path if model_path.is_dir() else model_path.parent) / 'tokenizer.model'),
        )

        self.device = (
            tuple(f'{Device.DEFAULT}:{i}' for i in range(shard))
            if shard > 1
            else Device.DEFAULT
        )

        self.model = build_transformer(
            model_path,
            model_size=size,
            quantize=quantize,
            device=self.device,
        )

        self.param_bytes = sum(x.uop.size * x.dtype.itemsize for x in get_parameters(model_path))

        self.last_seen_toks: list = []

    def prefill(self, toks, start_pos=0):
        # we can skip part of the prompt if it is the same as last and start_pos=0
        if start_pos == 0:
            for i, (a, b) in enumerate(zip(toks, self.last_seen_toks)):  # noqa
                if a != b:
                    break
            else:
                i = min(len(toks), len(self.last_seen_toks))
            start_pos += i
            self.last_seen_toks = toks
            toks = toks[i:]

        # prefill the model
        tok: ta.Any
        for tok in tqdm(toks):
            GlobalCounters.reset()
            self.model(
                Tensor([[tok]], device=self.device),
                start_pos,
                self.temperature,
                self.top_k,
                self.top_p,
                self.alpha_f,
                self.alpha_p,
            ).realize()
            start_pos += 1

        return start_pos

    def encode_role(self, role: str) -> list[int]:
        return [
            self.tokenizer.special_tokens['<|start_header_id|>'],
            *self.tokenizer.encode(role),
            self.tokenizer.special_tokens['<|end_header_id|>'],
            *self.tokenizer.encode('\n\n'),
        ]

    def encode_message(self, role: str, content: str) -> list[int]:
        return [
            *self.encode_role(role),
            *self.tokenizer.encode(content.strip()),
            self.tokenizer.special_tokens['<|eot_id|>'],
        ]

    def feed(self, toks, start_pos):
        return self.model(
            Tensor([toks], device=self.device),
            start_pos,
            self.temperature,
            self.top_k,
            self.top_p,
            self.alpha_f,
            self.alpha_p,
        )


##


class RunLlmToStopResult(ta.NamedTuple):
    start_pos: int
    last_tok: int


def run_llm_to_stop(
        llm: Llama3Llm,
        start_pos: int,
        last_tok: int,
) -> ta.Generator[str, None, RunLlmToStopResult]:
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

        yield llm.tokenizer.decode([tok])

    return RunLlmToStopResult(start_pos, last_tok)


def run_llm(
        llm: Llama3Llm,
        toks: ta.Sequence[int],
        start_pos: int = 0,
) -> ta.Generator[str, None, RunLlmToStopResult]:
    start_pos = llm.prefill(toks[:-1], start_pos=start_pos)
    last_tok = toks[-1]
    return run_llm_to_stop(llm, start_pos, last_tok)
