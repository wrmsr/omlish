#   Copyright 2000-2004 Michael Hudson-Doyle <micahel@gmail.com>
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
#
##
# (naming modules after builtin functions is not such a hot idea...)
#
# an KeyTrans instance translates Event objects into Command objects
#
# hmm, at what level do we want [C-i] and [tab] to be equivalent? [meta-a] and [esc a]?  obviously, these are going to
# be equivalent for the UnixConsole, but should they be for PygameConsole?
#
# it would in any situation seem to be a bad idea to bind, say, [tab] and [C-i] to *different* things... but should
# binding one bind the other?
#
# executive, temporary decision: [tab] and [C-i] are distinct, but [meta-key] is identified with [esc key].  We demand
# that any console class does quite a lot towards emulating a unix terminal.
import abc
import collections
import typing as ta
import unicodedata

from omlish import check
from omlish import lang

from .console import ConsoleEvent
from .keymap import compile_keymap
from .keymap import parse_keys
from .types import CommandName


##


class InputEvent(ta.NamedTuple):
    cls: ta.Any | None
    arg: ta.Any


class InputTranslator(lang.Abstract):
    @abc.abstractmethod
    def push(self, evt: ConsoleEvent) -> None:
        pass

    @abc.abstractmethod
    def get(self) -> InputEvent | None:
        return None

    @abc.abstractmethod
    def empty(self) -> bool:
        return True


class KeymapTranslator(InputTranslator):
    def __init__(
            self,
            keymap: ta.Sequence[tuple[str, CommandName]],
            *,
            invalid_cls: ta.Any | None = None,
            character_cls: ta.Any | None = None,
    ) -> None:
        super().__init__()

        self._keymap = keymap
        self._invalid_cls = invalid_cls
        self._character_cls = character_cls

        d: dict[tuple[str, ...], str] = {
            tuple(parse_keys(keyspec)): command
            for keyspec, command in keymap
        }

        self._k = self._ck = compile_keymap(d)

        self._results: collections.deque[InputEvent] = collections.deque()

        self._stack: list[str] = []

    def push(self, evt: ConsoleEvent) -> None:
        key = check.non_empty_str(evt.data)
        d = self._k.get(key)

        if isinstance(d, dict):
            self._stack.append(key)
            self._k = d

        else:
            if d is None:
                if self._stack or len(key) > 1 or unicodedata.category(key) == 'C':
                    self._results.append(InputEvent(self._invalid_cls, [*self._stack, key]))
                else:
                    # small optimization:
                    self._k[key] = self._character_cls
                    self._results.append(InputEvent(self._character_cls, [key]))

            else:
                self._results.append(InputEvent(d, [*self._stack, key]))

            self._stack = []
            self._k = self._ck

    def get(self) -> InputEvent | None:
        if self._results:
            return self._results.popleft()
        else:
            return None

    def empty(self) -> bool:
        return not self._results
