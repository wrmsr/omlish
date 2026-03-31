import rlcompleter

from omdev.tui import textual as tx


##


COMPLETER_DELIMS = frozenset(" \t\n`~!@#$%^&*()-=+[{]}\\|;:'\",<>/?")


def extract_stem(text: str, cursor_col: int) -> str:
    """Extract completion stem by walking back from cursor to a delimiter."""

    p = cursor_col - 1
    while p >= 0 and text[p] not in COMPLETER_DELIMS:
        p -= 1
    return text[p + 1: cursor_col]


def common_prefix(wordlist: list[str], start: int = 0) -> str:
    """Find the longest common prefix of all words from index `start`."""

    if not wordlist:
        return ''
    d: dict[str, int] = {}
    i = start
    try:
        while True:
            for word in wordlist:
                d[word[i]] = 1
            if len(d) > 1:
                return wordlist[0][start:i]
            i += 1
            d = {}
    except IndexError:
        return wordlist[0][start:i]


class CompletionProvider:
    """Provides Python completions using rlcompleter against a namespace."""

    def __init__(self, namespace: dict) -> None:
        self._completer = rlcompleter.Completer(namespace)

    def get_completions(self, stem: str) -> list[str]:
        if not stem:
            return []
        results = []
        state = 0
        while True:
            try:
                match = self._completer.complete(stem, state)
            except Exception:  # noqa  # FIXME
                break
            if match is None:
                break
            results.append(match)
            state += 1
        results.sort()
        return results


class CompletionPopup(tx.OptionList):
    """Display-only completion popup. Never receives focus."""

    can_focus = False

    DEFAULT_CSS = """
        CompletionPopup {
            display: none;
            height: auto;
            max-height: 8;
            border: solid $accent;
            background: $boost;
        }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._stem = ''
        self._completions: list[str] = []

    def show(self, completions: list[str], stem: str) -> None:
        self._stem = stem
        self._completions = completions
        self.clear_options()
        for c in completions:
            self.add_option(c)
        if completions:
            self.highlighted = 0
        self.display = True

    def dismiss(self) -> None:
        self.display = False

    def filter(self, new_stem: str) -> bool:
        """Re-filter with new stem. Returns False if no matches remain."""

        self._stem = new_stem
        filtered = [c for c in self._completions if c.startswith(new_stem)]
        self.clear_options()
        for c in filtered:
            self.add_option(c)
        if filtered:
            self.highlighted = 0
            return True
        self.dismiss()
        return False

    def get_selected(self) -> str | None:
        if self.highlighted is not None and self.option_count > 0:
            return str(self.get_option_at_index(self.highlighted).prompt)
        return None
