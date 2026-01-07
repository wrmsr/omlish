import abc
import typing as ta

from omlish import lang

from ...markdown.incparse import IncrementalMarkdownParser
from ...markdown.tokens import flatten_tokens as _flatten_tokens
from .console2 import console_render


with lang.auto_proxy_import(globals()):
    import markdown_it as md  # noqa
    import markdown_it.token  # noqa
    import rich.console
    import rich.live
    import rich.markdown
    import rich.text


##


def configure_markdown_parser(parser: ta.Optional['md.MarkdownIt'] = None) -> 'md.MarkdownIt':
    if parser is None:
        parser = md.MarkdownIt()

    return (
        parser
        .enable('strikethrough')
        .enable('table')
    )


def markdown_from_tokens(tokens: ta.Sequence['md.token.Token']) -> 'rich.markdown.Markdown':
    rmd = rich.markdown.Markdown('')
    rmd.parsed = tokens  # type: ignore[assignment]
    return rmd


def flatten_tokens_filter(token: 'md.token.Token') -> bool:
    return (
        token.type != 'fence' and
        token.tag != 'img'
    )


def flatten_tokens(tokens: ta.Iterable['md.token.Token']) -> ta.Iterable['md.token.Token']:
    return _flatten_tokens(tokens, filter=flatten_tokens_filter)


##


class MarkdownLiveStream(lang.ExitStacked, lang.Abstract):
    def __init__(
            self,
            *,
            parser: ta.Optional['md.MarkdownIt'] = None,
            console: ta.Optional['rich.console.Console'] = None,
    ) -> None:
        super().__init__()

        if console is None:
            console = rich.console.Console()
        self._console = console

        if parser is None:
            parser = configure_markdown_parser()
        self._parser = parser

        self._lines_printed_to_scrollback = 0

    _live: 'rich.live.Live'  # noqa

    def _enter_contexts(self) -> None:
        super()._enter_contexts()

        self._live = self._enter_context(rich.live.Live(
            rich.text.Text(''),
            console=self._console,
            refresh_per_second=10,
        ))

    def _console_render(self, obj: ta.Any) -> list[str]:
        return console_render(
            obj,
            force_terminal=True,
            width=self._console.width,
        ).splitlines()

    def _console_render_markdown(self, src: str) -> list[str]:
        return self._console_render(markdown_from_tokens(self._parser.parse(src)))

    @abc.abstractmethod
    def feed(self, s: str) -> None:
        raise NotImplementedError


class NaiveMarkdownLiveStream(MarkdownLiveStream):
    _accumulated = ''

    def feed(self, s: str) -> None:
        self._accumulated += s
        all_lines = self._console_render_markdown(self._accumulated)

        # Calculate how many lines fit in the live window
        available_height = self._console.height - 2

        # Determine which lines overflow and need to be printed to scrollback
        total_lines = len(all_lines)
        if total_lines > available_height:
            # Lines that should be in scrollback
            lines_for_scrollback = total_lines - available_height

            # Print any new lines that weren't already printed
            if lines_for_scrollback > self._lines_printed_to_scrollback:
                new_lines_to_print = all_lines[self._lines_printed_to_scrollback:lines_for_scrollback]
                for line in new_lines_to_print:
                    self._live.console.print(rich.text.Text.from_ansi(line))
                self._lines_printed_to_scrollback = lines_for_scrollback

            # Show only the bottom portion in the live window
            visible_lines = all_lines[-available_height:]

        else:
            visible_lines = all_lines

        # Update the live display
        self._live.update(rich.text.Text.from_ansi('\n'.join(visible_lines)))


