"""
https://github.com/WillKoehrsen/wikipedia-data-science/blob/master/notebooks/Downloading%20and%20Parsing%20Wikipedia%20Articles.ipynb
"""
import importlib.resources

from omlish import marshal as msh
from omlish.formats import json

from . import mfh


def test_dom():
    src = importlib.resources.files(__package__).joinpath('test.wiki').read_text()

    nodes = mfh.parse_nodes(src)

    def install_msh_poly(cls: type) -> None:
        p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]

    install_msh_poly(mfh.Node)

    print(es_json := json.dumps_pretty(msh.marshal(nodes, mfh.Nodes)))
    nodes2 = msh.unmarshal(json.loads(es_json), mfh.Nodes)  # type: ignore
    assert len(nodes) == len(nodes2)
