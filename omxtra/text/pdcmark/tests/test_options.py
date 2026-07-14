import pytest

from omcore import dataclasses as dc

from ... import pdcmark as m


def test_options_kw_only():
    with pytest.raises(TypeError):
        m.Options(True)  # type: ignore


def test_commonmark_preset_defaults():
    assert m.COMMONMARK.tables is False
    assert m.COMMONMARK.strikethrough is False
    assert m.COMMONMARK.tasklists is False
    assert m.COMMONMARK.gfm_blockquote_kinds is False
    assert m.COMMONMARK.prescan_refdefs is False
    assert m.COMMONMARK.max_nested_parens == 32
    assert m.COMMONMARK.max_container_depth == 32
    assert m.COMMONMARK.broken_link_resolver is None


def test_gfm_preset_enables_gfm_extensions():
    assert m.GFM.tables is True
    assert m.GFM.strikethrough is True
    assert m.GFM.tasklists is True
    assert m.GFM.gfm_blockquote_kinds is True


def test_options_replace():
    custom = dc.replace(m.GFM, tables=False)
    assert custom.tables is False
    assert custom.strikethrough is True
    # original preset unchanged
    assert m.GFM.tables is True


class FixedResolver(m.BrokenLinkResolver):
    def resolve(self, link):
        return m.BrokenLinkResolution(dest_url='https://x', title='')


def test_broken_link_resolver_hook():
    custom = dc.replace(m.COMMONMARK, broken_link_resolver=FixedResolver())
    assert isinstance(custom.broken_link_resolver, m.BrokenLinkResolver)


def test_noop_broken_link_resolver_returns_none():
    r = m.NOOP_BROKEN_LINK_RESOLVER
    assert r(m.BrokenLink(span=(0, 5), link_type=m.LinkType.REFERENCE, reference='x')) is None
