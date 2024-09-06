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

    for n, src in WIKI_FILES.items():
        print(n)

        nodes = mfh.parse_nodes(src)

        es_json = json.dumps_pretty(msh.marshal(nodes, mfh.Nodes))
        # print(es_json)
        nodes2 = msh.unmarshal(json.loads(es_json), mfh.Nodes)  # type: ignore
        assert len(nodes) == len(nodes2)
