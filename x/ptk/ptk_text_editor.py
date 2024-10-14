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
A simple example of a Notepad-like text editor.
"""
import asyncio
import datetime
import sys
import typing as ta

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.layout.containers import Float
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.containers import VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.search import start_search
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Button
from prompt_toolkit.widgets import Dialog
from prompt_toolkit.widgets import Label
from prompt_toolkit.widgets import MenuContainer
from prompt_toolkit.widgets import MenuItem
from prompt_toolkit.widgets import SearchToolbar
from prompt_toolkit.widgets import TextArea


class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to instantiate this as an object and pass at
    around.
    """

    show_status_bar = True
    current_path = None


def get_statusbar_text():
    return ' Press Ctrl-C to open menu. '


def get_statusbar_right_text():
    return f' {text_field.document.cursor_position_row + 1}:{text_field.document.cursor_position_col + 1}  '


search_toolbar = SearchToolbar()
text_field = TextArea(
    lexer=DynamicLexer(
        lambda: PygmentsLexer.from_filename(
            ApplicationState.current_path or '.txt', sync_from_start=False,
        ),
    ),
    scrollbar=True,
    line_numbers=True,
    search_field=search_toolbar,
)


class TextInputDialog:
    def __init__(self, title='', label_text='', completer=None):
        super().__init__()
        self.future = asyncio.Future()

        def accept_text(buf):
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept():
            self.future.set_result(self.text_area.text)

        def cancel():
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
        )

        ok_button = Button(text='OK', handler=accept)
        cancel_button = Button(text='Cancel', handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


class MessageDialog:
    def __init__(self, title, text):
        super().__init__()
        self.future = asyncio.Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text='OK', handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


body = HSplit([
    text_field,
    search_toolbar,
    ConditionalContainer(
        content=VSplit(
            [
                Window(
                    FormattedTextControl(get_statusbar_text),
                    style='class:status',
                ),
                Window(
                    FormattedTextControl(get_statusbar_right_text),
                    style='class:status.right',
                    width=9,
                    align=WindowAlign.RIGHT,
                ),
            ],
            height=1,
        ),
        filter=Condition(lambda: ApplicationState.show_status_bar),
    ),
])


# Global key bindings.
bindings = KeyBindings()


@bindings.add('c-c')
def _(event):
    """Focus menu."""

    event.app.layout.focus(root_container.window)


@bindings.add('c-\\')
def _(event):
    """Force exit."""
    sys.exit(1)


#
# Handlers for menu items.
#


def do_open_file():
    async def coroutine():
        open_dialog = TextInputDialog(
            title='Open file',
            label_text='Enter the path of a file:',
            completer=PathCompleter(),
        )

        path = await show_dialog_as_float(open_dialog)
        ApplicationState.current_path = path

        if path is not None:
            try:
                with open(path, 'rb') as f:
                    text_field.text = f.read().decode('utf-8', errors='ignore')
            except OSError as e:
                show_message('Error', f'{e}')

    asyncio.ensure_future(coroutine())


def do_about():
    show_message('About', 'Text editor demo.\nCreated by Jonathan Slenders.')


def show_message(title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    asyncio.ensure_future(coroutine())


async def show_dialog_as_float(dialog):
    """Coroutine."""

    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


def do_new_file():
    text_field.text = ''


def do_exit():
    get_app().exit()


def do_time_date():
    text = datetime.datetime.now().isoformat()
    text_field.buffer.insert_text(text)


def do_go_to():
    async def coroutine():
        dialog = TextInputDialog(title='Go to line', label_text='Line number:')

        line_number = await show_dialog_as_float(dialog)

        try:
            line_number = int(line_number)
        except ValueError:
            show_message('Invalid line number')
        else:
            text_field.buffer.cursor_position = (
                text_field.buffer.document.translate_row_col_to_index(
                    line_number - 1, 0,
                )
            )

    asyncio.ensure_future(coroutine())


def do_undo():
    text_field.buffer.undo()


def do_cut():
    data = text_field.buffer.cut_selection()
    get_app().clipboard.set_data(data)


def do_copy():
    data = text_field.buffer.copy_selection()
    get_app().clipboard.set_data(data)


def do_delete():
    text_field.buffer.cut_selection()


def do_find():
    start_search(text_field.control)


def do_find_next():
    search_state = get_app().current_search_state

    cursor_position = text_field.buffer.get_search_position(
        search_state, include_current_position=False,
    )
    text_field.buffer.cursor_position = cursor_position


def do_paste():
    text_field.buffer.paste_clipboard_data(get_app().clipboard.get_data())


def do_select_all():
    text_field.buffer.cursor_position = 0
    text_field.buffer.start_selection()
    text_field.buffer.cursor_position = len(text_field.buffer.text)


def do_status_bar():
    ApplicationState.show_status_bar = not ApplicationState.show_status_bar


#
# The menu container.
#


def _resend_keypress(kb: KeyBindings, event: KeyPressEvent, new_key: str) -> None:
    # TODO: KeyProcessor._process handles eager, prefixes, etc
    bs = [b for b in kb.get_bindings_for_keys((new_key,)) if b.filter()]
    bs[-1].call(event)


class MyMenuContainer(MenuContainer):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        kb = self.control.key_bindings

        @Condition
        def in_menu() -> bool:
            return len(self.selected_menu) > 0

        @kb.add("c-f", filter=in_menu)
        def _up_in_menu(event: KeyPressEvent) -> None:
            _resend_keypress(kb, event, 'right')

        @kb.add("c-b", filter=in_menu)
        def _up_in_menu(event: KeyPressEvent) -> None:
            _resend_keypress(kb, event, 'left')

        @kb.add("c-p", filter=in_menu)
        def _up_in_menu(event: KeyPressEvent) -> None:
            _resend_keypress(kb, event, 'up')

        @kb.add("c-n", filter=in_menu)
        def _down_in_menu(event: KeyPressEvent) -> None:
            _resend_keypress(kb, event, 'down')


root_container = MyMenuContainer(
    body=body,
    menu_items=[
        MenuItem(
            'File',
            children=[
                MenuItem('New...', handler=do_new_file),
                MenuItem('Open...', handler=do_open_file),
                MenuItem('Save'),
                MenuItem('Save as...'),
                MenuItem('-', disabled=True),
                MenuItem('Exit', handler=do_exit),
            ],
        ),
        MenuItem(
            'Edit',
            children=[
                MenuItem('Undo', handler=do_undo),
                MenuItem('Cut', handler=do_cut),
                MenuItem('Copy', handler=do_copy),
                MenuItem('Paste', handler=do_paste),
                MenuItem('Delete', handler=do_delete),
                MenuItem('-', disabled=True),
                MenuItem('Find', handler=do_find),
                MenuItem('Find next', handler=do_find_next),
                MenuItem('Replace'),
                MenuItem('Go To', handler=do_go_to),
                MenuItem('Select All', handler=do_select_all),
                MenuItem('Time/Date', handler=do_time_date),
            ],
        ),
        MenuItem(
            'View',
            children=[MenuItem('Status Bar', handler=do_status_bar)],
        ),
        MenuItem(
            'Info',
            children=[MenuItem('About', handler=do_about)],
        ),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
    ],
    key_bindings=bindings,
)


style = Style.from_dict(
    {
        'status': 'reverse',
        'shadow': 'bg:#440044',
    },
)


layout = Layout(root_container, focused_element=text_field)


application = Application(
    layout=layout,
    enable_page_navigation_bindings=True,  # noqa
    style=style,
    mouse_support=True,
    full_screen=True,
)


def run() -> None:
    application.run()


if __name__ == '__main__':
    run()
