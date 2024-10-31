import contextlib

import llama_cpp
import llama_cpp.llama_tokenizer


def _main() -> None:
    with contextlib.ExitStack() as es:
        llama = es.enter_context(contextlib.closing(llama_cpp.Llama.from_pretrained(
            repo_id="Qwen/Qwen1.5-0.5B-Chat-GGUF",
            filename="*q8_0.gguf",
            tokenizer=llama_cpp.llama_tokenizer.LlamaHFTokenizer.from_pretrained(
                "Qwen/Qwen1.5-0.5B"
            ),
            verbose=False,
        )))

        response = llama.create_chat_completion(
            messages=[{"role": "user", "content": "What is the capital of France?"}],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "string"},
                        "capital": {"type": "string"},
                    },
                    "required": ["country", "capital"],
                },
            },
            stream=True,
        )

        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            if "content" not in delta:
                continue
            print(delta["content"], end="", flush=True)

        print()


if __name__ == '__main__':
    _main()
