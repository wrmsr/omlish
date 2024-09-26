"""
https://github.com/golang/go/blob/3d33437c450aa74014ea1d41cd986b6ee6266984/src/text/template/parse/node.go
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
import abc
import enum
import typing as ta

from omlish import dataclasses as dc

from .lex import Pos


if ta.TYPE_CHECKING:
    from . import parse


class NodeType(enum.IntEnum):
    TEXT = enum.auto()        # Plain text.
    ACTION = enum.auto()      # A non-control action such as a field evaluation.
    BOOL = enum.auto()        # A boolean constant.
    CHAIN = enum.auto()       # A sequence of field accesses.
    COMMAND = enum.auto()     # An element of a pipeline.
    DOT = enum.auto()         # The cursor, dot.
    ELSE = enum.auto()        # An else action. Not added to tree.
    END = enum.auto()         # An end action. Not added to tree.
    FIELD = enum.auto()       # A field or method name.
    IDENTIFIER = enum.auto()  # An identifier; always a function name.
    IF = enum.auto()          # An if action.
    LIST = enum.auto()        # A list of Nodes.
    NIL = enum.auto()         # An untyped nil constant.
    NUMBER = enum.auto()      # A numerical constant.
    PIPE = enum.auto()        # A pipeline of commands.
    RANGE = enum.auto()       # A range action.
    STRING = enum.auto()      # A string constant.
    TEMPLATE = enum.auto()    # A template invocation action.
    VARIABLE = enum.auto()    # A $ variable.
    WITH = enum.auto()        # A with action.
    COMMENT = enum.auto()     # A comment.
    BREAK = enum.auto()       # A break action.
    CONTINUE = enum.auto()    # A continue action.


class Node(abc.ABC):
    """
    A Node is an element in the parse tree. The interface is trivial. The interface contains an unexported method so
    that only types local to this package can satisfy it.
    """

    @property
    @abc.abstractmethod
    def type(self) -> NodeType:
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self) -> 'Node':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def pos(self) -> Pos:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def tree(self) -> 'parse.Tree':
        raise NotImplementedError


# Nodes.


@dc.dataclass()
class ListNode(Node):
    # ListNode holds a sequence of nodes.

    type: NodeType = dc.xfield(override=True)
    pos: Pos = dc.xfield(override=True)
    tree: 'parse.Tree' = dc.xfield(override=True)

    nodes: list[Node] = dc.field(default_factory=list)

    def append(self, n: Node) -> None:
        self.nodes.append(n)

    def copy_list(self) -> 'ListNode':
        n = self.tree.new_list(self.pos)
        for node in self.nodes:
            n.append(node.copy())
        return n

    def copy(self) -> Node:
        return self.copy()


@dc.dataclass()
class TextNode(Node):
    # TextNode holds plain text.

    type: NodeType = dc.xfield(override=True)
    pos: Pos = dc.xfield(override=True)
    tree: 'parse.Tree' = dc.xfield(override=True)

    text: str  # The text; may span newlines.

    def copy(self) -> Node:
        return TextNode(tree=self.tree, type=NodeType.TEXT, pos=self.pos, text=self.text)


@dc.dataclass()
class CommentNode(Node):
    # CommentNode holds a comment.

    type: NodeType = dc.xfield(override=True)
    pos: Pos = dc.xfield(override=True)
    tree: 'parse.Tree' = dc.xfield(override=True)

    text: str # Comment text.

    def copy(self) -> Node:
        return TextNode(tree=self.tree, type=NodeType.COMMENT, pos=self.pos, text=self.text)


@dc.dataclass()
class PipeNode(Node):
    # PipeNode holds a pipeline with optional declaration

    type: NodeType = dc.xfield(override=True)
    pos: Pos = dc.xfield(override=True)
    tree: 'parse.Tree' = dc.xfield(override=True)

    line: int  # The line number in the input. Deprecated: Kept for compatibility.
    is_assign: bool  # The variables are being assigned, not declared.
    decl: list['VariableNode']  # Variables in lexical order.
    cmds: list['CommandNode']  # The commands in lexical order.

    def append(self, command: 'CommandNode') -> None:
        self.cmds.append(command)

    def copy_pipe(self) -> 'PipeNode':
        vars: list[VariableNode] = []
        for d in self.decl:
            vars.append(d.copy())
        n = self.tree.new_pipeline(self.pos, self.line, vars)
        n.is_assign = self.is_assign
        for c in self.cmds:
            n.append(c.copy())
        return n

    def copy(self) -> Node:
        return self.copy_pipe()


"""

