import yaml


def load_secrets() -> dict:
    with open('secrets.yml', 'r') as f:
        return yaml.safe_load(f)
