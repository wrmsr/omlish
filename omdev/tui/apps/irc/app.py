"""
TODO:
 - use omdev.irc obv
 - readliney input
 - command suggest / autocomplete
 - disable command palette
 - grow input box for multiline
 - styled text
"""
import shlex
import typing as ta

from omlish import lang

from ... import textual as tx
from .client import IrcClient
from .commands import ALL_COMMANDS
from .commands import IrcCommand


##


class IrcWindow:
    """Represents a chat window."""

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name: str = name
        self.lines: list[str] = []
        self.unread: int = 0
        self.displayed_line_count: int = 0  # Track how many lines are currently displayed

    def add_line(self, line: str) -> None:
        self.lines.append(line)
        self.unread += 1


class IrcApp(tx.App):
    """IRC client application."""

    _commands: ta.ClassVar[ta.Mapping[str, IrcCommand]] = ALL_COMMANDS

    CSS = """
    #messages {
        height: 1fr;
        overflow-y: auto;
        border: none;
        padding: 0;
    }

    #status {
        height: 1;
        background: $primary;
        color: $text;
        border: none;
        padding: 0;
    }

    #input {
        dock: bottom;
        border: none;
        padding: 0;
    }
    """

    BINDINGS: ta.ClassVar[ta.Sequence[tx.Binding]] = [
        tx.Binding('ctrl+n', 'next_window', 'Next Window', show=False),
        tx.Binding('ctrl+p', 'prev_window', 'Previous Window', show=False),
    ]

    def __init__(
            self,
            *,
            startup_commands: ta.Sequence[str] | None = None,
    ) -> None:
        super().__init__()

        self._client: IrcClient | None = None
        self._windows: dict[str, IrcWindow] = {'system': IrcWindow('system')}
        self._window_order: list[str] = ['system']
        self._current_window_idx: int = 0
        self._current_channel: str | None = None
        self._startup_commands: ta.Sequence[str] = startup_commands or []

    @property
    def client(self) -> IrcClient | None:
        return self._client

    @property
    def current_channel(self) -> str | None:
        return self._current_channel

    #

    def compose(self) -> tx.ComposeResult:
        text_area = tx.TextArea(id='messages', read_only=True, show_line_numbers=False)
        text_area.cursor_blink = False
        yield text_area
        yield tx.Static('', id='status')
        yield tx.Input(placeholder='Enter command or message', id='input', select_on_focus=False)

    async def on_mount(self) -> None:
        """Initialize on mount."""

        self._client = IrcClient(self.on_irc_message)
        self.update_display()
        self.query_one('#input').focus()

        # Show connection prompt
        await self.add_message('system', 'IRC Client - Use /connect <server> <port> <nickname>')
        await self.add_message('system', 'Example: /connect irc.libera.chat 6667 mynick')

        # Execute startup commands
        for cmd in self._startup_commands:
            # Add leading slash if not present
            if not cmd.startswith('/'):
                cmd = '/' + cmd
            await self.add_message('system', f'Executing: {cmd}')
            await self.handle_command(cmd)

    async def on_key(self, event: tx.Key) -> None:
        """Handle key events - redirect typing to input when messages area is focused."""

        focused = self.focused
        if focused and focused.id == 'messages':
            # If a printable character or common input key is pressed, focus the input and forward event
            if event.is_printable or event.key in ('space', 'backspace', 'delete'):
                input_widget = self.query_one('#input', tx.Input)
                input_widget.focus()
                # Post the key event to the input widget so it handles it naturally
                input_widget.post_message(tx.Key(event.key, event.character))
                # Stop the event from being processed by the messages widget
                event.stop()

    async def on_input_submitted(self, event: tx.Input.Submitted) -> None:
        """Handle user input."""

        text = event.value.strip()
        event.input.value = ''

        if not text:
            return

        # Handle commands
        if text.startswith('/'):
            await self.handle_command(text)
        else:
            # Send message to current channel
            if self._current_channel and self._client and self._client.connected:
                await self._client.privmsg(self._current_channel, text)
                await self.add_message(self._current_channel, f'<{self._client.nickname}> {text}')
            else:
                await self.add_message('system', 'Not in a channel or not connected')

    async def handle_command(self, text: str) -> None:
        """Handle IRC commands."""

        try:
            parts = shlex.split(text)
        except ValueError as e:
            await self.add_message('system', f'Invalid command syntax: {e}')
            return

        if not parts:
            return

        cmd = parts[0].lstrip('/').lower()
        argv = parts[1:]

        command = self._commands.get(cmd)
        if command:
            await command.run(self, argv)
        else:
            await self.add_message('system', f'Unknown command: /{cmd}')

    def action_next_window(self) -> None:
        """Switch to next window."""

        if len(self._window_order) > 1:
            self._current_window_idx = (self._current_window_idx + 1) % len(self._window_order)
            self.update_display()

    def action_prev_window(self) -> None:
        """Switch to previous window."""

        if len(self._window_order) > 1:
            self._current_window_idx = (self._current_window_idx - 1) % len(self._window_order)
            self.update_display()

    def get_or_create_window(self, name: str) -> IrcWindow:
        """Get or create a window."""

        if name not in self._windows:
            self._windows[name] = IrcWindow(name)
            self._window_order.append(name)
        return self._windows[name]

    def switch_to_window(self, name: str) -> None:
        """Switch to a specific window."""

        if name in self._window_order:
            self._current_window_idx = self._window_order.index(name)
            self.update_display()

    async def add_message(self, window_name: str, message: str) -> None:
        """Add a message to a window."""

        window = self.get_or_create_window(window_name)
        timestamp = lang.utcnow().strftime('%H:%M')
        window.add_line(f'[{timestamp}] {message}')
        self.update_display()

    async def on_irc_message(self, window_name: str, message: str) -> None:
        """Callback for IRC messages."""

        await self.add_message(window_name, message)

    _last_window: str | None = None

    def update_display(self) -> None:
        """Update the display."""

        current_window_name = self._window_order[self._current_window_idx]
        current_window = self._windows[current_window_name]

        # Update current channel for sending messages
        self._current_channel = current_window_name if current_window_name.startswith('#') else None

        # Mark as read
        current_window.unread = 0

        # Update messages display
        messages_widget = self.query_one('#messages', tx.TextArea)

        # Check if we switched windows or need full reload
        window_changed = self._last_window != current_window_name
        self._last_window = current_window_name

        lines_to_show = current_window.lines[-100:]  # Last 100 lines

        if window_changed:
            # Full reload when switching windows
            messages_widget.load_text('\n'.join(lines_to_show))
            current_window.displayed_line_count = len(lines_to_show)

        else:
            # Append only new lines
            new_line_count = len(lines_to_show) - current_window.displayed_line_count
            if new_line_count > 0:
                new_lines = lines_to_show[-new_line_count:]
                # Get the end position
                doc = messages_widget.document
                end_line = doc.line_count - 1
                end_col = len(doc.get_line(end_line))
                # Append new lines using insert
                prefix = '\n' if len(doc.text) > 0 else ''
                messages_widget.insert(prefix + '\n'.join(new_lines), location=(end_line, end_col))
                current_window.displayed_line_count = len(lines_to_show)

        # Update status line
        window_list = []
        for i, name in enumerate(self._window_order):
            win = self._windows[name]
            indicator = f'[{i + 1}:{name}]'
            if i == self._current_window_idx:
                indicator = f'[{i + 1}:{name}*]'
            elif win.unread > 0:
                indicator = f'[{i + 1}:{name}({win.unread})]'
            window_list.append(indicator)

        status_text = ' '.join(window_list)
        self.query_one('#status', tx.Static).update(status_text)

    async def on_unmount(self) -> None:
        if (cl := self._client) is not None:
            await cl.shutdown()