# ActionNode holds an action (something bounded by delimiters).
# Control actions have their own nodes; ActionNode represents simple
# ones such as field evaluations and parenthesized pipelines.
type ActionNode struct {
    NodeType
    Pos
    tr   *Tree
    Line int       # The line number in the input. Deprecated: Kept for compatibility.
    Pipe *PipeNode # The pipeline in the action.
}

func (t *Tree) newAction(pos Pos, line int, pipe *PipeNode) *ActionNode {
    return &ActionNode{tr: t, NodeType: NodeAction, Pos: pos, Line: line, Pipe: pipe}
}

func (a *ActionNode) String() string {
    var sb strings.Builder
    a.writeTo(&sb)
    return sb.String()
}

func (a *ActionNode) writeTo(sb *strings.Builder) {
    sb.WriteString("{{")
    a.Pipe.writeTo(sb)
    sb.WriteString("}}")
}

func (a *ActionNode) tree() *Tree {
    return a.tr
}

func (a *ActionNode) Copy() Node {
    return a.tr.newAction(a.Pos, a.Line, a.Pipe.CopyPipe())
}

# CommandNode holds a command (a pipeline inside an evaluating action).
type CommandNode struct {
    NodeType
    Pos
    tr   *Tree
    Args []Node # Arguments in lexical order: Identifier, field, or constant.
}

func (t *Tree) newCommand(pos Pos) *CommandNode {
    return &CommandNode{tr: t, NodeType: NodeCommand, Pos: pos}
}

func (c *CommandNode) append(arg Node) {
    c.Args = append(c.Args, arg)
}

func (c *CommandNode) String() string {
    var sb strings.Builder
    c.writeTo(&sb)
    return sb.String()
}

func (c *CommandNode) writeTo(sb *strings.Builder) {
    for i, arg := range c.Args {
        if i > 0 {
            sb.WriteByte(' ')
        }
        if arg, ok := arg.(*PipeNode); ok {
            sb.WriteByte('(')
            arg.writeTo(sb)
            sb.WriteByte(')')
            continue
        }
        arg.writeTo(sb)
    }
}

func (c *CommandNode) tree() *Tree {
    return c.tr
}

func (c *CommandNode) Copy() Node {
    if c == nil {
        return c
    }
    n := c.tr.newCommand(c.Pos)
    for _, c := range c.Args {
        n.append(c.Copy())
    }
    return n
}

# IdentifierNode holds an identifier.
type IdentifierNode struct {
    NodeType
    Pos
    tr    *Tree
    Ident string # The identifier's name.
}

# NewIdentifier returns a new [IdentifierNode] with the given identifier name.
func NewIdentifier(ident string) *IdentifierNode {
    return &IdentifierNode{NodeType: NodeIdentifier, Ident: ident}
}

# SetPos sets the position. [NewIdentifier] is a public method so we can't modify its signature.
# Chained for convenience.
# TODO: fix one day?
func (i *IdentifierNode) SetPos(pos Pos) *IdentifierNode {
    i.Pos = pos
    return i
}

# SetTree sets the parent tree for the node. [NewIdentifier] is a public method so we can't modify its signature.
# Chained for convenience.
# TODO: fix one day?
func (i *IdentifierNode) SetTree(t *Tree) *IdentifierNode {
    i.tr = t
    return i
}

