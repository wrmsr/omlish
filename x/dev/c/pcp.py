from pycparser import c_ast
from pycparser import c_generator
from pycparser import c_parser


def _main():
    ###### https://github.com/eliben/pycparser/blob/8241847ebec08b165bc9fecaf17879399bb7aba6/examples/explore_ast.py

    text = r"""
        typedef int Node, Hash;

        void HashPrint(Hash* hash, void (*PrintFunc)(char*, char*))
        {
            unsigned int i;

            if (hash == NULL || hash->heads == NULL)
                return;

            for (i = 0; i < hash->table_size; ++i)
            {
                Node* temp = hash->heads[i];

                while (temp != NULL)
                {
                    PrintFunc(temp->entry->key, temp->entry->value);
                    temp = temp->next;
                }
            }
        }
    """

    # Create the parser and ask to parse the text. parse() will throw a ParseError if there's an error in the code
    parser = c_parser.CParser()
    ast = parser.parse(text, filename='<none>')

    # Uncomment the following line to see the AST in a nice, human readable way. show() is the most useful tool in
    # exploring ASTs created by pycparser. See the c_ast.py file for the options you can pass it.

    ast.show(showcoord=True)

    # OK, we've seen that the top node is FileAST. This is always the top node of the AST. Its children are "external
    # declarations", and are stored in a list called ext[] (see _c_ast.cfg for the names and types of Nodes and their
    # children). As you see from the printout, our AST has two Typedef children and one FuncDef child.
    # Let's explore FuncDef more closely. As I've mentioned, the list ext[] holds the children of FileAST. Since the
    # function definition is the third child, it's ext[2]. Uncomment the following line to show it:

    ast.ext[2].show()

    # A FuncDef consists of a declaration, a list of parameter declarations (for K&R style function definitions), and a
    # body. First, let's examine the declaration.

    function_decl = ast.ext[2].decl

    # function_decl, like any other declaration, is a Decl. Its type child is a FuncDecl, which has a return type and
    # arguments stored in a ParamList node

    function_decl.type.show()
    function_decl.type.args.show()

    # The following displays the name and type of each argument:

    for param_decl in function_decl.type.args.params:
        print('Arg name: %s' % param_decl.name)
        print('Type:')
        param_decl.type.show(offset=6)

    # The body is of FuncDef is a Compound, which is a placeholder for a block surrounded by {} (You should be reading
    # _c_ast.cfg parallel to this explanation and seeing these things with your own eyes).
    # Let's see the block's declarations:

    function_body = ast.ext[2].body

    # The following displays the declarations and statements in the function body

    for decl in function_body.block_items:
        decl.show()

    # We can see a single variable declaration, i, declared to be a simple type
    # declaration of type 'unsigned int', followed by statements.

    # block_items is a list, so the third element is the For statement:

    for_stmt = function_body.block_items[2]
    for_stmt.show()

    # As you can see in _c_ast.cfg, For's children are 'init, cond, next' for the respective parts of the 'for' loop
    # specifier, and stmt, which is either a single stmt or a Compound if there's a block.
    #
    # Let's dig deeper, to the while statement inside the for loop:

    while_stmt = for_stmt.stmt.block_items[1]
    while_stmt.show()

    # While is simpler, it only has a condition node and a stmt node. The condition:

    while_cond = while_stmt.cond
    while_cond.show()

    # Note that it's a BinaryOp node - the basic constituent of expressions in our AST. BinaryOp is the expression tree,
    # with left and right nodes as children. It also has the op attribute, which is just the string representation of
    # the operator.

    print(while_cond.op)
    while_cond.left.show()
    while_cond.right.show()

    # That's it for the example. I hope you now see how easy it is to explore the AST created by pycparser. Although on
    # the surface it is quite complex and has a lot of node types, this is the inherent complexity of the C language
    # every parser/compiler designer has to cope with.
    # Using the tools provided by the c_ast package it's easy to explore the structure of AST nodes and write code that
    # processes them.
    # Specifically, see the cdecl.py example for a non-trivial demonstration of what you can do by recursively going
    # through the AST.

    ######

    def empty_main_function_ast():
        constant_zero = c_ast.Constant(type='int', value='0')
        return_node = c_ast.Return(expr=constant_zero)
        compound_node = c_ast.Compound(block_items=[return_node])
        type_decl_node = c_ast.TypeDecl(declname='main', quals=[],
                                        type=c_ast.IdentifierType(names=['int']),
                                        align=[])
        func_decl_node = c_ast.FuncDecl(args=c_ast.ParamList([]),
                                        type=type_decl_node)
        func_def_node = c_ast.Decl(name='main', quals=[], storage=[], funcspec=[],
                                   type=func_decl_node, init=None,
                                   bitsize=None, align=[])
        main_func_node = c_ast.FuncDef(decl=func_def_node, param_decls=None,
                                       body=compound_node)

        return main_func_node

    def generate_c_code(my_ast):
        generator = c_generator.CGenerator()
        return generator.visit(my_ast)

    main_function_ast = empty_main_function_ast()
    print("|----------------------------------------|")
    main_function_ast.show(offset=2)
    print("|----------------------------------------|")
    main_c_code = generate_c_code(main_function_ast)
    print("C code: \n%s" % main_c_code)


if __name__ == '__main__':
    _main()
