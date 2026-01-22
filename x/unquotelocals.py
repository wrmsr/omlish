import ast


class AnnotationUnquoter(ast.NodeTransformer):
    """
    AST transformer that unquotes string annotations on local variables in function bodies only, not class-level
    attributes.
    """

    def __init__(self):
        super().__init__()
        self._in_function_body = False

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AnnAssign:
        """
        Visit annotated assignment nodes. Only unquote if we're inside a function body (not at class or module level).
        """

        # First, recurse into any child nodes (value, target)
        self.generic_visit(node)

        # Only transform if we're inside a function body
        if not self._in_function_body:
            return node

        # Check if the annotation is a string literal
        if isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
            string_annotation = node.annotation.value
            try:
                parsed = ast.parse(string_annotation, mode='eval')
            except SyntaxError:
                pass
            else:
                new_annotation = ast.copy_location(parsed.body, node.annotation)
                ast.fix_missing_locations(new_annotation)
                node.annotation = new_annotation

        return node

    def _visit_function(self, node):
        """Common logic for visiting function definitions."""

        # Save state, enter function context
        was_in_function = self._in_function_body
        self._in_function_body = True

        # Process the function body
        self.generic_visit(node)

        # Restore state
        self._in_function_body = was_in_function
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        return self._visit_function(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """
        Visit class definitions. The class body itself is NOT a function, so we set _in_function_body = False, but
        methods inside will set it back to True.
        """

        was_in_function = self._in_function_body
        self._in_function_body = False

        self.generic_visit(node)

        self._in_function_body = was_in_function
        return node


def unquote_annotations(source: str) -> str:
    """Transform Python source code to unquote string annotations on local variables in function bodies only."""

    tree = ast.parse(source)
    transformer = AnnotationUnquoter()
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    return ast.unparse(transformed_tree)


def unquote_annotations_ast(tree: ast.AST) -> ast.AST:
    """Transform an AST to unquote string annotations on local variables in function bodies only."""

    transformer = AnnotationUnquoter()
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    return transformed_tree


if __name__ == '__main__':
    test_code = '''
# Module level - should NOT be transformed
module_var: "ModuleType" = 1

def outer_function():
    # Function local - SHOULD be transformed
    x: "int" = 5
    y: "list[str]"

    def inner_function():
        # Nested function local - SHOULD be transformed
        a: "float" = 3.14
        return a

    return x


class MyClass:
    # Class attribute - should NOT be transformed
    class_attr: "ClassAttrType"
    other_attr: "OtherType" = []

    def __init__(self):
        # These are in a function body - SHOULD be transformed
        self.instance_var: "InstanceType" = None
        local_in_init: "LocalInitType" = 42

    def method(self):
        # Function local - SHOULD be transformed
        method_local: "MethodLocalType" = []

        def nested_in_method():
            # Nested function local - SHOULD be transformed
            nested_var: "NestedVarType" = {}
            return nested_var

        return method_local

    class NestedClass:
        # Nested class attribute - should NOT be transformed
        nested_class_attr: "NestedClassAttr"

        def nested_class_method(self):
            # Function local - SHOULD be transformed
            nested_class_var: "NestedClassVarType" = True
            return nested_class_var
'''

    print('Original code:')
    print('=' * 60)
    print(test_code)
    print('\n' + '=' * 60)
    print('Transformed code:')
    print('=' * 60)

    transformed = unquote_annotations(test_code)
    print(transformed)

    # Verify
    print('\n' + '=' * 60)
    print('Verification:')
    try:
        ast.parse(transformed)
        print('✓ Transformed code is valid Python!')
    except SyntaxError as e:
        print(f'✗ Syntax error: {e}')

    # Check specific expectations
    print('\nChecking specific transformations:')
    checks = [
        ("class_attr: 'ClassAttrType'", 'Class attr should stay quoted'),
        ("other_attr: 'OtherType'", 'Class attr should stay quoted'),
        ("nested_class_attr: 'NestedClassAttr'", 'Nested class attr should stay quoted'),
        ("module_var: 'ModuleType'", 'Module var should stay quoted'),
        ('x: int', 'Function local should be unquoted'),
        ('a: float', 'Nested function local should be unquoted'),
        ('local_in_init: LocalInitType', 'Method local should be unquoted'),
        ('method_local: MethodLocalType', 'Method local should be unquoted'),
        ('nested_var: NestedVarType', 'Nested-in-method local should be unquoted'),
        ('nested_class_var: NestedClassVarType', 'Nested class method local should be unquoted'),
    ]

    for pattern, description in checks:
        if pattern in transformed:
            print(f'  ✓ {description}')
        else:
            print(f"  ✗ {description} - pattern '{pattern}' not found")
