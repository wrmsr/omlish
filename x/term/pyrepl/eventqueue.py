#   Copyright 2000-2008 Michael Hudson-Doyle <micahel@gmail.com>
#                        Armin Rigo
#
#                    All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and its documentation for any purpose is hereby granted
# without fee, provided that the above copyright notice appear in all copies and that both that copyright notice and
# this permission notice appear in supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES
# OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""
OS-independent base for an event and VT sequence scanner

See unix_eventqueue and windows_eventqueue for subclasses.
"""
import collections

from omlish import check

from .console import ConsoleEvent
from .keymap import compile_keymap


##


class BaseEventQueue:
    def __init__(
            self,
            encoding: str,
            keymap_dict: dict[bytes, str],
    ) -> None:
        super().__init__()

        self._compiled_keymap = compile_keymap(keymap_dict)
        self._keymap = self._compiled_keymap
        # trace('keymap {k!r}', k=self._keymap)
        self._encoding = encoding
        self._events: collections.deque[ConsoleEvent] = collections.deque()
        self._buf = bytearray()

    @property
    def encoding(self) -> str:
        return self._encoding

    def get(self) -> ConsoleEvent | None:
        """Retrieves the next event from the queue."""

        if self._events:
            return self._events.popleft()
        else:
            return None

    def empty(self) -> bool:
        """Checks if the queue is empty."""

        return not self._events

    def flush_buf(self) -> bytearray:
        """Flushes the buffer and returns its contents."""

        old = self._buf
        self._buf = bytearray()
        return old

    def insert(self, event: ConsoleEvent) -> None:
        """Inserts an event into the queue."""

        # trace('added event {event}', event=event)
        self._events.append(event)

    def push(self, char: int | bytes) -> None:
        """Processes a character by updating the buffer and handling special key mappings."""

        check.isinstance(char, (int, bytes))
        ord_char = char if isinstance(char, int) else ord(char)
        char = ord_char.to_bytes()
        self._buf.append(ord_char)

        if char in self._keymap:
            if self._keymap is self._compiled_keymap:
                # sanity check, buffer is empty when a special key comes
                check.state(len(self._buf) == 1)
            k = self._keymap[char]
            # trace('found map {k!r}', k=k)
            if isinstance(k, dict):
                self._keymap = k
            else:
                self.insert(ConsoleEvent('key', k, bytes(self.flush_buf())))
                self._keymap = self._compiled_keymap

        elif self._buf and self._buf[0] == 27:  # escape
            # escape sequence not recognized by our keymap: propagate it outside so that i can be recognized as an M-...
            # key (see also the docstring in keymap.py
            # trace('unrecognized escape sequence, propagating...')
            self._keymap = self._compiled_keymap
            self.insert(ConsoleEvent('key', '\033', b'\033'))
            for _c in self.flush_buf()[1:]:
                self.push(_c)

        else:
            try:
                decoded = bytes(self._buf).decode(self._encoding)
            except UnicodeError:
                return
            else:
                self.insert(ConsoleEvent('key', decoded, bytes(self.flush_buf())))
            self._keymap = self._compiled_keymap
