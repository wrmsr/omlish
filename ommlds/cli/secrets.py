import os

from omdev.home.secrets import load_secrets


##


def install_secrets() -> None:
    # FIXME: lol garbage
    for key in [
        'ANTHROPIC_API_KEY',
        'GEMINI_API_KEY',
        'GROQ_API_KEY',
        'HUGGINGFACE_TOKEN',
        'MISTRAL_API_KEY',
        'OPENAI_API_KEY',
        'TAVILY_API_KEY',
    ]:
        if (sec := load_secrets().try_get(key.lower())) is not None:
            os.environ[key] = sec.reveal()
