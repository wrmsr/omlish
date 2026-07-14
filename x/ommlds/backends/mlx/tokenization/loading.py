import functools
import json
import pathlib
import typing as ta

import transformers as tfm

from .detokenization.base import StreamingDetokenizer
from .detokenization.bpe import BpeStreamingDetokenizer
from .detokenization.naive import NaiveStreamingDetokenizer
from .detokenization.spm import SpmStreamingDetokenizer
from .tokenization import Tokenization
from .types import Tokenizer


##


def _match(a, b):
    if type(a) is not type(b):
        return False

    if isinstance(a, dict):
        return len(a) == len(b) and all(k in b and _match(a[k], b[k]) for k in a)

    if isinstance(a, list):
        return len(a) == len(b) and all(_match(ai, bi) for ai, bi in zip(a, b))

    return a == b


def _is_spm_decoder(decoder):
    return _match({
        'type': 'Sequence',
        'decoders': [
            {'type': 'Replace', 'pattern': {'String': '▁'}, 'content': ' '},
            {'type': 'ByteFallback'},
            {'type': 'Fuse'},
            {'type': 'Strip', 'content': ' ', 'start': 1, 'stop': 0},
        ],
    }, decoder)


def _is_spm_decoder_no_space(decoder):
    return _match({
        'type': 'Sequence',
        'decoders': [
            {'type': 'Replace', 'pattern': {'String': '▁'}, 'content': ' '},
            {'type': 'ByteFallback'},
            {'type': 'Fuse'},
        ],
    }, decoder)


def _is_bpe_decoder(decoder):
    return (
        isinstance(decoder, dict) and
        decoder.get('type', None) == 'ByteLevel'
    )


def load_tokenization(
        model_path: pathlib.Path,
        tokenizer_config_extra: dict | None = None,
        *,
        eos_token_ids: ta.Iterable[int] | int | None = None,
) -> Tokenization:
    """
    Load a huggingface tokenizer and try to infer the type of streaming detokenizer to use.

    Note, to use a fast streaming tokenizer, pass a local file path rather than a Hugging Face repo ID.
    """

    detokenizer_fac: ta.Callable[[Tokenizer], StreamingDetokenizer] = NaiveStreamingDetokenizer

    tokenizer_file = model_path / 'tokenizer.json'
    if tokenizer_file.exists():
        with open(tokenizer_file, encoding='utf-8') as fid:
            try:
                tokenizer_content = json.load(fid)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError('Failed to parse tokenizer.json', e.doc, e.pos) from None

        if 'decoder' in tokenizer_content:
            if _is_spm_decoder(tokenizer_content['decoder']):
                detokenizer_fac = SpmStreamingDetokenizer

            elif _is_spm_decoder_no_space(tokenizer_content['decoder']):
                detokenizer_fac = functools.partial(SpmStreamingDetokenizer, trim_space=False)

            elif _is_bpe_decoder(tokenizer_content['decoder']):
                detokenizer_fac = BpeStreamingDetokenizer

    if isinstance(eos_token_ids, int):
        eos_token_ids = [eos_token_ids]

    tokenizer = tfm.AutoTokenizer.from_pretrained(
        model_path,
        **(tokenizer_config_extra or {}),
    )

    detokenizer = detokenizer_fac(tokenizer)

    return Tokenization(
        tokenizer,
        detokenizer,
        eos_token_ids=eos_token_ids,
    )