func (i *IdentifierNode) String() string {
    return i.Ident
}

func (i *IdentifierNode) writeTo(sb *strings.Builder) {
    sb.WriteString(i.String())
}

func (i *IdentifierNode) tree() *Tree {
    return i.tr
}

func (i *IdentifierNode) Copy() Node {
    return NewIdentifier(i.Ident).SetTree(i.tr).SetPos(i.Pos)
}

# VariableNode holds a list of variable names, possibly with chained field
# accesses. The dollar sign is part of the (first) name.
type VariableNode struct {
    NodeType
    Pos
    tr    *Tree
    Ident []string # Variable name and fields in lexical order.
}

func (t *Tree) newVariable(pos Pos, ident string) *VariableNode {
    return &VariableNode{tr: t, NodeType: NodeVariable, Pos: pos, Ident: strings.Split(ident, ".")}
}

func (v *VariableNode) String() string {
    var sb strings.Builder
    v.writeTo(&sb)
    return sb.String()
}

func (v *VariableNode) writeTo(sb *strings.Builder) {
    for i, id := range v.Ident {
        if i > 0 {
            sb.WriteByte('.')
        }
        sb.WriteString(id)
    }
}

func (v *VariableNode) tree() *Tree {
    return v.tr
}

func (v *VariableNode) Copy() Node {
    return &VariableNode{tr: v.tr, NodeType: NodeVariable, Pos: v.Pos, Ident: append([]string{}, v.Ident...)}
}

# DotNode holds the special identifier '.'.
type DotNode struct {
    NodeType
    Pos
    tr *Tree
}

func (t *Tree) newDot(pos Pos) *DotNode {
    return &DotNode{tr: t, NodeType: NodeDot, Pos: pos}
}

func (d *DotNode) Type() NodeType {
    # Override method on embedded NodeType for API compatibility.
    # TODO: Not really a problem; could change API without effect but
    # api tool complains.
    return NodeDot
}

func (d *DotNode) String() string {
    return "."
}

func (d *DotNode) writeTo(sb *strings.Builder) {
    sb.WriteString(d.String())
}

func (d *DotNode) tree() *Tree {
    return d.tr
}

func (d *DotNode) Copy() Node {
    return d.tr.newDot(d.Pos)
}

# NilNode holds the special identifier 'nil' representing an untyped nil constant.
type NilNode struct {
    NodeType
    Pos
    tr *Tree
}

func (t *Tree) newNil(pos Pos) *NilNode {
    return &NilNode{tr: t, NodeType: NodeNil, Pos: pos}
}

func (n *NilNode) Type() NodeType {
    # Override method on embedded NodeType for API compatibility.
    # TODO: Not really a problem; could change API without effect but
    # api tool complains.
    return NodeNil
}

func (n *NilNode) String() string {
    return "nil"
}

func (n *NilNode) writeTo(sb *strings.Builder) {
    sb.WriteString(n.String())
}

func (n *NilNode) tree() *Tree {
    return n.tr
}

func (n *NilNode) Copy() Node {
    return n.tr.newNil(n.Pos)
}

# FieldNode holds a field (identifier starting with '.').
# The names may be chained ('.x.y').
# The period is dropped from each ident.
type FieldNode struct {
    NodeType
    Pos
    tr    *Tree
    Ident []string # The identifiers in lexical order.
}

func (t *Tree) newField(pos Pos, ident string) *FieldNode {
    return &FieldNode{tr: t, NodeType: NodeField, Pos: pos, Ident: strings.Split(ident[1:], ".")} # [1:] to drop leading period
}

func (f *FieldNode) String() string {
    var sb strings.Builder
    f.writeTo(&sb)
    return sb.String()
}

func (f *FieldNode) writeTo(sb *strings.Builder) {
    for _, id := range f.Ident {
        sb.WriteByte('.')
        sb.WriteString(id)
    }
}

