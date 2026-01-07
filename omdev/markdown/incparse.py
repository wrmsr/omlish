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


##


class ClaudeIncrementalMarkdownParser:
    # @omlish-llm-author "claude-opus-4-5"

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
        self._num_stable_lines = 0

    class FeedOutput(ta.NamedTuple):
        stable: ta.Sequence['md.token.Token']
        new_stable: ta.Sequence['md.token.Token']
        unstable: ta.Sequence['md.token.Token']

    def feed2(self, chunk: str) -> FeedOutput:
        self._buffer += chunk

        new_tokens = self._parser.parse(self._buffer)

        adjusted_tokens = self._adjust_token_line_numbers(new_tokens, self._num_stable_lines)

        stable_count = self._find_stable_token_count(adjusted_tokens, self._buffer)

        newly_stable: ta.Sequence[md.token.Token]
        if stable_count > 0:
            newly_stable = adjusted_tokens[:stable_count]

            max_line = 0
            for token in newly_stable:
                if token.map:
                    max_line = max(max_line, token.map[1])

            if max_line > self._num_stable_lines:
                lines_to_remove = max_line - self._num_stable_lines
                lines = self._buffer.split('\n')
                self._buffer = '\n'.join(lines[lines_to_remove:])

                self._stable_tokens.extend(newly_stable)
                self._num_stable_lines = max_line

        else:
            newly_stable = ()

        return ClaudeIncrementalMarkdownParser.FeedOutput(
            stable=self._stable_tokens,
            new_stable=newly_stable,
            unstable=adjusted_tokens[stable_count:],
        )

    def feed(self, chunk: str) -> list['md.token.Token']:
        out = self.feed2(chunk)
        return [*out.stable, *out.unstable]

    def _find_stable_token_count(
            self,
            tokens: list['md.token.Token'],
            buffer: str,
    ) -> int:
        if not tokens:
            return 0

        parent_indices = []
        for i, token in enumerate(tokens):
            if token.nesting in (1, 0) and token.level == 0:
                parent_indices.append(i)

        if len(parent_indices) < 2:
            return 0

        # Find the last parent index that is fully terminated. We need at least one more parent after it to consider it
        # stable.
        buffer_lines = buffer.split('\n')

        for candidate_idx in range(len(parent_indices) - 2, -1, -1):
            token_list_idx = parent_indices[candidate_idx]

            # Find the end of this block (either the token itself or its closing tag)
            block_end_idx = token_list_idx
            if tokens[token_list_idx].nesting == 1:
                # Opening tag - find corresponding close
                depth = 1
                for j in range(token_list_idx + 1, len(tokens)):
                    if tokens[j].level == 0:
                        if tokens[j].nesting == 1:
                            depth += 1
                        elif tokens[j].nesting == -1:
                            depth -= 1
                            if depth == 0:
                                block_end_idx = j
                                break

            # Get the line range for this block
            end_line = 0
            for t in tokens[:block_end_idx + 1]:
                if t.map:
                    end_line = max(end_line, t.map[1])

            # Check if followed by blank line or another clear block boundary end_line is exclusive (points to line
            # after the block). Relative to current buffer (not absolute).
            relative_end = end_line - self._num_stable_lines

            if relative_end < 0:
                continue

            if relative_end < len(buffer_lines):
                # Check for blank line or clear termination
                if relative_end < len(buffer_lines):
                    following_content = '\n'.join(buffer_lines[relative_end:])
                    # Stable if: blank line follows, or significant content after
                    if (
                        following_content.startswith('\n') or
                        (following_content.strip() and len(following_content.strip()) > 0)
                    ):
                        # Check the next parent token exists and has been parsed
                        if candidate_idx + 1 < len(parent_indices):
                            next_parent_idx = parent_indices[candidate_idx + 1]
                            next_token = tokens[next_parent_idx]
                            # The next block should start after our block ends
                            if next_token.map and next_token.map[0] >= end_line - self._num_stable_lines:
                                return parent_indices[candidate_idx + 1]

        return 0

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


