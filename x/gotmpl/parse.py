"""
https://github.com/golang/go/blob/3d33437c450aa74014ea1d41cd986b6ee6266984/src/text/template/parse/parse.go
"""
# Copyright 2009 The Go Authors.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#      disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#      following disclaimer in the documentation and/or other materials provided with the distribution.
#    * Neither the name of Google LLC nor the names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import typing as ta

from .lex import Lexer
from .lex import Pos
from .lex import Token
from .lex import TokenType
from .nodes import ActionNode
from .nodes import BoolNode
from .nodes import BranchNode
from .nodes import BreakNode
from .nodes import ChainNode
from .nodes import CommandNode
from .nodes import CommentNode
from .nodes import ContinueNode
from .nodes import DotNode
from .nodes import ElseNode
from .nodes import EndNode
from .nodes import FieldNode
from .nodes import IfNode
from .nodes import ListNode
from .nodes import NilNode
from .nodes import Node
from .nodes import NodeType
from .nodes import NumberNode
from .nodes import PipeNode
from .nodes import RangeNode
from .nodes import StringNode
from .nodes import TemplateNode
from .nodes import TextNode
from .nodes import VariableNode
from .nodes import WithNode


# Tree is the representation of a single parsed template.
class Tree:
    def __init__(self, name: str, *funcs: dict[str, ta.Callable]) -> None:
        super().__init__()

        self._name = name  # name of the template represented by the tree.
        self._funcs = list(funcs)

        self._parse_name: str = ''  # name of the top-level template during parsing, for error messages.
        self._root: ListNode | None = None  # top-level root of the tree.
        self._mode: int = 0  # parsing mode.
        self._text: str = ''  # text parsed to create the template (or its parent)

        # Parsing only; cleared after parse.
        self._lex: Lexer | None = None
        self._token: list[Token] = []  # three-token lookahead for parser.
        self._peek_count: int = 0
        self._vars: list[str] = []  # variables defined at the moment.
        self._tree_set: dict[str, Tree] = {}
        self._action_line: int = 0  # line of left delim starting action
        self._range_depth: int = 0

    #

    def new_list(self, pos: Pos) -> ListNode:
        return ListNode(tree=self, type=NodeType.LIST, pos=pos)

    def new_text(self, pos: Pos, text: str) -> TextNode:
        return TextNode(tree=self, type=NodeType.TEXT, pos=pos, text=text)

    def new_comment(self, pos: Pos, text: str) -> CommentNode:
        return CommentNode(tree=self, type=NodeType.COMMENT, pos=pos, text=text)

    def new_pipeline(self, pos: Pos, line: int, vars: list[VariableNode]) -> PipeNode:
        return PipeNode(tree=self, type=NodeType.PIPE, pos=pos, line=line, decl=vars)

    def new_action(self, pos: Pos, line: int, pipe: PipeNode) -> ActionNode:
        return ActionNode(tree=self, type=NodeType.ACTION, pos=pos, line=line, pipe=pipe)

    def new_command(self, pos: Pos) -> CommandNode:
        return CommandNode(tree=self, type=NodeType.COMMAND, pos=pos)

    def new_variable(self, pos: Pos, ident: str) -> VariableNode:
        return VariableNode(tree=self, type=NodeType.VARIABLE, pos=pos, ident=ident.split('.'))

    def new_dot(self, pos: Pos) -> DotNode:
        return DotNode(tree=self, type=NodeType.DOT, pos=pos)

    def new_nil(self, pos: Pos) -> NilNode:
        return NilNode(tree=self, type=NodeType.NIL, pos=pos)

    def new_field(self, pos: Pos, ident: str) -> FieldNode:
        return FieldNode(tree=self, type=NodeType.FIELD, pos=pos, ident=ident[1:].split('.'))  # [1:] to drop leading period  # noqa

    def new_chain(self, pos: Pos, node: Node) -> ChainNode:
        return ChainNode(tree=self, type=NodeType.CHAIN, pos=pos, node=node)

    def new_bool(self, pos: Pos, is_true: bool) -> BoolNode:
        return BoolNode(tree=self, type=NodeType.BOOL, pos=pos, is_true=is_true)

    def new_number(self, pos: Pos, text: str, typ: TokenType) -> NumberNode:
        n = NumberNode(tree=self, type=NodeType.NUMBER, pos=pos, text=text)  # noqa

        # switch typ {
        # case TokenType.CHAR_CONSTANT:
        #     rune, _, tail, err = strconv.UnquoteChar(text[1:], text[0])
        #     if err != nil {
        #         return nil, err
        #     }
        #     if tail != "'" {
        #         return nil, fmt.Errorf("malformed character constant: %s", text)
        #     }
        #     n.Int64 = int64(rune)
        #     n.IsInt = true
        #     n.Uint64 = uint64(rune)
        #     n.IsUint = true
        #     n.Float64 = float64(rune) # odd but those are the rules.
        #     n.IsFloat = true
        #     return n, nil
        # case TokenType.COMPLEX:
        #     # fmt.Sscan can parse the pair, so let it do the work.
        #     if _, err = fmt.Sscan(text, &n.Complex128); err != nil {
        #         return nil, err
        #     }
        #     n.IsComplex = true
        #     n.simplifyComplex()
        #     return n, nil
        # }
        # # Imaginary constants can only be complex unless they are zero.
        # if len(text) > 0 and text[len(text)-1] == 'i' {
        #     f, err = strconv.ParseFloat(text[:len(text)-1], 64)
        #     if err == nil {
        #         n.IsComplex = true
        #         n.Complex128 = complex(0, f)
        #         n.simplifyComplex()
        #         return n, nil
        #     }
        # }
        # # Do integer test first so we get 0x123 etc.
        # u, err = strconv.ParseUint(text, 0, 64) # will fail for -0; fixed below.
        # if err == nil {
        #     n.IsUint = true
        #     n.Uint64 = u
        # }
        # i, err = strconv.ParseInt(text, 0, 64)
        # if err == nil {
        #     n.IsInt = true
        #     n.Int64 = i
        #     if i == 0 {
        #         n.IsUint = true # in case of -0.
        #         n.Uint64 = u
        #     }
        # }
        # # If an integer extraction succeeded, promote the float.
        # if n.IsInt {
        #     n.IsFloat = true
        #     n.Float64 = float64(n.Int64)
        # } else if n.IsUint {
        #     n.IsFloat = true
        #     n.Float64 = float64(n.Uint64)
        # } else {
        #     f, err = strconv.ParseFloat(text, 64)
        #     if err == nil {
        #         # If we parsed it as a float but it looks like an integer,
        #         # it's a huge number too large to fit in an int. Reject it.
        #         if !strings.ContainsAny(text, ".eEpP") {
        #             return nil, fmt.Errorf("integer overflow: %r", text)
        #         }
        #         n.IsFloat = true
        #         n.Float64 = f
        #         # If a floating-point extraction succeeded, extract the int if needed.
        #         if !n.IsInt and float64(int64(f)) == f {
        #             n.IsInt = true
        #             n.Int64 = int64(f)
        #         }
        #         if !n.IsUint and float64(uint64(f)) == f {
        #             n.IsUint = true
        #             n.Uint64 = uint64(f)
        #         }
        #     }
        # }
        # if !n.IsInt and !n.IsUint and !n.IsFloat {
        #     return nil, fmt.Errorf("illegal number syntax: %r", text)
        # }
        # return n, nil

        raise NotImplementedError

    def new_string(self, pos: Pos, orig: str, text: str) -> StringNode:
        return StringNode(tree=self, type=NodeType.STRING, pos=pos, quoted=orig, text=text)

    def new_end(self, pos: Pos) -> EndNode:
        return EndNode(tree=self, type=NodeType.END, pos=pos)

    def new_else(self, pos: Pos, line: int) -> ElseNode:
        return ElseNode(tree=self, type=NodeType.ELSE, pos=pos, line=line)

    def new_if(self, pos: Pos, line: int, pipe: PipeNode, lst: ListNode, else_lst: ListNode) -> IfNode:
        return IfNode(BranchNode(tree=self, type=NodeType.IF, pos=pos, line=line, pipe=pipe, lst=lst, else_lst=else_lst))  # noqa

    def new_break(self, pos: Pos, line: int) -> BreakNode:
        return BreakNode(tree=self, type=NodeType.BREAK, pos=pos, line=line)

    def new_continue(self, pos: Pos, line: int) -> ContinueNode:
        return ContinueNode(tree=self, type=NodeType.CONTINUE, pos=pos, line=line)

    def new_range(self, pos: Pos, line: int, pipe: PipeNode, lst: ListNode, else_list) -> RangeNode:
        return RangeNode(BranchNode(tree=self, type=NodeType.RANGE, pos=pos, line=line, pipe=pipe, lst=lst, else_lst=else_lst))  # noqa

    def new_with(self, pos: Pos, line: int, pipe: PipeNode, lst: ListNode, else_lst: ListNode) -> WithNode:
        return WithNode(BranchNode(tree=self, type=NodeType.WITH, pos=pos, line=line, pipe=pipe, lst=lst, else_lst=else_lst))  # noqa

    def new_template(self, pos: Pos, line: int, name: str, pipe: PipeNode) -> TemplateNode:
        return TemplateNode(tree=self, type=NodeType.TEMPLATE, pos=pos, line=line, name=name, pipe=pipe)

    #

    def next(self) -> Token:
        # next returns the next token.
        if self._peek_count > 0:
            self._peek_count -= 1
        else:
            self._token[0] = self._lex.next_token()
        return self._token[self._peek_count]

    def backup(self) -> None:
        # backup backs the input stream up one token.
        self._peek_count += 1

    def backup2(self, t1: Token) -> None:
        # backup2 backs the input stream up two tokens. The zeroth token is already there.
        self._token[1] = t1
        self._peek_count = 2

    def backup3(self, t2: Token, t1: Token) -> None:  # Reverse order: we're pushing back.
        # backup3 backs the input stream up three tokens. The zeroth token is already there.
        self._token[1] = t1
        self._token[2] = t2
        self._peek_count = 3

    # peek returns but does not consume the next token.
    def peek(self) -> Token:
        if self._peek_count > 0:
            return self._token[self._peek_count - 1]
        self._peek_count = 1
        self._token[0] = self._lex.next_token()
        return self._token[0]

    # next_non_space returns the next non-space token.
    def next_non_space(self) -> Token:
        while True:
            token = self.next()
            if token.typ != TokenType.SPACE:
                break
        return token

    # peek_non_space returns but does not consume the next non-space token.
    def peek_non_space(self) -> Token:
        token = self.next_non_space()
        self.backup()
        return token

    # Parsing.

    def error_context(self, n: Node) -> tuple[str, str]:  # (location, context)
        # ErrorContext returns a textual representation of the location of the node in the input text. The receiver is
        # only used when the node does not have a pointer to the tree inside, which can occur in old code.
        pos = n.pos
        tree = n.tree
        if not tree:
            tree = self
        text = tree._text[:pos]
        byte_num = text.rfind('\n')
        if byte_num == -1:
            byte_num = pos # On first line.
        else:
            byte_num += 1 # After the newline.
            byte_num = pos - byte_num
        line_num = 1 + text.count('\n')
        context = str(n)
        return "%s:%d:%d" % (tree._parse_name, line_num, byte_num), context

    def errorf(self, format: str, *args: ta.Any) -> ta.NoReturn:
        # errorf formats the error and terminates processing.
        self._root = None
        format = 'template: %s:%d: %s' % (self._parse_name, self._token[0].line, format)
        raise Exception(format, *args)

    def error(self, err: Exception) -> ta.NoReturn:
        # error terminates processing.
        raise err

    def expect(self, expected: TokenType, context: str) -> Token:
        # expect consumes the next token and guarantees it has the required type.
        token = self.next_non_space()
        if token.typ != expected:
            self.unexpected(token, context)
        return token

    def expect_one_of(self, expected1: TokenType, expected2: TokenType, context: str) -> Token:
        # expect_one_of consumes the next token and guarantees it has one of the required types.
        token = self.next_non_space()
        if token.typ != expected1 and token.typ != expected2:
            self.unexpected(token, context)
        return token

    def unexpected(self, token: Token, context: str) -> ta.NoReturn:
        # unexpected complains about the token and terminates processing.
        if token.typ == TokenType.ERROR:
            extra = ''
            if self._action_line != 0 and self._action_line != token.line:
                extra = ' in action started at %s:%d' % (self._parse_name, self._action_line)
                if token.val.endswith(' action'):
                    extra = extra[len(' in action'):]  # avoid "action in action"
            self.errorf("%s%s", token, extra)
        self.errorf("unexpected %s in %s", token, context)

    def start_parse(
            self,
            funcs: list[dict[str, ta.Any]],
            lex: Lexer,
            tree_set: dict[str, 'Tree'],
    ) -> None:
        # startParse initializes the parser, using the lexer.
        self._root = None
        self._lex = lex
        self._vars = ['$']
        self._funcs = funcs
        self._tree_set = tree_set
        lex._options = LexOptions(  # noqa
            emit_comment=(self._mode & MODE_PARSE_COMMENTS) != 0,
            break_ok=not self.has_function('break'),
            continue_ok=not self.has_function('continue'),
        )

    def stop_parse(self) -> None:
        # stop_parse terminates parsing.
        self._lex = None
        self._vars = None
        self._funcs = None
        self._tree_set = None

    def parse(
            self,
            text: str,
            left_delim: str,
            right_delim: str,
            tree_set: dict[str, 'Tree'],
            *funcs: dict[str, ta.Any],
    ) -> 'Tree':
        # Parse parses the template definition string to construct a representation of the template for execution. If
        # either action delimiter string is empty, the default ("{{" or "}}") is used. Embedded template definitions are
        # added to the tree_set map.
        try:
            self._parse_name = self._name
            lexer = Lexer(
                self._name,
                text,
                left_delim=left_delim,
                right_delim=right_delim,
            )
            self.start_parse(list(funcs), lexer, tree_set)
            self._text = text
            self._parse()
            self.add()
            self.stop_parse()
            return self
        except Exception as e:
            self.stop_parse()
            raise e

    def add(self) -> None:
        # add adds tree to t.tree_set.
        tree = self._tree_set[self._name]
        if tree is None or is_empty_tree(tree._root):
            self._tree_set[self._name] = self
            return
        if not is_empty_tree(self._root):
            self.errorf('template: multiple definition of template %r', self._name)

    def _parse(self) -> None:
        # parse is the top-level parser for a template, essentially the same as TokenType.LIST except it also parses
        # {{define}} actions. It runs to EOF.
        self._root = self.new_list(self.peek().pos)
        while self.peek().typ != TokenType.EOF:
            if self.peek().typ == TokenType.LEFT_DELIM:
                delim = self.next()
                if self.next_non_space().typ == TokenType.DEFINE:
                    new_t = Tree('definition')  # name will be updated once we know it.
                    new_t._text = self._text
                    new_t._mode = self._mode
                    new_t._parse_name = self._parse_name
                    new_t.start_parse(self._funcs, self._lex, self._tree_set)
                    new_t.parse_definition()
                    continue
                self.backup2(delim)
            n = self.text_or_action()
            if n.type in (NodeType.END, NodeType.ELSE):
                self.errorf('unexpected %s', n)
            else:
                self._root.append(n)

    def parse_definition(self) -> None:
        # parseDefinition parses a {{define}} ...  {{end}} template definition and installs the definition in
        # t.tree_set. The "define" keyword has already been scanned.
        context = 'define clause'
        name = self.expect_one_of(TokenType.STRING, TokenType.RAW_STRING, context)
        try:
            self._name = unquote(name.val)
        except Exception as err:
            self.error(err)
        self.expect(TokenType.RIGHT_DELIM, context)
        self._root, end = self.item_list()
        if end.type != NodeType.END:
            self.errorf("unexpected %s in %s", end, context)
        self.add()
        self.stop_parse()

    def item_list(self) -> tuple[ListNode, Node]:  # (list, next)
        # itemList:
        #
        #    text_or_action*
        #
        # Terminates at {{end}} or {{else}}, returned separately.
        lst = self.new_list(self.peek_non_space().pos)
        while self.peek_non_space().typ != TokenType.EOF:
            n = self.text_or_action()
            if n.type in (NodeType.END, NodeType.ELSE):
                return lst, n
            lst.append(n)
        self.errorf('unexpected EOF')

    def text_or_action(self) -> Node:
        # text_or_action:
        #
        #    text | comment | action
        token = self.next_non_space()
        if token.typ == TokenType.TEXT:
            return self.new_text(token.pos, token.val)
        elif token.typ == TokenType.LEFT_DELIM:
            self._action_line = token.line
            try:
                return self.action()
            finally:
                self.clear_action_line()
        elif token.typ == TokenType.COMMENT:
            return self.new_comment(token.pos, token.val)
        else:
            self.unexpected(token, 'input')

    def clear_action_line(self) -> None:
        self._action_line = 0

    def action(self) -> Node:
        # Action:
        #
        #    control
        #    command ("|" command)*
        #
        # Left delim is past. Now get actions.
        # First word could be a keyword such as range.
        token = self.next_non_space()
        if token.typ == TokenType.BLOCK:
            return self.block_control()
        elif token.typ == TokenType.BREAK:
            return self.break_control(token.pos, token.line)
        elif token.typ == TokenType.CONTINUE:
            return self.continue_control(token.pos, token.line)
        elif token.typ == TokenType.ELSE:
            return self.else_control()
        elif token.typ == TokenType.END:
            return self.end_control()
        elif token.typ == TokenType.IF:
            return self.if_control()
        elif token.typ == TokenType.RANGE:
            return self.range_control()
        elif token.typ == TokenType.TEMPLATE:
            return self.template_control()
        elif token.typ == TokenType.WITH:
            return self.with_control()
        self.backup()
        token = self.peek()
        # Do not pop variables; they persist until 'end'.
        return self.new_action(token.pos, token.line, t.pipeline('command', TokenType.RIGHT_DELIM))

    def break_control(self, pos: Pos, line: int) -> Node:
        # Break:
        #
        #    {{break}}
        #
        # Break keyword is past.
        token = self.next_non_space()
        if token.typ != TokenType.RIGHT_DELIM:
            self.unexpected(token, '{{break}}')
        if self._range_depth == 0:
            self.errorf('{{break}} outside {{range}}')
        return self.new_break(pos, line)

    def continue_control(self, pos: Pos, line: int) -> Node:
        # Continue:
        #
        #    {{continue}}
        #
        # Continue keyword is past.
        token = self.next_non_space()
        if token.typ != TokenType.RIGHT_DELIM:
            self.unexpected(token, '{{continue}}')
        if self._range_depth == 0:
            self.errorf('{{continue}} outside {{range}}')
        return self.new_continue(pos, line)


