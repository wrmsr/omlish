# ruff: noqa: W293
import pytest

from ..chopping import chop
from ..rendering import dump
from ..rendering import render


def chop_and_say(s, **kwargs):
    print()

    print(kwargs)
    print(s)

    print('====')
    root = chop(s, **kwargs)
    print(dump(root))

    print('====')
    print(render(root))

    print()

    return root


@pytest.mark.parametrize('aic', [False, True, 'lists_only'])
def test_docwrap(aic):
    root = chop_and_say(  # noqa
        """\
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

     - here is an improper
      text child
     
     - item last

  the fuck?
""", allow_improper_list_children=aic)


def test_docwrap2():
    root = chop_and_say(  # noqa
        """\
    Hi! I am a long string! I am longer than twenty characters.

    This is a list:
     - The items of the list are indented by a single space, followed by a hyphen.
     - This is the second item.
      - This is a sub-list, indented by one.
      - This is the second item of the sub-list
     - This is the third item.
       - Weirdly, this sub-list is indented by two, as opposed to the previous item's sublist.
       - That difference is preserved.
     - This item has a blank line in it.

       That blank line is preserved, and it is still docwrapped.
""")


def test_list_one_item():
    root = chop_and_say(  # noqa
        """\
    This is the one item list test.
    
     - One item

    That was the one item list test.
    
    - One inline item

    That was the one inline item list test.
""")
