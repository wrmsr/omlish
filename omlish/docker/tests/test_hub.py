import pytest

from .. import hub


@pytest.mark.online
def test_hub_image_version():
    repo = 'library/nginx'
    info = hub.get_hub_repo_info(repo)
    assert info.tags
    assert info.manifests