func (f *FieldNode) tree() *Tree {
    return f.tr
}

func (f *FieldNode) Copy() Node {
    return &FieldNode{tr: f.tr, NodeType: NodeField, Pos: f.Pos, Ident: append([]string{}, f.Ident...)}
}

# ChainNode holds a term followed by a chain of field accesses (identifier starting with '.').
# The names may be chained ('.x.y').
# The periods are dropped from each ident.
type ChainNode struct {
    NodeType
    Pos
    tr    *Tree
    Node  Node
    Field []string # The identifiers in lexical order.
}

func (t *Tree) newChain(pos Pos, node Node) *ChainNode {
    return &ChainNode{tr: t, NodeType: NodeChain, Pos: pos, Node: node}
}

# Add adds the named field (which should start with a period) to the end of the chain.
func (c *ChainNode) Add(field string) {
    if len(field) == 0 || field[0] != '.' {
        panic("no dot in field")
    }
    field = field[1:] # Remove leading dot.
    if field == "" {
        panic("empty field")
    }
    c.Field = append(c.Field, field)
}

func (c *ChainNode) String() string {
    var sb strings.Builder
    c.writeTo(&sb)
    return sb.String()
}

func (c *ChainNode) writeTo(sb *strings.Builder) {
    if _, ok := c.Node.(*PipeNode); ok {
        sb.WriteByte('(')
        c.Node.writeTo(sb)
        sb.WriteByte(')')
    } else {
        c.Node.writeTo(sb)
    }
    for _, field := range c.Field {
        sb.WriteByte('.')
        sb.WriteString(field)
    }
}

func (c *ChainNode) tree() *Tree {
    return c.tr
}

func (c *ChainNode) Copy() Node {
    return &ChainNode{tr: c.tr, NodeType: NodeChain, Pos: c.Pos, Node: c.Node, Field: append([]string{}, c.Field...)}
}

# BoolNode holds a boolean constant.
type BoolNode struct {
    NodeType
    Pos
    tr   *Tree
    True bool # The value of the boolean constant.
}

func (t *Tree) newBool(pos Pos, true bool) *BoolNode {
    return &BoolNode{tr: t, NodeType: NodeBool, Pos: pos, True: true}
}

func (b *BoolNode) String() string {
    if b.True {
        return "true"
    }
    return "false"
}

func (b *BoolNode) writeTo(sb *strings.Builder) {
    sb.WriteString(b.String())
}

func (b *BoolNode) tree() *Tree {
    return b.tr
}

func (b *BoolNode) Copy() Node {
    return b.tr.newBool(b.Pos, b.True)
}

# NumberNode holds a number: signed or unsigned integer, float, or complex.
# The value is parsed and stored under all the types that can represent the value.
# This simulates in a small amount of code the behavior of Go's ideal constants.
type NumberNode struct {
    NodeType
    Pos
    tr         *Tree
    IsInt      bool       # Number has an integral value.
    IsUint     bool       # Number has an unsigned integral value.
    IsFloat    bool       # Number has a floating-point value.
    IsComplex  bool       # Number is complex.
    Int64      int64      # The signed integer value.
    Uint64     uint64     # The unsigned integer value.
    Float64    float64    # The floating-point value.
    Complex128 complex128 # The complex value.
    Text       string     # The original textual representation from the input.
}

