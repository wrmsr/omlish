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
from .nodes import ChainNode
from .nodes import CommandNode
from .nodes import CommentNode
from .nodes import DotNode
from .nodes import FieldNode
from .nodes import ListNode
from .nodes import NilNode
from .nodes import Node
from .nodes import NodeType
from .nodes import PipeNode
from .nodes import TextNode
from .nodes import VariableNode


# Tree is the representation of a single parsed template.
class Tree:
    def __init__(self, name: str, funcs: ta.Mapping[str, ta.Callable]) -> None:
        super().__init__()

        self._name = name  # name of the template represented by the tree.
        self._funcs = funcs

        self._parse_name: str = ''  # name of the top-level template during parsing, for error messages.
        self._root: ListNode  # top-level root of the tree.
        self._mode: int = 0  # parsing mode.
        self._text: str = ''  # text parsed to create the template (or its parent)

        # Parsing only; cleared after parse.
        self._lex: Lexer
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
        # case itemCharConstant:
        #     rune, _, tail, err := strconv.UnquoteChar(text[1:], text[0])
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
        # case itemComplex:
        #     # fmt.Sscan can parse the pair, so let it do the work.
        #     if _, err := fmt.Sscan(text, &n.Complex128); err != nil {
        #         return nil, err
        #     }
        #     n.IsComplex = true
        #     n.simplifyComplex()
        #     return n, nil
        # }
        # # Imaginary constants can only be complex unless they are zero.
        # if len(text) > 0 && text[len(text)-1] == 'i' {
        #     f, err := strconv.ParseFloat(text[:len(text)-1], 64)
        #     if err == nil {
        #         n.IsComplex = true
        #         n.Complex128 = complex(0, f)
        #         n.simplifyComplex()
        #         return n, nil
        #     }
        # }
        # # Do integer test first so we get 0x123 etc.
        # u, err := strconv.ParseUint(text, 0, 64) # will fail for -0; fixed below.
        # if err == nil {
        #     n.IsUint = true
        #     n.Uint64 = u
        # }
        # i, err := strconv.ParseInt(text, 0, 64)
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
        #     f, err := strconv.ParseFloat(text, 64)
        #     if err == nil {
        #         # If we parsed it as a float but it looks like an integer,
        #         # it's a huge number too large to fit in an int. Reject it.
        #         if !strings.ContainsAny(text, ".eEpP") {
        #             return nil, fmt.Errorf("integer overflow: %q", text)
        #         }
        #         n.IsFloat = true
        #         n.Float64 = f
        #         # If a floating-point extraction succeeded, extract the int if needed.
        #         if !n.IsInt && float64(int64(f)) == f {
        #             n.IsInt = true
        #             n.Int64 = int64(f)
        #         }
        #         if !n.IsUint && float64(uint64(f)) == f {
        #             n.IsUint = true
        #             n.Uint64 = uint64(f)
        #         }
        #     }
        # }
        # if !n.IsInt && !n.IsUint && !n.IsFloat {
        #     return nil, fmt.Errorf("illegal number syntax: %q", text)
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
            self._token[0] = self._lex.nextItem()
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
        self._token[0] = self._lex.nextItem()
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
        funcs: ta.Mapping[str, ta.Callable],
) -> ta.Mapping[str, Tree]:
    tree_set: dict[str, Tree] = {}
    t = Tree(name, funcs)
    t._text = text
    t.parse(text, left_delim, right_delim, tree_set, funcs)
    return tree_set


