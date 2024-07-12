import typing as ta

import yaml


def load_secrets() -> dict[str, ta.Any]:
    with open('secrets.yml', 'r') as f:
        return yaml.safe_load(f)
