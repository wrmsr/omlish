import pathlib

from tinygrad.helpers import fetch


##


def fetch_model(size: str) -> pathlib.Path:
    if size == '1B':
        fetch(
            'https://huggingface.co/bofenghuang/Meta-Llama-3-8B'
            '/resolve/main/original/tokenizer.model',
            'tokenizer.model',
            subdir='llama3-1b-instruct',
        )
        return fetch(
            'https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF'
            '/resolve/main/Llama-3.2-1B-Instruct-Q6_K.gguf',
            'Llama-3.2-1B-Instruct-Q6_K.gguf',
            subdir='llama3-1b-instruct',
        )

    elif size == '8B':
        fetch(
            'https://huggingface.co/bofenghuang/Meta-Llama-3-8B'
            '/resolve/main/original/tokenizer.model',
            'tokenizer.model',
            subdir='llama3-8b-sfr',
        )
        fetch(
            'https://huggingface.co/TriAiExperiments/SFR-Iterative-DPO-LLaMA-3-8B-R'
            '/resolve/main/model-00001-of-00004.safetensors',
            'model-00001-of-00004.safetensors',
            subdir='llama3-8b-sfr',
        )
        fetch(
            'https://huggingface.co/TriAiExperiments/SFR-Iterative-DPO-LLaMA-3-8B-R'
            '/resolve/main/model-00002-of-00004.safetensors',
            'model-00002-of-00004.safetensors',
            subdir='llama3-8b-sfr',
        )
        fetch(
            'https://huggingface.co/TriAiExperiments/SFR-Iterative-DPO-LLaMA-3-8B-R'
            '/resolve/main/model-00003-of-00004.safetensors',
            'model-00003-of-00004.safetensors',
            subdir='llama3-8b-sfr',
        )
        fetch(
            'https://huggingface.co/TriAiExperiments/SFR-Iterative-DPO-LLaMA-3-8B-R'
            '/resolve/main/model-00004-of-00004.safetensors',
            'model-00004-of-00004.safetensors',
            subdir='llama3-8b-sfr',
        )
        return fetch(
            'https://huggingface.co/TriAiExperiments/SFR-Iterative-DPO-LLaMA-3-8B-R'
            '/raw/main/model.safetensors.index.json',
            'model.safetensors.index.json',
            subdir='llama3-8b-sfr',
        )

    elif size == '70B':
        subdir = 'DeepSeek-R1-Distill-Llama-70B'
        model = fetch(
            'https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B'
            '/resolve/main/model.safetensors.index.json?download=true',
            'model.safetensors.index.json',
            subdir=subdir,
        )
        fetch(
            'https://huggingface.co/bofenghuang/Meta-Llama-3-8B'
            '/resolve/main/original/tokenizer.model',
            'tokenizer.model',
            subdir=subdir,
        )
        for i in range(17):
            fetch(
                f'https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B'
                f'/resolve/main/model-{i + 1:05d}-of-000017.safetensors?download=true',
                f'model-{i + 1:05d}-of-000017.safetensors',
                subdir=subdir,
            )
        return model

    else:
        raise ValueError(size)
