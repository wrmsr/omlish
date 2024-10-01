import os.path


def load_secrets():
    with open(os.path.join(os.path.expanduser('~/.omlish-llm/.env'))) as f:
        for l in f:
            if l := l.strip():
                k, _, v = l.partition('=')
                os.environ[k] = v