class IncrementalMarkdownLiveStream(MarkdownLiveStream):
    # @omlish-llm-author "gemini-3-pro"

    def __init__(
            self,
            *,
            parser: ta.Optional['md.MarkdownIt'] = None,
            console: ta.Optional['rich.console.Console'] = None,
    ) -> None:
        super().__init__(
            parser=parser,
            console=console,
        )

        self._inc_parser = IncrementalMarkdownParser(parser=self._parser)

    def feed(self, s: str) -> None:
        ip_out = self._inc_parser.feed2(s)

        if ip_out.new_stable:
            # Render the stable lines
            stable_lines = self._console_render(markdown_from_tokens(ip_out.new_stable))

            # Overlap Detection
            already_printed_count = min(self._lines_printed_to_scrollback, len(stable_lines))

            if already_printed_count < len(stable_lines):
                new_stable_lines = stable_lines[already_printed_count:]
                # Ensure no_wrap=True is used here to match strict line counting
                self._live.console.print(rich.text.Text.from_ansi('\n'.join(new_stable_lines), no_wrap=True))

            # Adjust counter
            self._lines_printed_to_scrollback = max(0, self._lines_printed_to_scrollback - len(stable_lines))

        unstable_lines = self._console_render(markdown_from_tokens(ip_out.unstable))

        available_height = self._console.height - 2
        total_lines = len(unstable_lines)

        if total_lines > available_height:
            # We calculate lines allowed in scrollback, but we subtract 1. This ensures the very bottom line (often a
            # transient border) stays in the Live window and is not committed to history until more content pushes it
            # up.
            lines_for_scrollback = max(0, total_lines - available_height - 1)

            if lines_for_scrollback > self._lines_printed_to_scrollback:
                new_lines_to_print = unstable_lines[self._lines_printed_to_scrollback:lines_for_scrollback]

                # Ensure no_wrap=True is used here to prevent auto-wrap from creating "phantom" lines that desync our
                # line counts.
                self._live.console.print(rich.text.Text.from_ansi('\n'.join(new_lines_to_print), no_wrap=True))

                self._lines_printed_to_scrollback = lines_for_scrollback

            visible_lines = unstable_lines[-available_height:]

        else:
            visible_lines = unstable_lines

        self._live.update(rich.text.Text.from_ansi('\n'.join(visible_lines)))


class SteppedIncrementalMarkdownLiveStream(MarkdownLiveStream):
    # @omlish-llm-author "gemini-3-pro"

    def __init__(
            self,
            *,
            parser: ta.Optional['md.MarkdownIt'] = None,
            console: ta.Optional['rich.console.Console'] = None,
            scroll_step: int | None = None,
    ) -> None:
        super().__init__(
            parser=parser,
            console=console,
        )

        self._inc_parser = IncrementalMarkdownParser(parser=self._parser)
        self._scroll_step = scroll_step

    def feed(self, s: str) -> None:
        ip_out = self._inc_parser.feed2(s)

        ##
        # Handle stable content

        if ip_out.new_stable:
            stable_lines = self._console_render(markdown_from_tokens(ip_out.new_stable))

            # Overlap Detection: Determine how many lines of this now-stable block were already pushed to scrollback
            # while they were in the "unstable" phase.
            already_printed_count = min(self._lines_printed_to_scrollback, len(stable_lines))

            if already_printed_count < len(stable_lines):
                new_stable_lines = stable_lines[already_printed_count:]
                # Force no_wrap=True to ensure 1:1 line counting
                self._live.console.print(rich.text.Text.from_ansi('\n'.join(new_stable_lines), no_wrap=True))

            # Adjust the global scrollback counter. We effectively shift the "start" of the unstable window down by the
            # size of the stable block.
            self._lines_printed_to_scrollback = max(0, self._lines_printed_to_scrollback - len(stable_lines))

        ##
        # Handle unstable content

        unstable_lines = self._console_render(markdown_from_tokens(ip_out.unstable))
        total_lines = len(unstable_lines)
        available_height = self._console.height - 2

        # Calculate the absolute minimum lines that MUST be in scrollback to fit the current content. We subtract 1 to
        # hold back the bottom-most line (e.g., table borders) from history until it is pushed up by further content.
        min_needed_scrollback = max(0, total_lines - available_height - 1)

        if min_needed_scrollback > self._lines_printed_to_scrollback:
            # We need to scroll. Calculate how much.
            diff = min_needed_scrollback - self._lines_printed_to_scrollback

            # Use the step size if configured, otherwise just satisfy the immediate difference. If the difference is
            # larger than the step (e.g., big paste), we jump the full difference.
            step = self._scroll_step if self._scroll_step is not None else 1
            jump_size = max(diff, step)

            # Calculate the new target scrollback index. We must clamp this to 'total_lines - 1' to ensure we never push
            # the strictly held-back last line into history.
            max_pushable_index = max(0, total_lines - 1)
            target_scrollback = min(self._lines_printed_to_scrollback + jump_size, max_pushable_index)

            if target_scrollback > self._lines_printed_to_scrollback:
                new_lines_to_print = unstable_lines[self._lines_printed_to_scrollback:target_scrollback]
                self._live.console.print(rich.text.Text.from_ansi('\n'.join(new_lines_to_print), no_wrap=True))
                self._lines_printed_to_scrollback = target_scrollback

        # Update the live display. We slice from '_lines_printed_to_scrollback' to the end. If we just performed a large
        # 'jump', this will naturally result in fewer lines than 'available_height', creating the desired visual "void"
        # at the bottom.
        visible_lines = unstable_lines[self._lines_printed_to_scrollback:]
        self._live.update(rich.text.Text.from_ansi('\n'.join(visible_lines)))


