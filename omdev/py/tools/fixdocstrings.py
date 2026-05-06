"""
Fix docstring formatting in Python source code.

Reads Python source from stdin and outputs to stdout with docstrings reformatted according to:
1. If docstring fits on a single 120-char line (including triple-quotes and indentation), make it single-line
2. Otherwise, put each triple-quote on its own line with no content sharing the line
3. Always ensure a blank line follows class/function docstrings (but NOT module docstrings)
"""
import ast
import os.path
import re
import sys
import typing as ta

from omlish import check
from omlish.logs import all as logs

from ..tokens import all as tks


log = logs.get_module_logger(globals())


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
            self._module_docstring_positions: set[tuple[int, int]] = set()
            return

        # Parse AST to identify docstring positions
        try:
            self._tree = ast.parse(src)
        except SyntaxError:
            # If we can't parse, don't try to fix anything
            self._tree = None
            self._docstring_positions = set()
            self._module_docstring_positions = set()
        else:
            self._docstring_positions = self._find_docstring_positions()

    def _find_docstring_positions(self) -> set[tuple[int, int]]:
        """Find all docstring positions (line, col_offset) in the AST."""

        if self._tree is None:
            return set()

        positions = set()
        module_positions = set()

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
                    pos = (expr_node.lineno, expr_node.col_offset)
                    positions.add(pos)
                    # Track module-level docstrings separately
                    if isinstance(node, ast.Module):
                        module_positions.add(pos)

        self._module_docstring_positions = module_positions
        return positions

    def _is_docstring(self, token: tks.Token) -> bool:
        """Check if a token is a docstring based on AST positions."""

        if token.name != 'STRING':
            return False

        # Check if this token's position matches a docstring position
        return (token.line, token.utf8_byte_offset) in self._docstring_positions

    def _is_module_docstring(self, token: tks.Token) -> bool:
        """Check if a token is a module-level docstring."""

        return (token.line, token.utf8_byte_offset) in self._module_docstring_positions

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

                # Ensure blank line after docstring (but not for module docstrings)
                if not self._is_module_docstring(token):
                    tokens = self._ensure_blank_line_after_docstring(tokens, i)

            i += 1

        return tks.tokens_to_src(tokens)


##


class _Runner:
    def __init__(
            self,
            *,
            overwrite: bool = False,
            dry_run: bool = False,
            num_workers: int | None = None,
            exclude_pats: ta.Sequence[re.Pattern] | None = None,
    ) -> None:
        super().__init__()

        self._overwrite = overwrite
        self._dry_run = dry_run
        self._num_workers = num_workers
        self._exclude_pats = exclude_pats

    #

    def _should_exclude_file(self, file_path: str) -> bool:
        if (xps := self._exclude_pats):
            for xp in xps:
                if xp.match(file_path):
                    return True

        return False

    def _find_file_paths(self, roots: ta.Iterable[str]) -> set[str]:
        roots = sorted({check.non_empty_str(s) for s in check.not_isinstance(roots, str)})

        file_paths: set[str] = set()

        for root in roots:
            if os.path.isfile(root):
                if not self._should_exclude_file(root):
                    file_paths.add(root)

            elif os.path.isdir(root):
                for dp, _dns, fns in os.walk(root):
                    for fn in fns:
                        if not fn.endswith('.py'):
                            continue

                        fp = os.path.join(dp, fn)

                        if not self._should_exclude_file(fp):
                            file_paths.add(fp)

            else:
                raise FileNotFoundError(root)

        return file_paths

    #

    @classmethod
    def _run_one(
            cls,
            file_path: str,
    ) -> tuple[str, str] | None:
        with open(file_path) as f:
            src = f.read()

        fixed_src = DocstringFixer(src).fix()

        if fixed_src == src:
            return None

        return (file_path, fixed_src)

    def run(
            self,
            roots: ta.Iterable[str],
    ) -> None:
        file_paths = self._find_file_paths(roots)

        #

        import concurrent.futures as cf

        from omlish.concurrent.executors import new_executor

        with new_executor(
            self._num_workers,
            cf.ProcessPoolExecutor,
        ) as exe:
            futs: list[cf.Future] = [
                exe.submit(self._run_one, fp)
                for fp in file_paths
            ]

            for fut in futs:
                if (res := fut.result()) is not None:
                    fp, fixed_src = res

                    if not self._overwrite:
                        sys.stdout.write('\n'.join([
                            '====',
                            fp,
                            '====',
                            fixed_src,
                            '',
                        ]))

                    elif self._dry_run:
                        log.info(lambda: f'Would fix {fp}')

                    else:
                        log.info(lambda: f'Fixing {fp}')
                        with open(fp, 'w') as f:
                            f.write(fixed_src)


##


def _main() -> None:
    """Read from stdin, fix docstrings, write to stdout."""

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('src', nargs='+')
    parser.add_argument('-W', '--overwrite', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('-j', '--workers', type=int)
    parser.add_argument('-x', '--exclude', action='append')

    args = parser.parse_args()

    if not args.src:
        raise Exception('src must be specified')

    logs.configure_standard_logging()

    if '-' in args.src:
        if list(args.src) != ['-']:
            raise Exception('if - in src it must be only src')

        src = sys.stdin.read()
        fixed_src = DocstringFixer(src).fix()
        sys.stdout.write(fixed_src)

        return

    _Runner(
        overwrite=bool(args.overwrite),
        dry_run=bool(args.dry_run),
        num_workers=args.workers,
        exclude_pats=[re.compile(xp) for xp in args.exclude] if args.exclude else None,
    ).run(args.src)


if __name__ == '__main__':
    _main()