func (t *Tree) newNumber(pos Pos, text string, typ itemType) (*NumberNode, error) {
    n := &NumberNode{tr: t, NodeType: NodeNumber, Pos: pos, Text: text}
    switch typ {
    case itemCharConstant:
        rune, _, tail, err := strconv.UnquoteChar(text[1:], text[0])
        if err != nil {
            return nil, err
        }
        if tail != "'" {
            return nil, fmt.Errorf("malformed character constant: %s", text)
        }
        n.Int64 = int64(rune)
        n.IsInt = true
        n.Uint64 = uint64(rune)
        n.IsUint = true
        n.Float64 = float64(rune) # odd but those are the rules.
        n.IsFloat = true
        return n, nil
    case itemComplex:
        # fmt.Sscan can parse the pair, so let it do the work.
        if _, err := fmt.Sscan(text, &n.Complex128); err != nil {
            return nil, err
        }
        n.IsComplex = true
        n.simplifyComplex()
        return n, nil
    }
    # Imaginary constants can only be complex unless they are zero.
    if len(text) > 0 && text[len(text)-1] == 'i' {
        f, err := strconv.ParseFloat(text[:len(text)-1], 64)
        if err == nil {
            n.IsComplex = true
            n.Complex128 = complex(0, f)
            n.simplifyComplex()
            return n, nil
        }
    }
    # Do integer test first so we get 0x123 etc.
    u, err := strconv.ParseUint(text, 0, 64) # will fail for -0; fixed below.
    if err == nil {
        n.IsUint = true
        n.Uint64 = u
    }
    i, err := strconv.ParseInt(text, 0, 64)
    if err == nil {
        n.IsInt = true
        n.Int64 = i
        if i == 0 {
            n.IsUint = true # in case of -0.
            n.Uint64 = u
        }
    }
    # If an integer extraction succeeded, promote the float.
    if n.IsInt {
        n.IsFloat = true
        n.Float64 = float64(n.Int64)
    } else if n.IsUint {
        n.IsFloat = true
        n.Float64 = float64(n.Uint64)
    } else {
        f, err := strconv.ParseFloat(text, 64)
        if err == nil {
            # If we parsed it as a float but it looks like an integer,
            # it's a huge number too large to fit in an int. Reject it.
            if !strings.ContainsAny(text, ".eEpP") {
                return nil, fmt.Errorf("integer overflow: %q", text)
            }
            n.IsFloat = true
            n.Float64 = f
            # If a floating-point extraction succeeded, extract the int if needed.
            if !n.IsInt && float64(int64(f)) == f {
                n.IsInt = true
                n.Int64 = int64(f)
            }
            if !n.IsUint && float64(uint64(f)) == f {
                n.IsUint = true
                n.Uint64 = uint64(f)
            }
        }
    }
    if !n.IsInt && !n.IsUint && !n.IsFloat {
        return nil, fmt.Errorf("illegal number syntax: %q", text)
    }
    return n, nil
}

# simplifyComplex pulls out any other types that are represented by the complex number.
# These all require that the imaginary part be zero.
func (n *NumberNode) simplifyComplex() {
    n.IsFloat = imag(n.Complex128) == 0
    if n.IsFloat {
        n.Float64 = real(n.Complex128)
        n.IsInt = float64(int64(n.Float64)) == n.Float64
        if n.IsInt {
            n.Int64 = int64(n.Float64)
        }
        n.IsUint = float64(uint64(n.Float64)) == n.Float64
        if n.IsUint {
            n.Uint64 = uint64(n.Float64)
        }
    }
}

func (n *NumberNode) String() string {
    return n.Text
}

func (n *NumberNode) writeTo(sb *strings.Builder) {
    sb.WriteString(n.String())
}

func (n *NumberNode) tree() *Tree {
    return n.tr
}

func (n *NumberNode) Copy() Node {
    nn := new(NumberNode)
    *nn = *n # Easy, fast, correct.
    return nn
}

# StringNode holds a string constant. The value has been "unquoted".
type StringNode struct {
    NodeType
    Pos
    tr     *Tree
    Quoted string # The original text of the string, with quotes.
    Text   string # The string, after quote processing.
}

func (t *Tree) newString(pos Pos, orig, text string) *StringNode {
    return &StringNode{tr: t, NodeType: NodeString, Pos: pos, Quoted: orig, Text: text}
}

func (s *StringNode) String() string {
    return s.Quoted
}

func (s *StringNode) writeTo(sb *strings.Builder) {
    sb.WriteString(s.String())
}

