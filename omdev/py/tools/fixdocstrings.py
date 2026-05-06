"""
Fix docstring formatting in Python source code.

Reads Python source from stdin and outputs to stdout with docstrings reformatted according to:
1. If docstring fits on a single 120-char line (including triple-quotes and indentation), make it single-line
2. Otherwise, put each triple-quote on its own line with no content sharing the line
3. Always ensure a blank line follows every docstring

TODO:
 - actually don't add a blank line after module docstring, but other rules still apply
 - optional overwrite in-place
   - only write out if different
 - accept dir args, recursive
 - nargs='*' of ignore path regex pats, can like `--ignore '.*/tests/.*'`
 - multiprocessing executor, `--j, --workers', if None/0 (default) then run in process serially

"""
import ast
import sys

from ..tokens import all as tks


##


class DocstringFixer:
    """Fixes docstring formatting while preserving all other whitespace and comments."""

    def __init__(self, src: str) -> None:
        super().__init__()

        self._src = src

        self._tree: ast.Module | None

        # Try to tokenize and parse - if either fails, we can't fix anything
        try:
            self._tokens = list(tks.src_to_tokens(src))
        except Exception:  # noqa
            # If tokenization fails, we can't do anything
            self._tokens = []
            self._tree = None
            self._docstring_positions: set[tuple[int, int]] = set()
            return

        # Parse AST to identify docstring positions
        try:
            self._tree = ast.parse(src)
        except SyntaxError:
            # If we can't parse, don't try to fix anything
            self._tree = None
            self._docstring_positions = set()
        else:
            self._docstring_positions = self._find_docstring_positions()

    def _find_docstring_positions(self) -> set[tuple[int, int]]:
        """Find all docstring positions (line, col_offset) in the AST."""

        if self._tree is None:
            return set()

        positions = set()

        for node in ast.walk(self._tree):
            # Only these node types can have docstrings
            if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            docstring = ast.get_docstring(node, clean=False)
            if docstring is None:
                continue

            # Get the first statement which should be the Expr node containing the docstring
            if node.body and isinstance(node.body[0], ast.Expr):
                expr_node = node.body[0]
                if isinstance(expr_node.value, ast.Constant) and isinstance(expr_node.value.value, str):
                    # Record position (line, col_offset)
                    positions.add((expr_node.lineno, expr_node.col_offset))

        return positions

    def _is_docstring(self, token: tks.Token) -> bool:
        """Check if a token is a docstring based on AST positions."""

        if token.name != 'STRING':
            return False

        # Check if this token's position matches a docstring position
        return (token.line, token.utf8_byte_offset) in self._docstring_positions

    def _get_string_content(self, token_src: str) -> tuple[str, str, str]:
        """
        Parse a string token into (prefix, quotes, content).

        Returns:
            (prefix, quotes, content) where:
            - prefix is the string prefix (r, u, f, b, etc., possibly empty)
            - quotes is the quote style (', ", ''', \"\"\")
            - content is the actual string content
        """

        src = token_src

        # Extract prefix
        prefix_chars = []
        i = 0
        while i < len(src) and src[i] in 'rRuUfFbB':
            prefix_chars.append(src[i])
            i += 1
        prefix = ''.join(prefix_chars)

        # Extract quotes
        remainder = src[i:]
        if remainder.startswith(('"""', "'''")):
            quotes = remainder[:3]
            content = remainder[3:-3]
        elif remainder.startswith(('"', "'")):
            quotes = remainder[0]
            content = remainder[1:-1]
        else:
            raise ValueError(f'Invalid string token: {token_src}')

        return prefix, quotes, content

    def _calculate_display_width(self, s: str) -> int:
        """Calculate the display width of a string (treating tabs as single characters for simplicity)."""

        # For docstring width calculation, we need to account for indentation
        # Tabs are typically 8 spaces, but in code they align to tab stops
        # For simplicity, we'll count each tab as 4 spaces
        return len(s.replace('\t', '    '))

    def _fix_docstring(self, token: tks.Token, indent: str) -> list[tks.Token]:
        """
        Fix a docstring token's formatting.

        Returns a list of tokens to replace the original docstring token.
        """

        prefix, quotes, content = self._get_string_content(token.src)

        # Only handle triple-quoted strings as docstrings
        if len(quotes) != 3:
            return [token]

        # Strip leading/trailing newlines (and any surrounding whitespace on those lines)
        # from content that come from multi-line format - these are formatting artifacts
        lines = content.split('\n')

        # Remove empty leading lines
        while lines and not lines[0].strip():
            lines.pop(0)

        # Remove empty trailing lines
        while lines and not lines[-1].strip():
            lines.pop()

        stripped_content = '\n'.join(lines)

        # Check if the *stripped* content has explicit newlines (i.e., it's meant to be multi-line)
        has_explicit_newlines = '\n' in stripped_content

        # Calculate if single-line format fits in 120 chars
        single_line = f'{prefix}{quotes}{stripped_content}{quotes}'
        single_line_with_indent = f'{indent}{single_line}'

        if not has_explicit_newlines and self._calculate_display_width(single_line_with_indent) <= 120:
            # Use single-line format
            new_src = single_line
        else:
            # Use multi-line format with triple-quotes on separate lines
            # Keep the original content structure (including any indentation within)
            new_src = f'{prefix}{quotes}\n{stripped_content}\n{quotes}'

        return [tks.Token(name='STRING', src=new_src, line=token.line, utf8_byte_offset=token.utf8_byte_offset)]

    def _ensure_blank_line_after_docstring(
            self,
            tokens: list[tks.Token],
            docstring_idx: int,
    ) -> list[tks.Token]:
        """
        Ensure there's a blank line after a docstring.

        Returns modified token list.
        """

        # Find the next NEWLINE token after the docstring
        idx = docstring_idx + 1
        while idx < len(tokens) and tokens[idx].name == 'UNIMPORTANT_WS':
            idx += 1

        if idx >= len(tokens) or tokens[idx].name != 'NEWLINE':
            # Something's wrong, don't modify
            return tokens

        # Check what comes after the NEWLINE
        idx += 1

        # Count consecutive NL/NEWLINE tokens (blank lines)
        newline_count = 0
        first_newline_idx = idx

        while idx < len(tokens):
            if tokens[idx].name in ('NL', 'NEWLINE'):
                newline_count += 1
                idx += 1
            elif tokens[idx].name == 'UNIMPORTANT_WS':
                # Skip whitespace between newlines
                idx += 1
            else:
                break

        # If we don't have at least one blank line (2 newlines total including the one right after docstring),
        # we need to add a NL token
        if newline_count == 0:
            # Insert a NL token to create a blank line
            # We need to insert it right after the first NEWLINE following the docstring
            new_tokens = [*tokens[:first_newline_idx], tks.Token('NL', '\n'), *tokens[first_newline_idx:]]
            return new_tokens

        return tokens

    def fix(self) -> str:
        """Fix all docstrings in the source and return the modified source."""

        if self._tree is None:
            # Can't parse, return original
            return self._src

        tokens = self._tokens[:]

        # Identify and fix docstrings
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if self._is_docstring(token):
                # Get the indentation before this token
                # The indentation could be an INDENT token or UNIMPORTANT_WS before the docstring on the same line
                indent = ''
                j = i - 1

                # Look backwards for INDENT or UNIMPORTANT_WS
                while j >= 0:
                    if tokens[j].name == 'INDENT':
                        indent = tokens[j].src
                        break
                    elif tokens[j].name == 'UNIMPORTANT_WS' and '\n' not in tokens[j].src:
                        indent = tokens[j].src
                        break
                    elif tokens[j].name in ('NEWLINE', 'NL'):
                        # Reached the previous line without finding indent
                        break
                    j -= 1

                # Fix the docstring
                fixed_tokens = self._fix_docstring(token, indent)
                tokens = tokens[:i] + fixed_tokens + tokens[i + 1:]

                # Ensure blank line after docstring
                tokens = self._ensure_blank_line_after_docstring(tokens, i)

            i += 1

        return tks.tokens_to_src(tokens)


def _main() -> None:
    """Read from stdin, fix docstrings, write to stdout."""

    src = sys.stdin.read()

    fixer = DocstringFixer(src)
    fixed_src = fixer.fix()

    sys.stdout.write(fixed_src)


if __name__ == '__main__':
    _main()
