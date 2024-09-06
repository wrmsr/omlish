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
from omlish import marshal as msh
from omlish.formats import json

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

    es = build_dom_nodes(wiki)  # noqa

    def install_msh_poly(cls: type) -> None:
        p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]

    install_msh_poly(dom.Node)

    print(es_json := json.dumps_pretty(msh.marshal(es, dom.Nodes)))

    es2 = msh.unmarshal(json.loads(es_json), dom.Nodes)
    # assert users2 == users

    assert len(es2) == len(es)
