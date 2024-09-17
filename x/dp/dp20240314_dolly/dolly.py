"""
https://github.com/databrickslabs/dolly

https://huggingface.co/databricks/dolly-v2-3b/blob/main/instruct_pipeline.py
"""
import torch
import transformers


def _main():
    instruct_pipeline = transformers.pipeline(
        model="databricks/dolly-v2-12b",
        torch_dtype=torch.float16,
        trust_remote_code=True,
        device_map="auto",
    )

    print(instruct_pipeline("Explain to me the difference between nuclear fission and fusion."))


if __name__ == '__main__':
    _main()
