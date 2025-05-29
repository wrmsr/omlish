import dataclasses as dc
import pathlib

import mlx_lm.utils
from mlx import nn

from omlish import lang

from .tokenization import Tokenization
from .tokenization import load_tokenization


##


@dc.dataclass(frozen=True, kw_only=True)
class LoadedModel:
    path: pathlib.Path

    model: nn.Module
    config: dict

    #

    tokenizer_config_extra: dict | None = None
    tokenization: Tokenization

    @lang.cached_function
    def tokenizer_wrapper(self) -> mlx_lm.utils.TokenizerWrapper:
        return mlx_lm.utils.load_tokenizer(
            self.path,
            self.tokenizer_config_extra or {},
            eos_token_ids=self.config.get('eos_token_id', None),
        )


def load_model(
        path_or_hf_repo: str,
        *,
        tokenizer_config: dict | None = None,
        model_config: dict | None = None,
        adapter_path: str | None = None,
        lazy: bool = False,
) -> LoadedModel:
    model_path = mlx_lm.utils.get_model_path(path_or_hf_repo)

    model, config = mlx_lm.utils.load_model(
        model_path,
        lazy=lazy,
        model_config=model_config or {},
    )

    if adapter_path is not None:
        model = mlx_lm.utils.load_adapters(
            model,
            adapter_path,
        )
        model.eval()

    tokenization = load_tokenization(
        model_path,
        tokenizer_config or {},
        eos_token_ids=config.get('eos_token_id', None),
    )

    return LoadedModel(
        path=model_path,

        model=model,
        config=config,

        tokenizer_config_extra=tokenizer_config,
        tokenization=tokenization,
    )