"""
# Parsing.

# ErrorContext returns a textual representation of the location of the node in the input text. The receiver is only used
# when the node does not have a pointer to the tree inside, which can occur in old code.
    def error_context(self, n: Node) (location, context str) {
        pos := int(n.Position())
        tree := n.tree()
        if tree == nil {
            tree = t
        }
        text := tree.text[:pos]
        byteNum := strings.LastIndex(text, "\n")
        if byteNum == -1 {
            byteNum = pos # On first line.
        } else {
            byteNum+=1 # After the newline.
            byteNum = pos - byteNum
        }
        lineNum := 1 + strings.Count(text, "\n")
        context = n.String()
        return fmt.Sprintf("%s:%d:%d", tree.parse_name, lineNum, byteNum), context
    }

# errorf formats the error and terminates processing.
def (t *Tree) errorf(format str, args ...any) {
    t.Root = nil
    format = fmt.Sprintf("template: %s:%d: %s", t.parse_name, t.token[0].line, format)
    panic(fmt.Errorf(format, args...))
}

# error terminates processing.
def (t *Tree) error(err error) {
    t.errorf("%s", err)
}

# expect consumes the next token and guarantees it has the required type.
def (t *Tree) expect(expected itemType, context str) Token {
    token := t.next_non_space()
    if token.typ != expected {
        t.unexpected(token, context)
    }
    return token
}

# expectOneOf consumes the next token and guarantees it has one of the required types.
def (t *Tree) expectOneOf(expected1, expected2 itemType, context str) Token {
    token := t.next_non_space()
    if token.typ != expected1 && token.typ != expected2 {
        t.unexpected(token, context)
    }
    return token
}

# unexpected complains about the token and terminates processing.
def (t *Tree) unexpected(token Token, context str) {
    if token.typ == itemError {
        extra := ""
        if t.action_line != 0 && t.action_line != token.line {
            extra = fmt.Sprintf(" in action started at %s:%d", t.parse_name, t.action_line)
            if strings.HasSuffix(token.val, " action") {
                extra = extra[len(" in action"):] # avoid "action in action"
            }
        }
        t.errorf("%s%s", token, extra)
    }
    t.errorf("unexpected %s in %s", token, context)
}

# recover is the handler that turns panics into returns from the top level of Parse.
def (t *Tree) recover(errp *error) {
    e := recover()
    if e != nil {
        if _, ok := e.(runtime.Error); ok {
            panic(e)
        }
        if t != nil {
            t.stopParse()
        }
        *errp = e.(error)
    }
}

# startParse initializes the parser, using the lexer.
def (t *Tree) startParse(funcs []map[str]any, lex *lexer, tree_set map[str]*Tree) {
    t.Root = nil
    t.lex = lex
    t.vars = []str{"$"}
    t.funcs = funcs
    t.tree_set = tree_set
    lex.options = lexOptions{
        emitComment: t.Mode&ParseComments != 0,
        breakOK:     !t.hasFunction("break"),
        continueOK:  !t.hasFunction("continue"),
    }
}

# stopParse terminates parsing.
def (t *Tree) stopParse() {
    t.lex = nil
    t.vars = nil
    t.funcs = nil
    t.tree_set = nil
}

# Parse parses the template definition string to construct a representation of
# the template for execution. If either action delimiter string is empty, the
# default ("{{" or "}}") is used. Embedded template definitions are added to
# the tree_set map.
def (t *Tree) Parse(text, left_delim, right_delim str, tree_set map[str]*Tree, funcs ...map[str]any) (tree *Tree, err error) {
    defer t.recover(&err)
    t.parse_name = t.Name
    lexer := lex(t.Name, text, left_delim, right_delim)
    t.startParse(funcs, lexer, tree_set)
    t.text = text
    t.parse()
    t.add()
    t.stopParse()
    return t, nil
}

# add adds tree to t.tree_set.
def (t *Tree) add() {
    tree := t.tree_set[t.Name]
    if tree == nil || is_empty_tree(tree.Root) {
        t.tree_set[t.Name] = t
        return
    }
    if !is_empty_tree(t.Root) {
        t.errorf("template: multiple definition of template %q", t.Name)
    }
}

# is_empty_tree reports whether this tree (node) is empty of everything but space or comments.
def is_empty_tree(n: Node) -> bool:
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

# parse is the top-level parser for a template, essentially the same
# as itemList except it also parses {{define}} actions.
# It runs to EOF.
def (t *Tree) parse() {
    t.Root = t.newList(t.peek().pos)
    for t.peek().typ != itemEOF {
        if t.peek().typ == itemLeftDelim {
            delim := t.next()
            if t.next_non_space().typ == itemDefine {
                newT := New("definition") # name will be updated once we know it.
                newT.text = t.text
                newT.Mode = t.Mode
                newT.parse_name = t.parse_name
                newT.startParse(t.funcs, t.lex, t.tree_set)
                newT.parseDefinition()
                continue
            }
            t.backup2(delim)
        }
        switch n := t.textOrAction(); n.Type() {
        case nodeEnd, nodeElse:
            t.errorf("unexpected %s", n)
        default:
            t.Root.append(n)
        }
    }
}

# parseDefinition parses a {{define}} ...  {{end}} template definition and
# installs the definition in t.tree_set. The "define" keyword has already
# been scanned.
def (t *Tree) parseDefinition() {
    const context = "define clause"
    name := t.expectOneOf(itemString, itemRawString, context)
    var err error
    t.Name, err = strconv.Unquote(name.val)
    if err != nil {
        t.error(err)
    }
    t.expect(itemRightDelim, context)
    var end Node
    t.Root, end = t.itemList()
    if end.Type() != nodeEnd {
        t.errorf("unexpected %s in %s", end, context)
    }
    t.add()
    t.stopParse()
}

# itemList:
#
#    textOrAction*
#
# Terminates at {{end}} or {{else}}, returned separately.
def (t *Tree) itemList() (list *ListNode, next Node) {
    list = t.newList(t.peek_non_space().pos)
    for t.peek_non_space().typ != itemEOF {
        n := t.textOrAction()
        switch n.Type() {
        case nodeEnd, nodeElse:
            return list, n
        }
        list.append(n)
    }
    t.errorf("unexpected EOF")
    return
}

# textOrAction:
#
#    text | comment | action
def (t *Tree) textOrAction() Node {
    switch token := t.next_non_space(); token.typ {
    case itemText:
        return t.newText(token.pos, token.val)
    case itemLeftDelim:
        t.action_line = token.line
        defer t.clearActionLine()
        return t.action()
    case itemComment:
        return t.newComment(token.pos, token.val)
    default:
        t.unexpected(token, "input")
    }
    return nil
}

def (t *Tree) clearActionLine() {
    t.action_line = 0
}

# Action:
#
#    control
#    command ("|" command)*
#
# Left delim is past. Now get actions.
# First word could be a keyword such as range.
def (t *Tree) action() (n Node) {
    switch token := t.next_non_space(); token.typ {
    case itemBlock:
        return t.blockControl()
    case itemBreak:
        return t.breakControl(token.pos, token.line)
    case itemContinue:
        return t.continueControl(token.pos, token.line)
    case itemElse:
        return t.elseControl()
    case itemEnd:
        return t.endControl()
    case itemIf:
        return t.ifControl()
    case itemRange:
        return t.rangeControl()
    case itemTemplate:
        return t.templateControl()
    case itemWith:
        return t.withControl()
    }
    t.backup()
    token := t.peek()
    # Do not pop variables; they persist until "end".
    return t.newAction(token.pos, token.line, t.pipeline("command", itemRightDelim))
}

# Break:
#
#    {{break}}
#
# Break keyword is past.
def (t *Tree) breakControl(pos Pos, line int) Node {
    if token := t.next_non_space(); token.typ != itemRightDelim {
        t.unexpected(token, "{{break}}")
    }
    if t.range_depth == 0 {
        t.errorf("{{break}} outside {{range}}")
    }
    return t.newBreak(pos, line)
}

# Continue:
#
#    {{continue}}
#
# Continue keyword is past.
def (t *Tree) continueControl(pos Pos, line int) Node {
    if token := t.next_non_space(); token.typ != itemRightDelim {
        t.unexpected(token, "{{continue}}")
    }
    if t.range_depth == 0 {
        t.errorf("{{continue}} outside {{range}}")
    }
    return t.newContinue(pos, line)
}

# Pipeline:
#
#    declarations? command ('|' command)*
def (t *Tree) pipeline(context str, end itemType) (pipe *PipeNode) {
    token := t.peek_non_space()
    pipe = t.newPipeline(token.pos, token.line, nil)
    # Are there declarations or assignments?
decls:
    if v := t.peek_non_space(); v.typ == itemVariable {
        t.next()
        # Since space is a token, we need 3-token look-ahead here in the worst case:
        # in "$x foo" we need to read "foo" (as opposed to ":=") to know that $x is an
        # argument variable rather than a declaration. So remember the token
        # adjacent to the variable so we can push it back if necessary.
        tokenAfterVariable := t.peek()
        next := t.peek_non_space()
        switch {
        case next.typ == itemAssign, next.typ == itemDeclare:
            pipe.IsAssign = next.typ == itemAssign
            t.next_non_space()
            pipe.Decl = append(pipe.Decl, t.newVariable(v.pos, v.val))
            t.vars = append(t.vars, v.val)
        case next.typ == itemChar && next.val == ",":
            t.next_non_space()
            pipe.Decl = append(pipe.Decl, t.newVariable(v.pos, v.val))
            t.vars = append(t.vars, v.val)
            if context == "range" && len(pipe.Decl) < 2 {
                switch t.peek_non_space().typ {
                case itemVariable, itemRightDelim, itemRightParen:
                    # second initialized variable in a range pipeline
                    goto decls
                default:
                    t.errorf("range can only initialize variables")
                }
            }
            t.errorf("too many declarations in %s", context)
        case tokenAfterVariable.typ == itemSpace:
            t.backup3(v, tokenAfterVariable)
        default:
            t.backup2(v)
        }
    }
    for {
        switch token := t.next_non_space(); token.typ {
        case end:
            # At this point, the pipeline is complete
            t.checkPipeline(pipe, context)
            return
        case itemBool, itemCharConstant, itemComplex, itemDot, itemField, itemIdentifier,
            itemNumber, itemNil, itemRawString, itemString, itemVariable, itemLeftParen:
            t.backup()
            pipe.append(t.command())
        default:
            t.unexpected(token, context)
        }
    }
}

def (t *Tree) checkPipeline(pipe *PipeNode, context str) {
    # Reject empty pipelines
    if len(pipe.Cmds) == 0 {
        t.errorf("missing value for %s", context)
    }
    # Only the first command of a pipeline can start with a non executable operand
    for i, c := range pipe.Cmds[1:] {
        switch c.Args[0].Type() {
        case NodeBool, NodeDot, NodeNil, NodeNumber, NodeString:
            # With A|B|C, pipeline stage 2 is B
            t.errorf("non executable command in pipeline stage %d", i+2)
        }
    }
}

def (t *Tree) parseControl(context str) (pos Pos, line int, pipe *PipeNode, list, elseList *ListNode) {
    defer t.popVars(len(t.vars))
    pipe = t.pipeline(context, itemRightDelim)
    if context == "range" {
        t.range_depth+=1
    }
    var next Node
    list, next = t.itemList()
    if context == "range" {
        t.range_depth-=1
    }
    switch next.Type() {
    case nodeEnd: #done
    case nodeElse:
        # Special case for "else if" and "else with".
        # If the "else" is followed immediately by an "if" or "with",
        # the elseControl will have left the "if" or "with" token pending. Treat
        #    {{if a}}_{{else if b}}_{{end}}
        #  {{with a}}_{{else with b}}_{{end}}
        # as
        #    {{if a}}_{{else}}{{if b}}_{{end}}{{end}}
        #  {{with a}}_{{else}}{{with b}}_{{end}}{{end}}.
        # To do this, parse the "if" or "with" as usual and stop at it {{end}};
        # the subsequent{{end}} is assumed. This technique works even for long if-else-if chains.
        if context == "if" && t.peek().typ == itemIf {
            t.next() # Consume the "if" token.
            elseList = t.newList(next.Position())
            elseList.append(t.ifControl())
        } else if context == "with" && t.peek().typ == itemWith {
            t.next()
            elseList = t.newList(next.Position())
            elseList.append(t.withControl())
        } else {
            elseList, next = t.itemList()
            if next.Type() != nodeEnd {
                t.errorf("expected end; found %s", next)
            }
        }
    }
    return pipe.Position(), pipe.Line, pipe, list, elseList
}

# If:
#
#    {{if pipeline}} itemList {{end}}
#    {{if pipeline}} itemList {{else}} itemList {{end}}
#
# If keyword is past.
def (t *Tree) ifControl() Node {
    return t.newIf(t.parseControl("if"))
}

# Range:
#
#    {{range pipeline}} itemList {{end}}
#    {{range pipeline}} itemList {{else}} itemList {{end}}
#
# Range keyword is past.
def (t *Tree) rangeControl() Node {
    r := t.newRange(t.parseControl("range"))
    return r
}

# With:
#
#    {{with pipeline}} itemList {{end}}
#    {{with pipeline}} itemList {{else}} itemList {{end}}
#
# If keyword is past.
def (t *Tree) withControl() Node {
    return t.newWith(t.parseControl("with"))
}

# End:
#
#    {{end}}
#
# End keyword is past.
def (t *Tree) endControl() Node {
    return t.newEnd(t.expect(itemRightDelim, "end").pos)
}

# Else:
#
#    {{else}}
#
# Else keyword is past.
def (t *Tree) elseControl() Node {
    peek := t.peek_non_space()
    # The "{{else if ... " and "{{else with ..." will be
    # treated as "{{else}}{{if ..." and "{{else}}{{with ...".
    # So return the else node here.
    if peek.typ == itemIf || peek.typ == itemWith {
        return t.newElse(peek.pos, peek.line)
    }
    token := t.expect(itemRightDelim, "else")
    return t.newElse(token.pos, token.line)
}

# Block:
#
#    {{block stringValue pipeline}}
#
# Block keyword is past.
# The name must be something that can evaluate to a string.
# The pipeline is mandatory.
def (t *Tree) blockControl() Node {
    const context = "block clause"

    token := t.next_non_space()
    name := t.parseTemplateName(token, context)
    pipe := t.pipeline(context, itemRightDelim)

    block := New(name) # name will be updated once we know it.
    block.text = t.text
    block.Mode = t.Mode
    block.parse_name = t.parse_name
    block.startParse(t.funcs, t.lex, t.tree_set)
    var end Node
    block.Root, end = block.itemList()
    if end.Type() != nodeEnd {
        t.errorf("unexpected %s in %s", end, context)
    }
    block.add()
    block.stopParse()

    return t.newTemplate(token.pos, token.line, name, pipe)
}

# Template:
#
#    {{template stringValue pipeline}}
#
# Template keyword is past. The name must be something that can evaluate to a string.
def (t *Tree) templateControl() Node {
    const context = "template clause"
    token := t.next_non_space()
    name := t.parseTemplateName(token, context)
    var pipe *PipeNode
    if t.next_non_space().typ != itemRightDelim {
        t.backup()
        # Do not pop variables; they persist until "end".
        pipe = t.pipeline(context, itemRightDelim)
    }
    return t.newTemplate(token.pos, token.line, name, pipe)
}

def (t *Tree) parseTemplateName(token Token, context str) (name str) {
    switch token.typ {
    case itemString, itemRawString:
        s, err := strconv.Unquote(token.val)
        if err != nil {
            t.error(err)
        }
        name = s
    default:
        t.unexpected(token, context)
    }
    return
}

# command:
#
#    operand (space operand)*
#
# space-separated arguments up to a pipeline character or right delimiter.
# we consume the pipe character but leave the right delim to terminate the action.
def (t *Tree) command() *CommandNode {
    cmd := t.newCommand(t.peek_non_space().pos)
    for {
        t.peek_non_space() # skip leading spaces.
        operand := t.operand()
        if operand != nil {
            cmd.append(operand)
        }
        switch token := t.next(); token.typ {
        case itemSpace:
            continue
        case itemRightDelim, itemRightParen:
            t.backup()
        case itemPipe:
            # nothing here; break loop below
        default:
            t.unexpected(token, "operand")
        }
        break
    }
    if len(cmd.Args) == 0 {
        t.errorf("empty command")
    }
    return cmd
}

# operand:
#
#    term .Field*
#
# An operand is a space-separated component of a command,
# a term possibly followed by field accesses.
# A nil return means the next item is not an operand.
def (t *Tree) operand() Node {
    node := t.term()
    if node == nil {
        return nil
    }
    if t.peek().typ == itemField {
        chain := t.newChain(t.peek().pos, node)
        for t.peek().typ == itemField {
            chain.Add(t.next().val)
        }
        # Compatibility with original API: If the term is of type NodeField
        # or NodeVariable, just put more fields on the original.
        # Otherwise, keep the Chain node.
        # Obvious parsing errors involving literal values are detected here.
        # More complex error cases will have to be handled at execution time.
        switch node.Type() {
        case NodeField:
            node = t.newField(chain.Position(), chain.String())
        case NodeVariable:
            node = t.newVariable(chain.Position(), chain.String())
        case NodeBool, NodeString, NodeNumber, NodeNil, NodeDot:
            t.errorf("unexpected . after term %q", node.String())
        default:
            node = chain
        }
    }
    return node
}

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
def (t *Tree) term() Node {
    switch token := t.next_non_space(); token.typ {
    case itemIdentifier:
        checkFunc := t.Mode&SkipFuncCheck == 0
        if checkFunc && !t.hasFunction(token.val) {
            t.errorf("function %q not defined", token.val)
        }
        return NewIdentifier(token.val).SetTree(t).SetPos(token.pos)
    case itemDot:
        return t.newDot(token.pos)
    case itemNil:
        return t.newNil(token.pos)
    case itemVariable:
        return t.useVar(token.pos, token.val)
    case itemField:
        return t.newField(token.pos, token.val)
    case itemBool:
        return t.newBool(token.pos, token.val == "true")
    case itemCharConstant, itemComplex, itemNumber:
        number, err := t.newNumber(token.pos, token.val, token.typ)
        if err != nil {
            t.error(err)
        }
        return number
    case itemLeftParen:
        return t.pipeline("parenthesized pipeline", itemRightParen)
    case itemString, itemRawString:
        s, err := strconv.Unquote(token.val)
        if err != nil {
            t.error(err)
        }
        return t.newString(token.pos, token.val, s)
    }
    t.backup()
    return nil
}

# hasFunction reports if a function name exists in the Tree's maps.
def (t *Tree) hasFunction(name str) bool {
    for _, funcMap := range t.funcs {
        if funcMap == nil {
            continue
        }
        if funcMap[name] != nil {
            return true
        }
    }
    return false
}

# popVars trims the variable list to the specified length
def (t *Tree) popVars(n int) {
    t.vars = t.vars[:n]
}

# useVar returns a node for a variable reference. It errors if the
# variable is not defined.
def (t *Tree) useVar(pos Pos, name str) Node {
    v := t.newVariable(pos, name)
    for _, varName := range t.vars {
        if varName == v.Ident[0] {
            return v
        }
    }
    t.errorf("undefined variable %q", v.Ident[0])
    return nil
}
"""
