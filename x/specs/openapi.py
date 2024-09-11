import os.path

import yaml


def _main():
    with open(os.path.join(os.path.dirname(__file__), '..', 'llm', 'openai.yaml')) as f:
        spec = yaml.safe_load(f)
    print(spec)


if __name__ == '__main__':
    _main()
