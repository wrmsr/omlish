import abc
import json
import os
import typing as ta

from omlish import lang


##


class InputHistoryStorage(lang.Abstract):
    @abc.abstractmethod
    def load(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, entries: ta.Sequence[str]) -> None:
        raise NotImplementedError


class InMemoryInputHistoryStorage(InputHistoryStorage):
    def __init__(self) -> None:
        super().__init__()

        self._entries: list[str] = []

    def load(self) -> list[str]:
        return list(self._entries)

    def save(self, entries: ta.Sequence[str]) -> None:
        self._entries = list(entries)


class FileInputHistoryStorage(InputHistoryStorage):
    def __init__(self, *, path: str) -> None:
        super().__init__()

        self._path = path

    def load(self) -> list[str]:
        if not os.path.exists(self._path):
            return []

        try:
            with open(self._path) as f:
                data = json.load(f)
                if isinstance(data, list) and all(isinstance(e, str) for e in data):
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, entries: ta.Sequence[str]) -> None:
        try:
            dir_path = os.path.dirname(self._path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(self._path, 'w') as f:
                json.dump(list(entries), f, indent=2)
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

        self._entries: list[str] = self._storage.load()
        self._position: int = len(self._entries)
        self._current_draft: str = ''

    def add(self, text: str) -> None:
        """Add a new history entry and reset position."""

        if not text.strip():
            return

        # Don't add duplicate consecutive entries
        if self._entries and self._entries[-1] == text:
            self.reset_position()
            return

        self._entries.append(text)

        # Trim to max size
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        self._storage.save(self._entries)
        self.reset_position()

    def get_previous(self, text: str | None = None) -> str | None:
        """
        Navigate to previous (older) history entry.

        Args:
            text: Current text in the input field (saved as draft when at end of history)

        Returns:
            The previous history entry, or None if at the beginning
        """

        if not self._entries:
            return None

        # Save current draft if we're at the end
        if self._position == len(self._entries) and text is not None:
            self._current_draft = text

        # Move to previous entry
        if self._position > 0:
            self._position -= 1
            return self._entries[self._position]

        # Already at oldest entry
        return self._entries[0] if self._entries else None

    def get_next(self, text: str | None = None) -> str | None:
        """
        Navigate to next (newer) history entry.

        Args:
            text: Current text in the input field (unused for now)

        Returns:
            The next history entry, the saved draft if moving past the end, or None
        """

        if not self._entries:
            return None

        # Move to next entry
        if self._position < len(self._entries):
            self._position += 1

            # If we moved past the end, return the draft
            if self._position == len(self._entries):
                draft = self._current_draft
                self._current_draft = ''
                return draft

            return self._entries[self._position]

        # Already at newest position
        return None

    def reset_position(self) -> None:
        """Reset history position to the end (no history item selected)."""

        self._position = len(self._entries)
        self._current_draft = ''
