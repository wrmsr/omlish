import dataclasses as dc
import typing as ta

from omlish import lang


with lang.auto_proxy_import(globals()):
    import markdown_it as md
    import markdown_it.token  # noqa


##


class IncrementalMarkdownParser:
    def __init__(
            self,
            *,
            parser: ta.Optional['md.MarkdownIt'] = None,
    ) -> None:
        super().__init__()

        if parser is None:
            parser = md.MarkdownIt()
        self._parser = parser

        self._stable_tokens: list[md.token.Token] = []
        self._buffer = ''
        self._num_stable_lines = 0  # Number of lines in stable tokens

    class FeedOutput(ta.NamedTuple):
        stable: ta.Sequence['md.token.Token']
        new_stable: ta.Sequence['md.token.Token']
        unstable: ta.Sequence['md.token.Token']

    def feed2(self, chunk: str) -> FeedOutput:
        self._buffer += chunk

        # Parse the current buffer
        new_tokens = self._parser.parse(self._buffer)

        # Adjust ALL tokens to account for stable lines from previous parses (new_tokens have line numbers relative to
        # current buffer)
        adjusted_tokens = self._adjust_token_line_numbers(new_tokens, self._num_stable_lines)

        # Find stable tokens (all but the last parent and its children)
        stable_count = self._find_stable_token_count(adjusted_tokens)

        newly_stable: ta.Sequence[md.token.Token]
        if stable_count > 0:
            # Extract newly stable tokens (already have adjusted line numbers)
            newly_stable = adjusted_tokens[:stable_count]

            # Calculate how many lines these stable tokens cover
            max_line = 0
            for token in newly_stable:
                if token.map:
                    max_line = max(max_line, token.map[1])

            # Update buffer to only contain unstable content
            if max_line > self._num_stable_lines:
                # max_line is absolute, num_stable_lines is the current buffer offset
                lines_to_remove = max_line - self._num_stable_lines
                lines = self._buffer.split('\n')
                self._buffer = '\n'.join(lines[lines_to_remove:])

                # Store newly stable tokens (with adjusted line numbers)
                self._stable_tokens.extend(newly_stable)
                self._num_stable_lines = max_line

        else:
            newly_stable = ()

        return IncrementalMarkdownParser.FeedOutput(
            stable=self._stable_tokens,
            new_stable=newly_stable,
            unstable=adjusted_tokens[stable_count:],
        )

    def feed(self, chunk: str) -> list['md.token.Token']:
        out = self.feed2(chunk)
        return [*out.stable, *out.unstable]

    def _find_stable_token_count(self, tokens: list['md.token.Token']) -> int:
        if not tokens:
            return 0

        # Find indices of all parent-level tokens (nesting = 0)
        parent_indices = []
        for i, token in enumerate(tokens):
            if token.nesting in (1, 0) and token.level == 0:
                parent_indices.append(i)

        if len(parent_indices) < 2:
            # Need at least 2 parent tokens to have stable content
            return 0

        # The last parent and everything after it is unstable. Everything before the second-to-last parent is stable.
        return parent_indices[-2]

    def _adjust_token_line_numbers(
            self,
            tokens: list['md.token.Token'],
            line_offset: int,
    ) -> list['md.token.Token']:
        adjusted = []
        for token in tokens:
            if token.map:
                token = dc.replace(
                    token,
                    map=[token.map[0] + line_offset, token.map[1] + line_offset],
                )

            adjusted.append(token)

        return adjusted
