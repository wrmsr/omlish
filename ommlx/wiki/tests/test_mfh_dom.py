"""
https://github.com/WillKoehrsen/wikipedia-data-science/blob/master/notebooks/Downloading%20and%20Parsing%20Wikipedia%20Articles.ipynb

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

"""
import importlib.resources
import typing as ta

import mwparserfromhell as mfh
import mwparserfromhell.nodes as mfn

from . import dom


Wikicode: ta.TypeAlias = mfh.wikicode.Wikicode


def test_dom():
    src = importlib.resources.files(__package__).joinpath('test.wiki').read_text()

    wiki = mfh.parse(src)

    wikilinks = [x.title for x in wiki.filter_wikilinks()]
    print(f'There are {len(wikilinks)} wikilinks.')

    external_links = [(x.title, x.url) for x in wiki.filter_external_links()]
    print(f'There are {len(external_links)} external links.')

    templates = wiki.filter_templates()
    print(f'There are {len(templates)} templates.')

    infobox = wiki.filter_templates(matches='Infobox periodic table')[0]
    print(infobox)

    information = {
        param.name.strip_code().strip(): param.value.strip_code().strip()
        for param in infobox.params
    }
    print(information)

    def find_template(wiki: Wikicode, template: str) -> list[dict[str, Wikicode]]:
        matches = wiki.filter_templates(matches=template)
        matches = [x for x in matches if x.name.strip_code().strip().lower() == template.lower()]
        return [
            {
                param.name.strip_code().strip(): param.value
                for param in match.params
                if param.value.strip_code().strip()
            }
            for match in matches
        ]

    r = find_template(wiki, 'Infobox periodic table group/header')
    print(r)

    es: list[dom.Dom] = []

    for n in wiki.nodes:
        match n:
            case mfn.Comment(contents=s):
                es.append(dom.Comment(s))
            case mfn.Text(value=s):
                es.append(dom.Text(s))
            case _:
                raise TypeError(n)
