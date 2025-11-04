import dataclasses as dc


##


@dc.dataclass(frozen=True)
class TextwrapOpts:
    # The maximum width of wrapped lines (unless break_long_words is false).
    width: int = 70  # noqa

    _: dc.KW_ONLY

    # String that will be prepended to the first line of wrapped output. Counts towards the line's width.
    initial_indent: str = ''

    # String that will be prepended to all lines save the first of wrapped output; also counts towards each line's
    # width.
    subsequent_indent: str = ''

    # Expand tabs in input text to spaces before further processing. Each tab will become 0 .. 'tabsize' spaces,
    # depending on its position in its line. If false, each tab is treated as a single character.
    expand_tabs: bool = True

    # Expand tabs in input text to 0 .. 'tabsize' spaces, unless 'expand_tabs' is false.
    tabsize: int = 8

    # Replace all whitespace characters in the input text by spaces after tab expansion. Note that if expand_tabs is
    # false and replace_whitespace is true, every tab will be converted to a single space!
    replace_whitespace: bool = True

    # Ensure that sentence-ending punctuation is always followed by two spaces. Off by default because the algorithm is
    # (unavoidably) imperfect.
    fix_sentence_endings: bool = False

    # Break words longer than 'width'.  If false, those words will not be broken, and some lines might be longer than
    # 'width'.
    break_long_words: bool = True

    # Allow breaking hyphenated words. If true, wrapping will occur preferably on whitespaces and right after hyphens
    # part of compound words.
    break_on_hyphens: bool = True

    # Drop leading and trailing whitespace from lines.
    drop_whitespace: bool = True

    # Truncate wrapped lines.
    max_lines: int | None = None

    # Append to the last line of truncated text.
    placeholder: str = ' [...]'