# A mode value is a set of flags (or 0). Modes control parser behavior.
MODE_PARSE_COMMENTS = 1 << 0  # parse comments and add them to AST
MODE_SKIP_FUNC_CHECK = 1 << 1  # do not check that functions are defined


# Parse returns a map from template name to [Tree], created by parsing the templates described in the argument string.
# The top-level template will be given the specified name. If an error is encountered, parsing stops and an empty map is
# returned with the error.
def parse(
        name: str,
        text: str,
        left_delim: str,
        right_delim: str,
        funcs: dict[str, ta.Callable],
) -> dict[str, Tree]:
    tree_set: dict[str, Tree] = {}
    t = Tree(name, funcs)
    t._text = text
    t.parse(text, left_delim, right_delim, tree_set, funcs)
    return tree_set


"""
    def pipeline(self, context: str, end: TokenType) -> PipeNode:
        # Pipeline:
        #
        #    declarations? command ('|' command)*
        token = self.peek_non_space()
        pipe = self.new_pipeline(token.pos, token.line, nil)

        # Are there declarations or assignments?
        while True:
            if v = self.peek_non_space(); v.typ == TokenType.VARIABLE {
                self.next()
                # Since space is a token, we need 3-token look-ahead here in the worst case:
                # in "$x foo" we need to read "foo" (as opposed to "=") to know that $x is an
                # argument variable rather than a declaration. So remember the token
                # adjacent to the variable so we can push it back if necessary.
                token_after_variable = self.peek()
                next = self.peek_non_space()

                if next.typ in (TokenType.ASSIGN, TokenType.DECLARE):
                    pipe.is_assign = next.typ == TokenType.ASSIGN
                    self.next_non_space()
                    pipe.decl.append(self.new_variable(v.pos, v.val))
                    self._vars.append(v.val)
                    
                elif next.typ == TokenType.CHAR and next.val == ',':
                    self.next_non_space()
                    pipe.decl.append(self.new_variable(v.pos, v.val))
                    self._vars.append(v.val)
                    if context == 'range' and len(pipe.Decl) < 2:
                        if self.peek_non_space().typ in (TokenType.VARIABLE, TokenType.RIGHT_DELIM, TokenType.RIGHT_PAREN):
                            # second initialized variable in a range pipeline
                            continue
                        else:
                            self.errorf('range can only initialize variables')
                    self.errorf('too many declarations in %s', context)
                    
                elif token_after_variable.typ == TokenType.SPACE:
                    self.backup3(v, token_after_variable)

                else:
                    self.backup2(v)
            
            break

        while True:
            token = self.next_non_space()
            if token.typ == end:
                # At this point, the pipeline is complete
                self.check_pipeline(pipe, context)
                return pipe
            elif token.typ in (TokenType.BOOL, TokenType.CHAR_CONSTANT, TokenType.COMPLEX, TokenType.DOT, TokenType.FIELD, TokenType.IDENTIFIER,
                TokenType.NUMBER, TokenType.NIL, TokenType.RAWS_TRING, TokenType.STRING, TokenType.VARIABLE, TokenType.LEFT_PAREN):
                self.backup()
                pipe.append(self.command())
            else:
                self.unexpected(token, context)

    def check_pipeline(self, pipe: PipeNode, context: str) -> None:
        # Reject empty pipelines
        if len(pipe.Cmds) == 0 {
            self.errorf("missing value for %s", context)
        # Only the first command of a pipeline can start with a non executable operand
        for i, c = range pipe.Cmds[1:] {
            switch c.Args[0].type {
            case NodeBool, NodeDot, NodeNil, NodeNumber, NodeString:
                # With A|B|C, pipeline stage 2 is B
                self.errorf("non executable command in pipeline stage %d", i+2)

    def parse_control(context str) (pos Pos, line int, pipe *PipeNode, lst, elseLst *ListNode) {
        defer self.pop_vars(len(self._vars))
        pipe = self.pipeline(context, TokenType.RIGHT_DELIM)
        if context == "range" {
            self._range_depth+=1
        }
        var next Node
        lst, next = self.item_list()
        if context == "range" {
            self._range_depth-=1
        }
        switch next.type {
        case NodeType.END: #done
        case NodeType.ELSE:
            # Special case for "else if" and "else with".
            # If the "else" is followed immediately by an "if" or "with",
            # the else_control will have left the "if" or "with" token pending. Treat
            #    {{if a}}_{{else if b}}_{{end}}
            #  {{with a}}_{{else with b}}_{{end}}
            # as
            #    {{if a}}_{{else}}{{if b}}_{{end}}{{end}}
            #  {{with a}}_{{else}}{{with b}}_{{end}}{{end}}.
            # To do this, parse the "if" or "with" as usual and stop at it {{end}};
            # the subsequent{{end}} is assumed. This technique works even for long if-else-if chains.
            if context == "if" and self.peek().typ == TokenType.IF {
                self.next() # Consume the "if" token.
                elseLst = self.new_list(next.Position())
                elseLst.append(self.if_control())
            } else if context == "with" and self.peek().typ == TokenType.WITH {
                self.next()
                elseLst = self.new_list(next.Position())
                elseLst.append(self.with_control())
            } else {
                elseLst, next = self.item_list()
                if next.type != NodeType.END {
                    self.errorf("expected end; found %s", next)
                }
            }
        }
        return pipe.Position(), pipe.Line, pipe, lst, elseLst
    }

    def if_control(self) -> Node:
        # If:
        #
        #    {{if pipeline}} itemList {{end}}
        #    {{if pipeline}} itemList {{else}} itemList {{end}}
        #
        # If keyword is past.
        return self.new_if(self.parse_control('if'))

    def range_control(self) -> Node:
        # Range:
        #
        #    {{range pipeline}} itemList {{end}}
        #    {{range pipeline}} itemList {{else}} itemList {{end}}
        #
        # Range keyword is past.
        r = self.new_range(self.parse_control('range'))
        return r

    def with_control(self) -> Node:
        # With:
        #
        #    {{with pipeline}} itemList {{end}}
        #    {{with pipeline}} itemList {{else}} itemList {{end}}
        #
        # If keyword is past.
        return self.new_with(self.parse_control('with'))

    def end_control(self) -> Node:
        # End:
        #
        #    {{end}}
        #
        # End keyword is past.
        return self.new_end(self.expect(item_right_delim, 'end').pos)

    def else_control(self) -> Node:
        # Else:
        #
        #    {{else}}
        #
        # Else keyword is past.
        peek = self.peek_non_space()
        # The "{{else if ... " and "{{else with ..." will be
        # treated as "{{else}}{{if ..." and "{{else}}{{with ...".
        # So return the else node here.
        if peek.typ == TokenType.IF or peek.typ == TokenType.WITH:
            return self.newElse(peek.pos, peek.line)
        token = self.expect(TokenType.RIGHT_DELIM, "else")
        return self.newElse(token.pos, token.line)

    def block_control(self) -> Node:
        # Block:
        #
        #    {{block stringValue pipeline}}
        #
        # Block keyword is past.
        # The name must be something that can evaluate to a string.
        # The pipeline is mandatory.
        const context = "block clause"

        token = self.next_non_space()
        name = self.parse_template_name(token, context)
        pipe = self.pipeline(context, TokenType.RIGHT_DELIM)

        block = New(name) # name will be updated once we know it.
        block.text = self._text
        block.Mode = self._mode
        block.parse_name = self.parse_name
        block.startParse(self.funcs, self.lex, self.tree_set)
        var end Node
        block.Root, end = block.item_list()
        if end.type != NodeType.END {
            self.errorf("unexpected %s in %s", end, context)
        }
        block.add()
        block.stop_parse()

        return self.newTemplate(token.pos, token.line, name, pipe)

    def template_control(self) -> Node:
        # Template:
        #
        #    {{template stringValue pipeline}}
        #
        # Template keyword is past. The name must be something that can evaluate to a string.
        const context = "template clause"
        token = self.next_non_space()
        name = self.parse_template_name(token, context)
        var pipe *PipeNode
        if self.next_non_space().typ != TokenType.RIGHT_DELIM {
            self.backup()
            # Do not pop variables; they persist until "end".
            pipe = self.pipeline(context, TokenType.RIGHT_DELIM)
        return self.newTemplate(token.pos, token.line, name, pipe)

    def parse_template_name(self, token Token, context str) -> (name str):
        switch token.typ:
        case TokenType.STRING, TokenType.RAW_STRING:
            s, err = strconv.Unquote(token.val)
            if err != nil:
                self.error(err)
            name = s
        default:
            self.unexpected(token, context)
        return

    def command(self) -> CommandNode:
        # command:
        #
        #    operand (space operand)*
        #
        # space-separated arguments up to a pipeline character or right delimiter.
        # we consume the pipe character but leave the right delim to terminate the action.
        cmd = self.newCommand(self.peek_non_space().pos)
        for {
            self.peek_non_space() # skip leading spaces.
            operand = self.operand()
            if operand != nil {
                cmd.append(operand)
            }
            switch token = self.next(); token.typ {
            case TokenType.SPACE:
                continue
            case TokenType.RIGHT_DELIM, TokenType.RIGHT_PAREN:
                self.backup()
            case itemPipe:
                # nothing here; break loop below
            default:
                self.unexpected(token, "operand")
            }
            break
        if len(cmd.Args) == 0 {
            self.errorf("empty command")
        return cmd

    def operand(self) -> Node:
        # operand:
        #
        #    term .Field*
        #
        # An operand is a space-separated component of a command,
        # a term possibly followed by field accesses.
        # A nil return means the next item is not an operand.
        node = self.term()
        if node == nil {
            return nil
        if self.peek().typ == TokenType.FIELD {
            chain = self.newChain(self.peek().pos, node)
            for self.peek().typ == TokenType.FIELD {
                chain.Add(self.next().val)
            }
            # Compatibility with original API: If the term is of type NodeField
            # or NodeVariable, just put more fields on the original.
            # Otherwise, keep the Chain node.
            # Obvious parsing errors involving literal values are detected here.
            # More complex error cases will have to be handled at execution time.
            switch node.type {
            case NodeField:
                node = self.newField(chain.Position(), chain.String())
            case NodeVariable:
                node = self.newVariable(chain.Position(), chain.String())
            case NodeBool, NodeString, NodeNumber, NodeNil, NodeDot:
                self.errorf("unexpected . after term %r", node.String())
            default:
                node = chain
        return node

    def term(self) -> Node:
        # term:
        #
        #    literal (number, str, nil, boolean)
        #    function (identifier)
        #    .
        #    .Field
        #    $
        #    '(' pipeline ')'
        #
        # A term is a simple "expression".
        # A nil return means the next item is not a term.
        switch token = self.next_non_space(); token.typ {
        case TokenType.IDENTIFIER:
            checkFunc = self._mode & SkipFuncCheck == 0
            if checkFunc and !self.has_function(token.val) {
                self.errorf("function %r not defined", token.val)
            }
            return NewIdentifier(token.val).SetTree(t).SetPos(token.pos)
        case TokenType.DOT:
            return self.newDot(token.pos)
        case TokenType.NIL:
            return self.newNil(token.pos)
        case TokenType.VARIABLE:
            return self.use_var(token.pos, token.val)
        case TokenType.FIELD:
            return self.newField(token.pos, token.val)
        case TokenType.BOOL:
            return self.newBool(token.pos, token.val == "true")
        case TokenType.CHAR_CONSTANT, TokenType.COMPLEX, TokenType.NUMBER:
            number, err = self.newNumber(token.pos, token.val, token.typ)
            if err != nil {
                self.error(err)
            }
            return number
        case TokenType.LEFT_PAREN:
            return self.pipeline("parenthesized pipeline", TokenType.RIGHT_PAREN)
        case TokenType.STRING, TokenType.RAW_STRING:
            s, err = strconv.Unquote(token.val)
            if err != nil {
                self.error(err)
            }
            return self.newString(token.pos, token.val, s)
        }
        self.backup()
        return nil
    }

    def has_function(self, name: str) -> bool:
        # has_function reports if a function name exists in the Tree's maps.
        for _, funcMap = range self._funcs {
            if funcMap == nil {
                continue
            if funcMap[name] != nil {
                return true
        return false

    def pop_vars(self, n: int) -> None:
        # pop_vars trims the variable list to the specified length
        self._vars = self._vars[:n]

    def use_var(self, pos: Pos, name: str) -> Node:
        # use_var returns a node for a variable reference. It errors if the
        # variable is not defined.
        v = self.newVariable(pos, name)
        for _, varName = range self._vars {
            if varName == v.Ident[0] {
                return v
        self.errorf("undefined variable %r", v.Ident[0])
        return nil


def is_empty_tree(n: Node) -> bool:
    # is_empty_tree reports whether this tree (node) is empty of everything but space or comments.
    if n is None:
        return True
    elif isinstance(n, ActionNode, CommentNode):
        return True
    elif isinstance(n, (IfNode, ListNode)):
        for node in n.nodes:
            if not is_empty_tree(node):
                return False
        return True
    elif isinstance(n, (RangeNode, TemplateNode, TextNode)):
        return len(n.Text.strip(' ')) == 0
    elif isinstance(n, WithNode):
        pass
    else:
        raise TypeError(f'unknown node: {n}')
    return False
"""