func (s *StringNode) tree() *Tree {
    return s.tr
}

func (s *StringNode) Copy() Node {
    return s.tr.newString(s.Pos, s.Quoted, s.Text)
}

# endNode represents an {{end}} action.
# It does not appear in the final parse tree.
type endNode struct {
    NodeType
    Pos
    tr *Tree
}

func (t *Tree) newEnd(pos Pos) *endNode {
    return &endNode{tr: t, NodeType: nodeEnd, Pos: pos}
}

func (e *endNode) String() string {
    return "{{end}}"
}

func (e *endNode) writeTo(sb *strings.Builder) {
    sb.WriteString(e.String())
}

func (e *endNode) tree() *Tree {
    return e.tr
}

func (e *endNode) Copy() Node {
    return e.tr.newEnd(e.Pos)
}

# elseNode represents an {{else}} action. Does not appear in the final tree.
type elseNode struct {
    NodeType
    Pos
    tr   *Tree
    Line int # The line number in the input. Deprecated: Kept for compatibility.
}

func (t *Tree) newElse(pos Pos, line int) *elseNode {
    return &elseNode{tr: t, NodeType: nodeElse, Pos: pos, Line: line}
}

func (e *elseNode) Type() NodeType {
    return nodeElse
}

func (e *elseNode) String() string {
    return "{{else}}"
}

func (e *elseNode) writeTo(sb *strings.Builder) {
    sb.WriteString(e.String())
}

func (e *elseNode) tree() *Tree {
    return e.tr
}

func (e *elseNode) Copy() Node {
    return e.tr.newElse(e.Pos, e.Line)
}

# BranchNode is the common representation of if, range, and with.
type BranchNode struct {
    NodeType
    Pos
    tr       *Tree
    Line     int       # The line number in the input. Deprecated: Kept for compatibility.
    Pipe     *PipeNode # The pipeline to be evaluated.
    List     *ListNode # What to execute if the value is non-empty.
    ElseList *ListNode # What to execute if the value is empty (nil if absent).
}

func (b *BranchNode) String() string {
    var sb strings.Builder
    b.writeTo(&sb)
    return sb.String()
}

func (b *BranchNode) writeTo(sb *strings.Builder) {
    name := ""
    switch b.NodeType {
    case NodeIf:
        name = "if"
    case NodeRange:
        name = "range"
    case NodeWith:
        name = "with"
    default:
        panic("unknown branch type")
    }
    sb.WriteString("{{")
    sb.WriteString(name)
    sb.WriteByte(' ')
    b.Pipe.writeTo(sb)
    sb.WriteString("}}")
    b.List.writeTo(sb)
    if b.ElseList != nil {
        sb.WriteString("{{else}}")
        b.ElseList.writeTo(sb)
    }
    sb.WriteString("{{end}}")
}

func (b *BranchNode) tree() *Tree {
    return b.tr
}

func (b *BranchNode) Copy() Node {
    switch b.NodeType {
    case NodeIf:
        return b.tr.newIf(b.Pos, b.Line, b.Pipe, b.List, b.ElseList)
    case NodeRange:
        return b.tr.newRange(b.Pos, b.Line, b.Pipe, b.List, b.ElseList)
    case NodeWith:
        return b.tr.newWith(b.Pos, b.Line, b.Pipe, b.List, b.ElseList)
    default:
        panic("unknown branch type")
    }
}

# IfNode represents an {{if}} action and its commands.
type IfNode struct {
    BranchNode
}

func (t *Tree) newIf(pos Pos, line int, pipe *PipeNode, list, elseList *ListNode) *IfNode {
    return &IfNode{BranchNode{tr: t, NodeType: NodeIf, Pos: pos, Line: line, Pipe: pipe, List: list, ElseList: elseList}}
}

