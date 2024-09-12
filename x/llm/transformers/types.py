import dataclasses as dc
import os
import typing as ta

from omlish import collections as col

import torch
import transformers.feature_extraction_utils


class NotSet:
    pass


NOT_SET = NotSet()


@dc.dataclass(frozen=True)
class PretrainedConfig:
    # class

    model_type: str
    is_composition: bool
    keys_to_ignore_at_inference: ta.Sequence[str]
    attribute_map: ta.Mapping[str, str]

    # common

    vocab_size: int | NotSet = NOT_SET
    hidden_size: int | NotSet = NOT_SET
    num_attention_heads: int | NotSet = NOT_SET
    num_hidden_layers: int | NotSet = NOT_SET

    # args

    name_or_path: str | None = ''
    output_hidden_states: bool | None = False
    output_attentions: bool | None = False
    return_dict: bool | None = True
    is_encoder_decoder: bool | None = False
    is_decoder: bool | None = False
    cross_attention_hidden_size: bool | None = None
    add_cross_attention: bool | None = False
    tie_encoder_decoder: bool | None = False
    prune_heads: ta.Mapping[int, ta.Sequence[int]] | None = col.frozendict()
    chunk_size_feed_forward: int | None = 0

    # sequence generation

    max_length: int | None = 20
    min_length: int | None = 0
    do_sample: bool | None = False
    early_stopping: bool | None = False
    num_beams: int | None = 1
    num_beam_groups: int | None = 1
    diversity_penalty: float | None = 0.
    temperature: float | None = 1.
    top_k: int | None = 50
    top_p: int | None = 1
    typical_p: float | None = 1.
    repetition_penalty: float | None = 1.
    length_penalty: float | None = 1.
    no_repeat_ngram_size: int | None = 0
    encoder_no_repeat_ngram_size: int | None = 0
    bad_words_ids: ta.Sequence[int] | None = None
    num_return_sequences: int | None = 1
    output_scores: bool | None = False
    return_dict_in_generate: bool | None = False
    forced_bos_token_id: int | None = None
    forced_eos_token_id: int | None = None
    remove_invalid_values: bool | None = None

    # fine-tuning

    architectures: ta.Sequence[str] | None = None
    finetuning_task: str | None = None
    id2label: ta.Mapping[int, str] | None = None
    label2id: ta.Mapping[str, int] | None = None
    num_labels: int | None = None
    task_specific_params: ta.Mapping[str, ta.Any] | None = None
    problem_type: str | None = None

    # tokenizer

    tokenizer_clas: str | None = None
    prefix: str | None = None
    bos_token_id: int | None = None
    pad_token_id: int | None = None
    eos_token_id: int | None = None
    decoder_start_token_id: int | None = None
    sep_token_id: int | None = None

    # pytorch

    torchscript: bool | None = False
    tie_word_embeddings: bool | None = True
    torch_dtype: str | None = None

    # tensorflow

    use_bfloat16: bool | None = False
    tf_legacy_loss: bool | None = False


@dc.dataclass(frozen=True)
class FromPretrainedArgs:
    pretrained_model_name_or_path: str | os.PathLike
    cache_dir: str | os.PathLike | None = None
    force_download: bool = False
    local_files_only: bool = False
    token: str | bool | None = None
    revision: str = 'main'


@dc.dataclass(frozen=True)
class PipelineArgs:
    task: str = None
    model: str | transformers.PreTrainedModel | transformers.TFPreTrainedModel | None = None
    config: str | PretrainedConfig | None = None
    tokenizer: str | transformers.PreTrainedTokenizer | transformers.PreTrainedTokenizerFast | None = None
    feature_extractor: str | transformers.feature_extraction_utils.PreTrainedFeatureExtractor | None = None
    image_processor: str | transformers.BaseImageProcessor | None = None
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
