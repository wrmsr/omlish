import dataclasses as dc
import pathlib
import typing as ta

import mlx_lm.utils
from mlx import nn

from omlish import check
from omlish import lang

from .tokenization import Tokenization
from .tokenization import load_tokenization


##


def get_model_path(
        path_or_hf_repo: str,
        revision: str | None = None,
) -> tuple[pathlib.Path, str | None]:
    """
    Ensures the model is available locally. If the path does not exist locally,
    it is downloaded from the Hugging Face Hub.

    Args:
        path_or_hf_repo (str): The local path or Hugging Face repository ID of the model.
        revision (str, optional): A revision id which can be a branch name, a tag, or a commit hash.

    Returns:
        Tuple[Path, str]: A tuple containing the local file path and the Hugging Face repo ID.
    """

    model_path = pathlib.Path(path_or_hf_repo)

    if not model_path.exists():
        from huggingface_hub import snapshot_download
        hf_path = path_or_hf_repo
        model_path = pathlib.Path(
            snapshot_download(
                path_or_hf_repo,
                revision=revision,
                allow_patterns=[
                    '*.jinja',
                    '*.json',
                    '*.jsonl',
                    '*.py',
                    '*.txt',

                    'model*.safetensors',

                    '*.tiktoken',
                    'tiktoken.model',
                    'tokenizer.model',
                ],
            ),
        )

    else:
        from huggingface_hub import ModelCard

        card_path = model_path / 'README.md'
        if card_path.is_file():
            card = ModelCard.load(card_path)
            hf_path = card.data.base_model
        else:
            hf_path = None

    return model_path, hf_path


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
    # FIXME: get_model_path return annotation is wrong:
    #   https://github.com/ml-explore/mlx-lm/blob/9ee2b7358f5e258af7b31a8561acfbbe56ad5085/mlx_lm/utils.py#L82
    model_path_res = ta.cast(ta.Any, get_model_path(path_or_hf_repo))
    if isinstance(model_path_res, tuple):
        model_path = check.isinstance(model_path_res[0], pathlib.Path)
    else:
        model_path = check.isinstance(model_path_res, pathlib.Path)

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
