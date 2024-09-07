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

    for n, src in WIKI_FILES.items():
        print(n)

        doc = mfh.parse_doc(src)

        for path, child in mfh.traverse_node(doc):  # Noqa
            # print(([(f'{p.__class__.__name__}@{hex(id(p))[2:]}', a) for p, a in path], child))
            pass

        es_json = json.dumps_pretty(msh.marshal(doc, mfh.Doc))
        # print(es_json)

        doc2 = msh.unmarshal(json.loads(es_json), mfh.Doc)
        assert len(doc.body) == len(doc2.body)
