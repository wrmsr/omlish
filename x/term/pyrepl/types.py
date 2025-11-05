import typing as ta


KeySpec: ta.TypeAlias = str  # like r"\C-c"

CommandName: ta.TypeAlias = str  # like "interrupt"

Completer: ta.TypeAlias = ta.Callable[[str, int], str | None]

CharBuffer: ta.TypeAlias = list[str]
CharWidths: ta.TypeAlias = list[int]