class GptIncrementalMarkdownParser:
    # @omlish-llm-author "gpt-5.2"

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
        self._num_stable_lines = 0  # Number of *source* lines removed from the buffer and committed.

    class FeedOutput(ta.NamedTuple):
        stable: ta.Sequence['md.token.Token']
        new_stable: ta.Sequence['md.token.Token']
        unstable: ta.Sequence['md.token.Token']

    def feed2(self, chunk: str) -> FeedOutput:
        self._buffer += chunk

        # Parse the current buffer (line numbers are relative to the buffer's start).
        new_tokens = self._parser.parse(self._buffer)

        # Adjust ALL tokens to account for stable lines from previous parses.
        adjusted_tokens = self._adjust_token_line_numbers(new_tokens, self._num_stable_lines)

        # Decide how many *source lines* from the front of the buffer are safe to commit permanently.
        stable_line_cut = self._find_stable_line_cut(self._buffer)
        stable_abs_line = self._num_stable_lines + stable_line_cut

        newly_stable: ta.Sequence[md.token.Token]
        if stable_line_cut > 0:
            # Commit tokens that are wholly before the stable cut.
            newly_stable_list: list[md.token.Token] = []
            remaining_list: list[md.token.Token] = []

            for t in adjusted_tokens:
                # Tokens without maps are treated conservatively as unstable unless we've already committed
                # all remaining source.
                if not t.map:
                    remaining_list.append(t)
                    continue

                # t.map is [start_line, end_line) in absolute source lines (after adjustment).
                if t.map[1] <= stable_abs_line:
                    newly_stable_list.append(t)
                else:
                    remaining_list.append(t)

            newly_stable = newly_stable_list

            # Remove committed source lines from the buffer.
            lines = self._buffer.split('\n')
            self._buffer = '\n'.join(lines[stable_line_cut:])

            # Persist committed state.
            self._stable_tokens.extend(newly_stable)
            self._num_stable_lines = stable_abs_line

            unstable = remaining_list

        else:
            newly_stable = ()
            unstable = adjusted_tokens

        return GptIncrementalMarkdownParser.FeedOutput(
            stable=self._stable_tokens,
            new_stable=newly_stable,
            unstable=unstable,
        )

    def feed(self, chunk: str) -> list['md.token.Token']:
        out = self.feed2(chunk)
        return [*out.stable, *out.unstable]

    ##
    # Stability boundary

    def _find_stable_line_cut(self, buf: str) -> int:
        """
        Return a conservative number of *source lines* from the buffer start that can be treated as permanently stable
        (i.e. future suffixes of the markdown source will not change their parse/render).

        This intentionally errs on the side of keeping more in the unstable tail.
        """

        if not buf:
            return 0

        lines = buf.split('\n')

        # Track whether we're inside a fenced code block. This is the biggest retroactive-parse hazard.
        in_fence = False
        fence_marker: str | None = None

        # Track whether we're inside a blockquote region (heuristic).
        in_quote = False

        # Track whether we're inside a list region (heuristic).
        in_list = False

        # We only commit up to a "hard" boundary: a blank line that is outside fence/quote/list context. Additionally,
        # we require that the boundary line itself is blank (so setext headings can't reach back).
        last_safe_cut: int = 0

        def is_blank(s: str) -> bool:
            return not s.strip()

        def is_fence_line(s: str) -> str | None:
            st = s.lstrip()
            if st.startswith('```'):
                return '```'
            if st.startswith('~~~'):
                return '~~~'
            return None

        def is_quote_line(s: str) -> bool:
            return s.lstrip().startswith('>')

        def is_list_line(s: str) -> bool:
            st = s.lstrip()
            if not st:
                return False
            # Very conservative list marker detection.
            if st[0] in ('-', '*', '+') and len(st) > 1 and st[1].isspace():
                return True
            # "1. " / "1) "
            i = 0
            while i < len(st) and st[i].isdigit():
                i += 1
            if i > 0 and i < len(st) and st[i] in ('.', ')'):
                j = i + 1
                return j < len(st) and st[j].isspace()
            return False

        def is_indented_code(s: str) -> bool:
            # Indented code blocks (4 spaces / 1 tab) can be sensitive to context; treat as "unstable context" for
            # committing boundaries.
            return s.startswith(('    ', '\t'))

        for i, line in enumerate(lines):
            # Fence tracking.
            fm = is_fence_line(line)
            if fm is not None:
                if not in_fence:
                    in_fence = True
                    fence_marker = fm
                else:
                    # Only close on the matching marker (conservative).
                    if fence_marker == fm:
                        in_fence = False
                        fence_marker = None

            # Quote tracking (heuristic: treat contiguous quote lines as quote context).
            if is_quote_line(line):
                in_quote = True
            elif is_blank(line):
                # A blank line is a potential place to end a quote, but only if we are not in a fence.
                if not in_fence:
                    in_quote = False

            # List tracking (heuristic: any list marker enters list context; blank lines end list context only if the
            # following non-blank line is not indented / not list / not quote).
            if is_list_line(line):
                in_list = True
            if is_blank(line) and not in_fence:
                # Peek ahead to see if the list plausibly continues.
                j = i + 1
                while j < len(lines) and is_blank(lines[j]):
                    j += 1
                if j >= len(lines):
                    # End of buffer: keep tail unstable.
                    pass
                else:
                    nxt = lines[j]
                    if (
                            not is_indented_code(nxt) and
                            not is_list_line(nxt) and
                            not is_quote_line(nxt)
                    ):
                        in_list = False

            # Commit boundary selection.
            if is_blank(line) and not in_fence and not in_quote and not in_list:
                # Safe to commit through this blank line (i.e. cut after it).
                last_safe_cut = i + 1

        # Never cut the entire buffer; leave at least one line in the tail so incremental feeds keep working.
        if last_safe_cut >= len(lines):
            return 0

        return last_safe_cut

    def _adjust_token_line_numbers(
            self,
            tokens: list['md.token.Token'],
            line_offset: int,
    ) -> list['md.token.Token']:
        adjusted: list[md.token.Token] = []

        def adj_tok(t: 'md.token.Token') -> 'md.token.Token':
            nt = t
            if nt.map:
                nt = dc.replace(
                    nt,
                    map=[nt.map[0] + line_offset, nt.map[1] + line_offset],
                )

            # Adjust children maps too (markdown-it uses children for inline tokens).
            ch = getattr(nt, 'children', None)
            if ch:
                new_children: list[md.token.Token] = []
                changed = False
                for c in ch:
                    nc = c
                    if nc.map:
                        nc = dc.replace(
                            nc,
                            map=[nc.map[0] + line_offset, nc.map[1] + line_offset],
                        )
                        changed = True
                    new_children.append(nc)
                if changed:
                    nt = dc.replace(nt, children=new_children)

            return nt

        for token in tokens:
            adjusted.append(adj_tok(token))

        return adjusted
