import transformers


def _main():
    model_name = "meta-llama/Meta-Llama-3-8B"
    pipeline = transformers.pipeline("text-generation", model=model_name)
    print(pipeline('hi there'))


if __name__ == '__main__':
    _main()
