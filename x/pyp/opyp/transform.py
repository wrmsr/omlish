# ruff: noqa: N802
import ast
import importlib
import inspect
import textwrap
import traceback
import typing as ta

from .asts import dfs_walk
from .config import PypConfig
from .errors import PypError
from .names import MAGIC_VARS
from .names import NameFinder
from .names import is_magic_var


class PypTransform:
    """
    PypTransform is responsible for transforming all input code.

    A lot of pyp's magic comes from it making decisions based on defined and undefined names in the input. This class
    helps keep track of that state as things change based on transformations. In general, the logic in here is very
    sensitive to reordering; there are various implicit assumptions about what transformations have happened and what
    names have been defined. But the code is pretty small and the tests are good, so you should be okay!
    """

    def __init__(
            self,
            before: list[str],
            code: list[str],
            after: list[str],
            define_pypprint: bool,
            config: PypConfig,
    ) -> None:
        def parse_input(code: list[str]) -> ast.Module:
            try:
                return ast.parse(textwrap.dedent('\n'.join(code).strip()))
            except SyntaxError as e:
                message = traceback.format_exception_only(type(e), e)
                message[0] = 'Invalid input\n\n'
                raise PypError(''.join(message).strip()) from e

        self.before_tree = parse_input(before)
        self.tree = parse_input(code)
        self.after_tree = parse_input(after)

        f = NameFinder(self.before_tree, self.tree, self.after_tree)
        self.defined: set[str] = f.top_level_defined
        self.undefined: set[str] = f.undefined
        self.wildcard_imports: list[str] = f.wildcard_imports

        # We'll always use sys in ``build_input``, so add it to undefined.
        # This lets config define it or lets us automatically import it later
        # (If before defines it, we'll just let it override the import...)
        self.undefined.add('sys')

        self.define_pypprint = define_pypprint
        self.config = config

        # The print statement ``build_output`` will add, if it determines it needs to.
        self.implicit_print: ast.Call | None = None

    def build_missing_config(self) -> None:
        """Modifies the AST to define undefined names defined in config."""

        config_definitions: set[str] = set()
        attempt_to_define = set(self.undefined)
        while attempt_to_define:
            can_define = attempt_to_define & set(self.config.name_to_def)
            # The things we can define might in turn require some definitions, so update the things
            # we need to attempt to define and loop
            attempt_to_define = set()
            for name in can_define:
                config_definitions.update(self.config.def_to_names[self.config.name_to_def[name]])
                attempt_to_define.update(self.config.requires[self.config.name_to_def[name]])
            # We don't need to attempt to define things we've already decided we need to define
            attempt_to_define -= config_definitions

        config_indices = {self.config.name_to_def[name] for name in config_definitions}

        # Run basically the same thing in reverse to see which dependencies stem from magic vars
        before_config_indices = set(config_indices)
        derived_magic_indices = {i for i in config_indices if any(map(is_magic_var, self.config.requires[i]))}
        derived_magic_names = set()

        while derived_magic_indices:
            before_config_indices -= derived_magic_indices
            derived_magic_names |= {name for i in derived_magic_indices for name in self.config.def_to_names[i]}
            derived_magic_indices = {i for i in before_config_indices if self.config.requires[i] & derived_magic_names}
        magic_config_indices = config_indices - before_config_indices

        before_config_defs = [self.config.parts[i] for i in sorted(before_config_indices)]
        magic_config_defs = [self.config.parts[i] for i in sorted(magic_config_indices)]

        self.before_tree.body = before_config_defs + self.before_tree.body
        self.tree.body = magic_config_defs + self.tree.body

        for i in config_indices:
            self.undefined.update(self.config.requires[i])
        self.defined |= config_definitions
        self.undefined -= config_definitions

    def define(self, name: str) -> None:
        """Defines a name."""

        self.defined.add(name)
        self.undefined.discard(name)

    def get_valid_name_in_top_scope(self, name: str) -> str:
        """Return a name related to ``name`` that does not conflict with existing definitions."""

        while name in self.defined or name in self.undefined:
            name += '_'
        return name

    def build_output(self) -> None:
        """
        Ensures that the AST prints something.

        This is done by either a) checking whether we load a thing that prints, or b) if the last thing in the tree is
        an expression, modifying the tree to print it.
        """

        if self.undefined & {'print', 'pprint', 'pp', 'pypprint'}:  # has an explicit print
            return

        def inner(body: list[ast.stmt], use_pypprint: bool = False) -> bool:
            if not body:
                return False
            if isinstance(body[-1], ast.Pass):
                del body[-1]
                return True
            if not isinstance(body[-1], ast.Expr):
                if (
                    # If the last thing in the tree is a statement that has a body
                    hasattr(body[-1], 'body')
                    # and doesn't have an orelse, since users could expect the print in that branch
                    and not getattr(body[-1], 'orelse', [])
                    # and doesn't enter a new scope
                    and not isinstance(
                        body[-1], (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
                    )
                ):
                    # ...then recursively look for a standalone expression
                    return inner(body[-1].body, use_pypprint)
                return False

            if isinstance(body[-1].value, ast.Name):
                output = body[-1].value.id
                body.pop()
            else:
                output = self.get_valid_name_in_top_scope('output')
                self.define(output)
                body[-1] = ast.Assign(
                    targets=[ast.Name(id=output, ctx=ast.Store())],
                    value=body[-1].value,
                )

            print_fn = 'print'
            if use_pypprint:
                print_fn = 'pypprint'
                self.undefined.add('pypprint')

            if_print = ast.parse(f'if {output} is not None: {print_fn}({output})').body[0]
            body.append(if_print)

            self.implicit_print = if_print.body[0].value  # type: ignore
            return True

        # First attempt to add a print to self.after_tree, then to self.tree. We use pypprint in self.after_tree and
        # print in self.tree, although the latter is subject to change later on if we call
        # ``use_pypprint_for_implicit_print``. This logic could be a little simpler if we refactored so that we know
        # what transformations we will do before we do them.
        success = inner(self.after_tree.body, True) or inner(self.tree.body)
        if not success:
            raise PypError(
                "Code doesn't generate any output; either explicitly print something, end with an expression that pyp "
                "can print, or explicitly end with `pass`.",
            )

    def use_pypprint_for_implicit_print(self) -> None:
        """If we implicitly print, use pypprint instead of print."""

        if self.implicit_print is not None:
            self.implicit_print.func.id = 'pypprint'  # type: ignore

            # Make sure we import it later
            self.undefined.add('pypprint')

    def build_input(self) -> None:
        """
        Modifies the AST to use input from stdin.

        How we do this depends on which magic variables are used.
        """

        possible_vars = {typ: names & self.undefined for typ, names in MAGIC_VARS.items()}

        if (possible_vars['loop'] or possible_vars['index']) and possible_vars['input']:
            loop_names = ', '.join(possible_vars['loop'] or possible_vars['index'])
            input_names = ', '.join(possible_vars['input'])
            raise PypError(f'Candidates found for both loop variable ({loop_names}) and input variable ({input_names})')

        for typ, names in possible_vars.items():
            if len(names) > 1:
                names_str = ', '.join(names)
                raise PypError(f'Multiple candidates for {typ} variable: {names_str}')

        if possible_vars['loop'] or possible_vars['index']:
            # We'll loop over stdin and define loop / index variables
            idx_var = possible_vars['index'].pop() if possible_vars['index'] else None
            loop_var = possible_vars['loop'].pop() if possible_vars['loop'] else None

            if loop_var:
                self.define(loop_var)
            if idx_var:
                self.define(idx_var)
            if loop_var is None:
                loop_var = '_'

            if idx_var:
                for_loop = f'for {idx_var}, {loop_var} in enumerate(sys.stdin): '
            else:
                for_loop = f'for {loop_var} in sys.stdin: '
            for_loop += f"{loop_var} = {loop_var}.rstrip('\\n')"

            loop: ast.For = ast.parse(for_loop).body[0]  # type: ignore
            loop.body.extend(self.tree.body)
            self.tree.body = [loop]
        elif possible_vars['input']:
            # We'll read from stdin and define the necessary input variable
            input_var = possible_vars['input'].pop()
            self.define(input_var)

            if input_var == 'stdin':
                input_assign = ast.parse(f'{input_var} = sys.stdin')
            else:
                input_assign = ast.parse(f"{input_var} = [x.rstrip('\\n') for x in sys.stdin]")

            self.tree.body = input_assign.body + self.tree.body
            self.use_pypprint_for_implicit_print()
        else:
            no_pipe_assertion = ast.parse(
                'assert sys.stdin.isatty() or not sys.stdin.read(), '
                """"The command doesn't process input, but input is present. """
                '''Maybe you meant to use a magic variable like `stdin` or `x`?"''',
            )
            self.tree.body = no_pipe_assertion.body + self.tree.body
            self.use_pypprint_for_implicit_print()

    def build_missing_imports(self) -> None:
        """Modifies the AST to import undefined names."""

        self.undefined -= set(dir(__import__('builtins')))

        # Optimisation: we will almost always define sys and pypprint. However, in order for us to get to `import sys`,
        # we'll need to examine our wildcard imports, which in the presence of config, could be slow.
        if 'pypprint' in self.undefined:
            pypprint_def = inspect.getsource(pypprint) if self.define_pypprint else 'from pyp import pypprint'
            self.before_tree.body = ast.parse(pypprint_def).body + self.before_tree.body
            self.undefined.remove('pypprint')

        if 'sys' in self.undefined:
            self.before_tree.body = ast.parse('import sys').body + self.before_tree.body
            self.undefined.remove('sys')

        # Now short circuit if we can
        if not self.undefined:
            return

        def get_names_in_module(module: str) -> ta.Any:
            try:
                mod = importlib.import_module(module)
            except ImportError as e:
                raise PypError(
                    f'Config contains wildcard import from {module}, but {module} failed to import',
                ) from e
            return getattr(mod, '__all__', (n for n in dir(mod) if not n.startswith('_')))

        subimports = {'Path': 'pathlib', 'pp': 'pprint'}
        wildcard_imports = (
            ['itertools', 'math', 'collections']
            + self.config.wildcard_imports
            + self.wildcard_imports
        )
        subimports.update({name: module for module in wildcard_imports for name in get_names_in_module(module)})

        def get_import_for_name(name: str) -> str:
            if name in subimports:
                return f'from {subimports[name]} import {name}'
            return f'import {name}'

        self.before_tree.body = [
            ast.parse(stmt).body[0] for stmt in sorted(map(get_import_for_name, self.undefined))
        ] + self.before_tree.body

    def build(self) -> ast.Module:
        """Returns a transformed AST."""

        self.build_missing_config()
        self.build_output()
        self.build_input()
        self.build_missing_imports()

        ret = ast.parse('')
        ret.body = self.before_tree.body + self.tree.body + self.after_tree.body
        # Add fake line numbers to the nodes, so we can generate a traceback on error
        i = 0
        for node in dfs_walk(ret):
            if isinstance(node, ast.stmt):
                i += 1
            node.lineno = i  # type: ignore[attr-defined]
            node.end_lineno = i  # type: ignore[attr-defined]

        return ast.fix_missing_locations(ret)
