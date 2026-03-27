def disable_mistral_bullshit() -> None:
    from transformers.tokenization_utils_tokenizers import TokenizersBackend

    @classmethod  # type: ignore  # noqa
    def _patch_mistral_regex(cls, transformer, *args, **kwargs):
        return transformer

    TokenizersBackend._patch_mistral_regex = _patch_mistral_regex  # type: ignore  # noqa
