"""
lol:
https://github.com/ollama/ollama/tree/50c05d57e0100625ee5bdd4ba9accec7f4536005/llm/ext_server

hf.hf_hub_download(repo_id='QuantFactory/Meta-Llama-3-8B-GGUF', filename='Meta-Llama-3-8B.Q8_0.gguf')

CMAKE_ARGS="-DGGML_METAL=on" ./python -mpip install llama-cpp-python
PATH="/usr/local/cuda-12.2/bin:$PATH" CMAKE_ARGS="-DGGML_CUDA=on" ./python -mpip install llama-cpp-python

holy god that's slow make a local cuda wheel
"""
import os.path


def _main() -> None:
    from llama_cpp import Llama

    llm = Llama(
        model_path=os.path.expanduser('~/.cache/huggingface/hub/models--QuantFactory--Meta-Llama-3-8B-GGUF/snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf'),
        # n_gpu_layers=-1, # Uncomment to use GPU acceleration
        # seed=1337, # Uncomment to set a specific seed
        # n_ctx=2048, # Uncomment to increase the context window
    )
    output = llm(
        "Q: Name the planets in the solar system? A: ",  # Prompt
        max_tokens=32,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
        stop=["Q:", "\n"],  # Stop generating just before the model would generate a new question
        echo=True  # Echo the prompt back in the output
    )  # Generate a completion, can also call create_completion
    print(output)


if __name__ == '__main__':
    _main()
