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

from omlish import check

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

    def build_dom_node(n: mfn.Node | mfn.extras.Parameter) -> dom.Node:
        match n:
            case mfn.Comment(contents=s):
                return dom.Comment(s)

            case mfn.Text(value=s):
                return dom.Text(s)

            case mfn.Template(name=na, params=ps):
                return dom.Template(
                    build_dom_nodes(na),
                    [check.isinstance(p, dom.Parameter) for p in build_dom_nodes(ps)],
                )

            case mfn.extras.Parameter(name=n, value=v):
                return dom.Parameter(
                    build_dom_nodes(n),
                    build_dom_nodes(v),
                )

            case _:
                raise TypeError(n)

    def build_dom_nodes(w: Wikicode | ta.Iterable[mfn.Node | mfn.extras.Parameter]) -> dom.Nodes:
        if isinstance(w, Wikicode):
            return [build_dom_node(c) for c in w.nodes]

        elif isinstance(w, ta.Iterable):
            return [build_dom_node(c) for c in w]

        else:
            raise TypeError(w)

    es = build_dom_nodes(wiki)  # noqa

    print(es)