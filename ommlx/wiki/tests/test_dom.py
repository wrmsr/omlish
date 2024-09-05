"""
https://en.wikipedia.org/wiki/Help:Wikitext
https://www.mediawiki.org/wiki/Alternative_parsers

mfh:
https://mwparserfromhell.readthedocs.io/en/latest/api/mwparserfromhell.nodes.html#module-mwparserfromhell.nodes
  mfh.nodes.text.Text
  mfh.nodes.argument.Argument
  mfh.nodes.comment.Comment
  mfh.nodes.external_link.ExternalLink
  mfh.nodes.heading.Heading
  mfh.nodes.html_entity.HTMLEntity
  mfh.nodes.tag.Tag
  mfh.nodes.template.Template
  mfh.nodes.wikilink.Wikilink

wtp:
https://github.com/5j9/wikitextparser ??
https://github.com/TrueBrain/TrueWiki
https://github.com/TrueBrain/wikitexthtml
  Argument
  Bold
  Comment
  ExternalLink
  Italic
  Parameter
  ParserFunction
  Section
  Table
  Tag
  Template
  WikiLink
  WikiList
  WikiText


"""
import abc
import dataclasses as dc
import importlib.resources
import typing as ta  # noqa

import wikitextparser as wtp


@dc.dataclass(frozen=True)
class Dom(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class Text(Dom):
    s: str


@dc.dataclass(frozen=True)
class WikiLink(Dom):
    pass


@dc.dataclass(frozen=True)
class ExternalLink(Dom):
    pass


def test_dom():
    src = importlib.resources.files(__package__).joinpath('test.wiki').read_text()
    wiki = wtp.parse(src)
    print(wiki)
