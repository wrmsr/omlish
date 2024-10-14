import pytest

from ... import check
from .. import hub


@pytest.mark.online
def test_hub_image_version():
    repo = 'library/nginx'
    info = check.not_none(hub.get_hub_repo_info(repo))
    assert info.tags
    assert info.manifests


def test_select_latest_tag():
    tags = [
        '1',
        '1.1',
        '1.1-foo',
        '1.2-foo',
        '1.2-bar',
        '1.2.1-bar',
        '1.3-bar',
        '1.4',
        '1.10',
        '2-bar',
    ]

    assert hub.select_latest_tag(tags) == '1.10'
    assert hub.select_latest_tag(tags, suffix='foo') == '1.2-foo'
    assert hub.select_latest_tag(tags, suffix='bar') == '2-bar'
    assert hub.select_latest_tag(tags, base='1.2-bar') == '1.3-bar'
