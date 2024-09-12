import dataclasses as dc
import typing as ta

import torch
import transformers


@dc.dataclass(frozen=True)
class PipelineArgs:
    task: str = None
    model: str | transformers.PreTrainedModel | transformers.TFPreTrainedModel | None = None
    config: str | PretrainedConfig | None = None
    tokenizer: str | PreTrainedTokenizer | PreTrainedTokenizerFast | None = None
    feature_extractor: str | PreTrainedFeatureExtractor | None = None
    image_processor: str | BaseImageProcessor | None = None
    framework: str | None = None
    revision: str | None = None
    use_fast: bool = True
    token: str | bool | None = None
    device: int | str | torch.device | None = None
    device_map: ta.Any = None
    torch_dtype: ta.Any = None
    trust_remote_code: bool | None = None
    model_kwargs: ta.Mapping[str, ta.Any] = None
    pipeline_class: ta.Any = None
