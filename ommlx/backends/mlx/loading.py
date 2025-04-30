import typing as ta

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import mlx.nn
    import mlx_lm.utils
    import transformers
else:
    mlx = lang.proxy_import('mlx', extras=['nn'])
    mlx_lm = lang.proxy_import('mlx_lm', extras=['utils'])
    transformers = lang.proxy_import('transformers')


##


class LoadedModel(ta.NamedTuple):
    model: 'mlx.nn.Module'
    tokenizer: 'mlx_lm.utils.TokenizerWrapper'

    @property
    def as_pre_trained_tokenizer(self) -> 'transformers.PreTrainedTokenizerBase':
        return ta.cast(transformers.PreTrainedTokenizerBase, self.tokenizer)

    @property
    def check_pre_trained_tokenizer(self) -> 'transformers.PreTrainedTokenizerBase':
        tw: ta.Any = check.isinstance(self.tokenizer, mlx_lm.utils.TokenizerWrapper)
        return check.isinstance(tw._tokenizer, transformers.PreTrainedTokenizerBase)  # noqa


def load_model(
        path_or_hf_repo: str,
        *,
        tokenizer_config: ta.Any = None,
        model_config: ta.Any = None,
        adapter_path: str | None = None,
        lazy: bool = False,
        **kwargs: ta.Any,
) -> LoadedModel:
    model, tokenizer = mlx_lm.load(
        path_or_hf_repo,
        **lang.opt_kw(
            tokenizer_config=tokenizer_config,
            model_config=model_config,
        ),
        adapter_path=adapter_path,
        lazy=lazy,
        **kwargs,
    )

    return LoadedModel(model, tokenizer)