##


class ClaudeIncrementalMarkdownLiveStream(MarkdownLiveStream):
    # @omlish-llm-author "claude-opus-4-5"

    def __init__(
            self,
            *,
            parser: ta.Optional['md.MarkdownIt'] = None,
            console: ta.Optional['rich.console.Console'] = None,
    ) -> None:
        super().__init__(
            parser=parser,
            console=console,
        )

        from ...markdown.incparse import ClaudeIncrementalMarkdownParser  # noqa
        self._inc_parser = ClaudeIncrementalMarkdownParser(parser=self._parser)
        self._last_unstable_line_count = 0

    def _enter_contexts(self) -> None:
        super()._enter_contexts()

        # Override to configure Live with explicit vertical overflow handling
        self._live = self._enter_context(rich.live.Live(
            rich.text.Text(''),
            console=self._console,
            refresh_per_second=10,
            vertical_overflow='crop',
        ))

    def feed(self, s: str) -> None:
        ip_out = self._inc_parser.feed2(s)

        if ip_out.new_stable:
            # Stop live display to commit stable content cleanly
            self._live.stop()

            # Render and print stable content to true scrollback
            stable_lines = self._console_render(markdown_from_tokens(ip_out.new_stable))
            for line in stable_lines:
                self._console.print(rich.text.Text.from_ansi(line), highlight=False)

            # Reset tracking state since we're starting fresh with new unstable content
            self._last_unstable_line_count = 0
            self._lines_printed_to_scrollback = 0

            # Restart live display
            self._live.start()

        # Render current unstable content
        unstable_lines = self._console_render(markdown_from_tokens(ip_out.unstable))
        current_line_count = len(unstable_lines)

        # Calculate available display height
        available_height = self._console.height - 2

        # Handle content that exceeds available height. Key insight: never commit unstable content to scrollback since
        # it may change.
        if current_line_count > available_height:
            # Only show the bottom portion that fits
            visible_lines = unstable_lines[-available_height:]
        else:
            visible_lines = unstable_lines

        # Handle shrinking content: if we had more lines before and now have fewer, we need to ensure the live region is
        # properly cleared.
        if current_line_count < self._last_unstable_line_count:
            # Pad with empty lines to prevent artifacts from previous longer content. This ensures the live region fully
            # overwrites its previous state.
            lines_to_clear = min(
                self._last_unstable_line_count - current_line_count,
                available_height - len(visible_lines),
            )
            if lines_to_clear > 0:
                visible_lines = visible_lines + [''] * lines_to_clear

        self._last_unstable_line_count = current_line_count

        # Update the live display
        display_text = '\n'.join(visible_lines)
        self._live.update(rich.text.Text.from_ansi(display_text))


class GptIncrementalMarkdownLiveStream(MarkdownLiveStream):
    # @omlish-llm-author "gpt-5.2"

    def __init__(
            self,
            *,
            parser: ta.Optional['md.MarkdownIt'] = None,
            console: ta.Optional['rich.console.Console'] = None,
    ) -> None:
        super().__init__(
            parser=parser,
            console=console,
        )

        from ...markdown.incparse import GptIncrementalMarkdownParser  # noqa
        self._inc_parser = GptIncrementalMarkdownParser(parser=self._parser)

    def feed(self, s: str) -> None:
        ip_out = self._inc_parser.feed2(s)

        # Permanently commit only content the parser marked as stable. This avoids *all* "scrollback delta accounting"
        # and the associated duplication/gap bugs when the rendered tail shrinks / reflows / reinterprets (streaming
        # markdown is non-monotonic).
        if ip_out.new_stable:
            # Print stable renderables directly through Rich (avoid ANSI round-tripping / splitlines). Use end="" so we
            # don't inject extra blank lines beyond what the markdown renderable produces.
            self._live.console.print(markdown_from_tokens(ip_out.new_stable), end='')

        # Show the remaining (unstable) tail in the live region. We intentionally do *not* try to "spill overflow of
        # unstable to scrollback", since those lines are not provably stable and may retroactively change; printing them
        # would violate correctness.
        self._live.update(markdown_from_tokens(ip_out.unstable))
