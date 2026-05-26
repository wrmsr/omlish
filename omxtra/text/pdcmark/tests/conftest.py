import os.path

import pytest


# Resolve a directory from a test-relative path. The pulldown-cmark submodule lives at the repo
# root; tests reference fixture files there.
REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
PDCMARK_SUBMODULE = os.path.join(REPO_ROOT, 'pulldown-cmark', 'pulldown-cmark')


@pytest.fixture(scope='session')
def repo_root() -> str:
    return REPO_ROOT


@pytest.fixture(scope='session')
def pulldown_cmark_root() -> str:
    return os.path.join(os.path.dirname(__file__), 'pulldown-cmark')
