from ..chopping import chop
from ..rendering import render


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


def test_softwrap2():
    root = chop("""\
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

       That blank line is preserved, and it is still softwrapped.
""")
    print(root)
    print(render(root))
    print()


def test_list_one_item():
    root = chop("""\
    This is the one item list test.
    
     - One item

    That was the one item list test.
""")
    print(root)
    print(render(root))
    print()
