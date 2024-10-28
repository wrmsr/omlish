import os.path

from omdev.secrets import load_secrets as _load_secrets


def load_secrets() -> None:
    sec = _load_secrets()

    os.environ['OPENAI_API_KEY'] = sec.get('openai_api_key').reveal()
    os.environ['TAVILY_API_KEY'] = sec.get('tavily_api_key').reveal()
    os.environ['ANTHROPIC_API_KEY'] = sec.get('anthropic_api_key').reveal()
    os.environ['MISTRAL_API_KEY'] = sec.get('mistral_api_key').reveal()
