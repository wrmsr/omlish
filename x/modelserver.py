import transformers


class ModelServer:
    pass


def _main():
    generator = transformers.pipeline('text-generation', model='facebook/opt-125m')
    print(generator('Hello, my name is'))


if __name__ == '__main__':
    _main()
