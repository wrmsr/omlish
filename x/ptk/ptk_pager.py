#!/usr/bin/env python
# Copyright (c) 2014, Jonathan Slenders
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# * Neither the name of the {organization} nor the names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
A simple application that shows a Pager application.
"""
from pygments.lexers.python import PythonLexer  # noqa
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D  # noqa
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar
from prompt_toolkit.widgets import TextArea


# Create one text buffer for the main content.

_pager_py_path = __file__


with open(_pager_py_path, 'rb') as f:
    text = f.read().decode('utf-8')


def get_statusbar_text():
    return [
        ('class:status', _pager_py_path + ' - '),
        (
            'class:status.position',
            f'{text_area.document.cursor_position_row + 1}:{text_area.document.cursor_position_col + 1}',
        ),
        ('class:status', ' - Press '),
        ('class:status.key', 'Ctrl-C'),
        ('class:status', ' to exit, '),
        ('class:status.key', '/'),
        ('class:status', ' for searching.'),
    ]


search_field = SearchToolbar(
    text_if_not_searching=[('class:not-searching', "Press '/' to start searching.")],
)


text_area = TextArea(
    text=text,
    read_only=True,
    scrollbar=True,
    line_numbers=True,
    search_field=search_field,
    lexer=PygmentsLexer(PythonLexer),
)


root_container = HSplit(
    [
        # The top toolbar.
        Window(
            content=FormattedTextControl(get_statusbar_text),
            height=D.exact(1),
            style='class:status',
        ),
        # The main content.
        text_area,
        search_field,
    ],
)


# Key bindings.
bindings = KeyBindings()


@bindings.add('c-c')
@bindings.add('q')
def _(event):
    "Quit."
    event.app.exit()


style = Style.from_dict(
    {
        'status': 'reverse',
        'status.position': '#aaaa00',
        'status.key': '#ffaa00',
        'not-searching': '#888888',
    },
)


# create application.
application = Application(
    layout=Layout(root_container, focused_element=text_area),
    key_bindings=bindings,
    enable_page_navigation_bindings=True,  # noqa
    mouse_support=True,
    style=style,
    full_screen=True,
)


def run() -> None:
    application.run()


if __name__ == '__main__':
    run()
