import dataclasses as dc
import os
import typing as ta

import torch
import transformers.feature_extraction_utils


class NotSet:
    pass


NOT_SET = NotSet()


@dc.dataclass(frozen=True)
class PretrainedConfig:
    """
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
    prune_heads: ta.Mapping[int, ta.Sequence[int]] | None = {}
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

    architectures (`List[str]`, *optional*): Model architectures that can be used with the model pretrained weights.
    finetuning_task (`str`, *optional*): Name of the task used to fine-tune the model. This can be used when converting from an original (TensorFlow or PyTorch) checkpoint.
    id2label (`Dict[int, str]`, *optional*): A map from index (for instance prediction index, or target index) to label.
    label2id (`Dict[str, int]`, *optional*): A map from label to index for the model.
    num_labels (`int`, *optional*): Number of labels to use in the last layer added to the model, typically for a classification task.
    task_specific_params (`Dict[str, Any]`, *optional*): Additional keyword arguments to store for the current task.
    problem_type (`str`, *optional*): Problem type for `XxxForSequenceClassification` models. Can be one of `"regression"`, `"single_label_classification"` or `"multi_label_classification"`.

    > Parameters linked to the tokenizer

    tokenizer_class (`str`, *optional*): The name of the associated tokenizer class to use (if none is set, will use the tokenizer associated to the model by default).
    prefix (`str`, *optional*): A specific prompt that should be added at the beginning of each text before calling the model.
    bos_token_id (`int`, *optional*): The id of the _beginning-of-stream_ token.
    pad_token_id (`int`, *optional*): The id of the _padding_ token.
    eos_token_id (`int`, *optional*): The id of the _end-of-stream_ token.
    decoder_start_token_id (`int`, *optional*): If an encoder-decoder model starts decoding with a different token than _bos_, the id of that token.
    sep_token_id (`int`, *optional*): The id of the _separation_ token.

    > PyTorch specific parameters

    torchscript (`bool`, *optional*, defaults to `False`): Whether or not the model should be used with Torchscript.
    tie_word_embeddings (`bool`, *optional*, defaults to `True`): Whether the model's input and output word embeddings should be tied. Note that this is only relevant if the model has a output word embedding layer.
    torch_dtype (`str`, *optional*): The `dtype` of the weights. This attribute can be used to initialize the model to a non-default `dtype` (which is normally `float32`) and thus allow for optimal storage allocation. For example, if the saved model is `float16`, ideally we want to load it back using the minimal amount of memory needed to load `float16` weights. Since the config object is stored in plain text, this attribute contains just the floating type string without the `torch.` prefix. For example, for `torch.float16` ``torch_dtype` is the `"float16"` string.

    > TensorFlow specific parameters

    use_bfloat16 (`bool`, *optional*, defaults to `False`): Whether or not the model should use BFloat16 scalars (only used by some TensorFlow models).
    tf_legacy_loss (`bool`, *optional*, defaults to `False`): Whether the model should use legacy TensorFlow losses. Legacy losses have variable output shapes and may not be XLA-compatible. This option is here for backward compatibility and will be removed in Transformers v5.
    """


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
