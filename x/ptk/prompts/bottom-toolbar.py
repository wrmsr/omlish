#!/usr/bin/env python
"""
A few examples of displaying a bottom toolbar.

The ``prompt`` function takes a ``bottom_toolbar`` attribute.
This can be any kind of formatted text (plain text, HTML or ANSI), or
it can be a callable that takes an App and returns an of these.

The bottom toolbar will always receive the style 'bottom-toolbar', and the text
inside will get 'bottom-toolbar.text'. These can be used to change the default
style.
"""
import time

from omdev import ptk


def main() -> None:
    # Example 1: fixed text.
    text = ptk.prompt(
        'Say something: ',
        bottom_toolbar='This is a toolbar',
    )
    print(f'You said: {text}')

    # Example 2: fixed text from a callable:
    def get_toolbar():
        return f'Bottom toolbar: time={time.time()!r}'

    text = ptk.prompt(
        'Say something: ',
        bottom_toolbar=get_toolbar,
        refresh_interval=.5,
    )
    print(f'You said: {text}')

    # Example 3: Using HTML:
    text = ptk.prompt(
        'Say something: ',
        bottom_toolbar=ptk.HTML(
            '(html) <b>This</b> <u>is</u> a <style bg="ansired">toolbar</style>',
        ),
    )
    print(f'You said: {text}')

    # Example 4: Using ANSI:
    text = ptk.prompt(
        'Say something: ',
        bottom_toolbar=ptk.ANSI(
            '(ansi): \x1b[1mThis\x1b[0m \x1b[4mis\x1b[0m a \x1b[91mtoolbar',
        ),
    )
    print(f'You said: {text}')

    # Example 5: styling differently.
    style = ptk.Style.from_dict({
        'bottom-toolbar': '#aaaa00 bg:#ff0000',
        'bottom-toolbar.text': '#aaaa44 bg:#aa4444',
    })

    text = ptk.prompt(
        'Say something: ',
        bottom_toolbar='This is a toolbar',
        style=style,
    )
    print(f'You said: {text}')

    # Example 6: Using a list of tokens.
    def get_bottom_toolbar():
        return [
            ('', ' '),
            ('bg:#ff0000 fg:#000000', 'This'),
            ('', ' is a '),
            ('bg:#ff0000 fg:#000000', 'toolbar'),
            ('', '. '),
        ]

    text = ptk.prompt(
        'Say something: ',
        bottom_toolbar=get_bottom_toolbar,
    )
    print(f'You said: {text}')

    # Example 7: multiline fixed text.
    text = ptk.prompt(
        'Say something: ',
        bottom_toolbar='This is\na multiline toolbar',
    )
    print(f'You said: {text}')


if __name__ == '__main__':
    main()
