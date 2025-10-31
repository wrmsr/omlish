from ..softwrap import Block
from ..softwrap import Indent
from ..softwrap import Text
from ..softwrap import blockify
from ..softwrap import chop
from ..softwrap import render


def test_blockify():
    print(blockify(
        Text('hi'),
        Block([Text('foo'), Text('foo2')]),
        Block([Text('bar'), Text('bar2')]),
    ))
    print(blockify(
        Text('hi'),
        Indent(2, Text('a')),
        Indent(2, Text('b')),
    ))


def test_softwrap():
    root = chop("""\
    Hi I'm some text.
    
    I am more text.
    
    This is a list:
     - Item one
     - item 2
       with another line
    
     - here is a proper nested list
       - subitem 1
         with a second line
       - subitem 2
       
       - subitem 3
    
     - here is an improper nested list
      - subitem 1
        with a second line
        and a third
      - subitem 2
      
      - subitem 3
     
     - item last

  the fuck?
""")
    print(root)
    print(render(root))
    print()


def test_marshal():
    # from omlish.formats import json
    # from omlish import marshal as msh
    #
    # msh.install_standard_factories(
    #     *msh.standard_polymorphism_factories(part_poly := msh.polymorphism_from_subclasses(Part)),
    #     msh.PolymorphismUnionMarshalerFactory(part_poly.impls, allow_partial=True),
    # )
    #
    # print(json.dumps_pretty(msh.marshal(root, Part)))
    # print()

    pass
