from ..secrets import load_secrets


def get_db_url() -> str:
    cfg = load_secrets()
    return f'postgresql+asyncpg://{cfg["postgres_user"]}:{cfg["postgres_pass"]}@{cfg["postgres_host"]}:5432'
