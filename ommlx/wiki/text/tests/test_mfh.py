"""
https://github.com/WillKoehrsen/wikipedia-data-science/blob/master/notebooks/Downloading%20and%20Parsing%20Wikipedia%20Articles.ipynb
"""
from omlish import marshal as msh
from omlish.formats import json

from .. import mfh
from .data import WIKI_FILES


def test_dom():
    def install_msh_poly(cls: type) -> None:
        p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]

    install_msh_poly(mfh.Node)
    install_msh_poly(mfh.ContentNode)

    print()

    for n, src in sorted(WIKI_FILES.items(), key=lambda t: t[0]):
        print(n)

        doc = mfh.parse_doc(src)

        for path, child in mfh.traverse_node(doc):  # Noqa
            # print(([(f'{p.__class__.__name__}@{hex(id(p))[2:]}', a) for p, a in path], child))

            if isinstance(child, mfh.Template):
                if (tn := mfh.one_text(child.name)) and tn.split()[0] == 'Infobox':
                    dct = {}
                    for p in child.params:
                        if (k := mfh.one_text(p.name)) and (v := mfh.one_text(p.value)):
                            dct[k.strip()] = v.strip()

                    print(tn.partition(' ')[2].strip())
                    print(dct)

        es_msh = msh.marshal(doc, mfh.Doc)
        es_json = json.dumps_pretty(es_msh)
        # print(es_json)

        doc2 = msh.unmarshal(json.loads(es_json), mfh.Doc)
        assert len(doc.body) == len(doc2.body)

        print()
