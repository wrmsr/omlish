import typing as ta

from omlish import lang

from ...markdown.incparse import IncrementalMarkdownParser
from .console2 import console_render


with lang.auto_proxy_import(globals()):
    import markdown_it as md  # noqa
    import markdown_it.token  # noqa
    import rich.console
    import rich.live
    import rich.markdown
    import rich.text


##


def configure_markdown_parser(parser: 'md.MarkdownIt') -> 'md.MarkdownIt':
    return (
        parser
        .enable('strikethrough')
        .enable('table')
    )


def markdown_from_tokens(tokens: ta.Sequence['md.token.Token']) -> 'rich.markdown.Markdown':
    rmd = rich.markdown.Markdown('')
    rmd.parsed = tokens
    return rmd


##


class IncrementalMarkdownRenderer(lang.ExitStacked):
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

        self._inc_parser = IncrementalMarkdownParser(parser=parser)

        self._accumulated = ''
        self._lines_printed_to_scrollback = 0

    _live: 'rich.live.Live'  # noqa

    def _enter_contexts(self) -> None:
        super()._enter_contexts()
        self._live = self._enter_context(rich.live.Live(
            rich.text.Text(''),
            console=self._console,
            refresh_per_second=10,
        ))

    def _get_rendered_lines(self, obj: ta.Any) -> list[str]:
        return console_render(
            obj,
            force_terminal=True,
            width=self._console.width,
        ).splitlines()

    def feed(self, s: str) -> None:
        self._accumulated += s

        ip_out = self._inc_parser.feed2(s)

        if ip_out.new_stable:
            rmd = rich.markdown.Markdown('')
            rmd.parsed = ip_out.new_stable
            stable_lines = self._get_rendered_lines(rmd)

        all_lines = self._get_rendered_lines(rich.markdown.Markdown(self._accumulated))

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
