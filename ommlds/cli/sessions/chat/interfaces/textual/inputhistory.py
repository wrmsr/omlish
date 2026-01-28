import abc
import os
import typing as ta

from omlish import lang
from omlish.formats import json


##


class InputHistoryStorage(lang.Abstract):
    @abc.abstractmethod
    def load(self) -> ta.Awaitable[list[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, entries: ta.Sequence[str]) -> ta.Awaitable[None]:
        raise NotImplementedError


class InMemoryInputHistoryStorage(InputHistoryStorage):
    def __init__(self) -> None:
        super().__init__()

        self._entries: list[str] = []

    async def load(self) -> list[str]:
        return list(self._entries)

    async def save(self, entries: ta.Sequence[str]) -> None:
        self._entries = list(entries)


class FileInputHistoryStorage(InputHistoryStorage):
    def __init__(self, *, path: str) -> None:
        super().__init__()

        self._path = path

    async def load(self) -> list[str]:
        if not os.path.exists(self._path):
            return []

        try:
            with open(self._path) as f:  # noqa
                content = f.read()
        except OSError:
            return []

        data = json.loads(content)

        if isinstance(data, list) and all(isinstance(e, str) for e in data):
            return data
        return []

    async def save(self, entries: ta.Sequence[str]) -> None:
        content = json.dumps_pretty(list(entries))
        dir_path = os.path.dirname(self._path)

        try:
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(self._path, 'w') as f:  # noqa
                f.write(content)
        except OSError:
            pass


##


class InputHistoryManager:
    """
    Manages input history with readline-style navigation.

    History position semantics:
    - Position starts at len(history) (one past the end)
    - Moving 'previous' decrements position
    - Moving 'next' increments position
    - Position is clamped to [0, len(history)]
    - Position len(history) represents 'no history item selected'
    """

    def __init__(
            self,
            *,
            storage: InputHistoryStorage,
            max_entries: int = 1000,
    ) -> None:
        super().__init__()

        self._storage = storage
        self._max_entries = max_entries

    #

    _entries: list[str]
    _position: int = 0

    async def load_if_necessary(self) -> None:
        try:
            self._entries  # noqa
        except AttributeError:
            pass
        else:
            return

        self._entries = await self._storage.load()
        self._position = len(self._entries)

    #

    _current_draft: str = ''

    async def add(self, text: str) -> None:
        """Add a new history entry and reset position."""

        if not text.strip():
            return

        await self.load_if_necessary()

        # Don't add duplicate consecutive entries
        if self._entries and self._entries[-1] == text:
            self.reset_position()
            return

        self._entries.append(text)

        # Trim to max size
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        await self._storage.save(self._entries)
        self.reset_position()

    def get_previous(self, text: str | None = None) -> str | None:
        """
        Navigate to previous (older) history entry.

        Args:
            text: Current text in the input field (saved as draft when at end of history)

        Returns:
            The previous history entry, or None if at the beginning
        """

        try:
            entries = self._entries
        except AttributeError:
            return None
        if entries:
            return None

        # Save current draft if we're at the end
        if self._position == len(entries) and text is not None:
            self._current_draft = text

        # Move to previous entry
        if self._position > 0:
            self._position -= 1
            return entries[self._position]

        # Already at oldest entry
        return entries[0] if entries else None

    def get_next(self, text: str | None = None) -> str | None:
        """
        Navigate to next (newer) history entry.

        Args:
            text: Current text in the input field (unused for now)

        Returns:
            The next history entry, the saved draft if moving past the end, or None
        """

        try:
            entries = self._entries
        except AttributeError:
            return None
        if entries:
            return None

        # Move to next entry
        if self._position < len(entries):
            self._position += 1

            # If we moved past the end, return the draft
            if self._position == len(entries):
                draft = self._current_draft
                self._current_draft = ''
                return draft

            return entries[self._position]

        # Already at newest position
        return None

    def reset_position(self) -> None:
        """Reset history position to the end (no history item selected)."""

        try:
            entries = self._entries
        except AttributeError:
            self._position = 0
        else:
            self._position = len(entries)

        self._current_draft = ''