func (i *IfNode) Copy() Node {
    return i.tr.newIf(i.Pos, i.Line, i.Pipe.CopyPipe(), i.List.CopyList(), i.ElseList.CopyList())
}

# BreakNode represents a {{break}} action.
type BreakNode struct {
    tr *Tree
    NodeType
    Pos
    Line int
}

func (t *Tree) newBreak(pos Pos, line int) *BreakNode {
    return &BreakNode{tr: t, NodeType: NodeBreak, Pos: pos, Line: line}
}

func (b *BreakNode) Copy() Node                  { return b.tr.newBreak(b.Pos, b.Line) }
func (b *BreakNode) String() string              { return "{{break}}" }
func (b *BreakNode) tree() *Tree                 { return b.tr }
func (b *BreakNode) writeTo(sb *strings.Builder) { sb.WriteString("{{break}}") }

# ContinueNode represents a {{continue}} action.
type ContinueNode struct {
    tr *Tree
    NodeType
    Pos
    Line int
}

func (t *Tree) newContinue(pos Pos, line int) *ContinueNode {
    return &ContinueNode{tr: t, NodeType: NodeContinue, Pos: pos, Line: line}
}

func (c *ContinueNode) Copy() Node                  { return c.tr.newContinue(c.Pos, c.Line) }
func (c *ContinueNode) String() string              { return "{{continue}}" }
func (c *ContinueNode) tree() *Tree                 { return c.tr }
func (c *ContinueNode) writeTo(sb *strings.Builder) { sb.WriteString("{{continue}}") }

# RangeNode represents a {{range}} action and its commands.
type RangeNode struct {
    BranchNode
}

func (t *Tree) newRange(pos Pos, line int, pipe *PipeNode, list, elseList *ListNode) *RangeNode {
    return &RangeNode{BranchNode{tr: t, NodeType: NodeRange, Pos: pos, Line: line, Pipe: pipe, List: list, ElseList: elseList}}
}

func (r *RangeNode) Copy() Node {
    return r.tr.newRange(r.Pos, r.Line, r.Pipe.CopyPipe(), r.List.CopyList(), r.ElseList.CopyList())
}

# WithNode represents a {{with}} action and its commands.
type WithNode struct {
    BranchNode
}

func (t *Tree) newWith(pos Pos, line int, pipe *PipeNode, list, elseList *ListNode) *WithNode {
    return &WithNode{BranchNode{tr: t, NodeType: NodeWith, Pos: pos, Line: line, Pipe: pipe, List: list, ElseList: elseList}}
}

func (w *WithNode) Copy() Node {
    return w.tr.newWith(w.Pos, w.Line, w.Pipe.CopyPipe(), w.List.CopyList(), w.ElseList.CopyList())
}

# TemplateNode represents a {{template}} action.
type TemplateNode struct {
    NodeType
    Pos
    tr   *Tree
    Line int       # The line number in the input. Deprecated: Kept for compatibility.
    Name string    # The name of the template (unquoted).
    Pipe *PipeNode # The command to evaluate as dot for the template.
}

func (t *Tree) newTemplate(pos Pos, line int, name string, pipe *PipeNode) *TemplateNode {
    return &TemplateNode{tr: t, NodeType: NodeTemplate, Pos: pos, Line: line, Name: name, Pipe: pipe}
}

func (t *TemplateNode) String() string {
    var sb strings.Builder
    t.writeTo(&sb)
    return sb.String()
}

func (t *TemplateNode) writeTo(sb *strings.Builder) {
    sb.WriteString("{{template ")
    sb.WriteString(strconv.Quote(t.Name))
    if t.Pipe != nil {
        sb.WriteByte(' ')
        t.Pipe.writeTo(sb)
    }
    sb.WriteString("}}")
}

func (t *TemplateNode) tree() *Tree {
    return t.tr
}

func (t *TemplateNode) Copy() Node {
    return t.tr.newTemplate(t.Pos, t.Line, t.Name, t.Pipe.CopyPipe())
}
"""
