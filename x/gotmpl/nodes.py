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
import dataclasses as dc
import enum
import typing as ta

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


@dc.dataclass()
class Node(abc.ABC):
    """
    A Node is an element in the parse tree. The interface is trivial. The interface contains an unexported method so
    that only types local to this package can satisfy it.
    """

    type: NodeType
    pos: Pos
    tree: 'parse.Tree'

    @abc.abstractmethod
    def copy(self) -> 'Node':
        raise NotImplementedError


# Nodes.


@dc.dataclass()
class ListNode(Node):
    # ListNode holds a sequence of nodes.

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

    text: str  # The text; may span newlines.

    def copy(self) -> Node:
        return TextNode(tree=self.tree, type=NodeType.TEXT, pos=self.pos, text=self.text)


@dc.dataclass()
class CommentNode(Node):
    # CommentNode holds a comment.

    text: str # Comment text.

    def copy(self) -> Node:
        return TextNode(tree=self.tree, type=NodeType.COMMENT, pos=self.pos, text=self.text)


@dc.dataclass()
class PipeNode(Node):
    # PipeNode holds a pipeline with optional declaration

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


@dc.dataclass()
class ActionNode(Node):
    # ActionNode holds an action (something bounded by delimiters). Control actions have their own nodes; ActionNode
    # represents simple ones such as field evaluations and parenthesized pipelines.

    line: int  # The line number in the input. Deprecated: Kept for compatibility.
    pipe: PipeNode  # The pipeline in the action.

    def copy(self) -> Node:
        return self.tree.new_action(self.pos, self.line, self.pipe.copy_pipe())


"""


@dc.dataclass()
class CommandNode(Node):
    # CommandNode holds a command (a pipeline inside an evaluating action).
    args: list[Node] # Arguments in lexical order: Identifier, field, or constant.

    func (c *CommandNode) append(arg Node) {
        c.Args = append(c.Args, arg)
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

    func (i *IdentifierNode) Copy() Node {
        return NewIdentifier(i.Ident).SetTree(i.tr).SetPos(i.Pos)
    }

# NewIdentifier returns a new [IdentifierNode] with the given identifier name.
func NewIdentifier(ident string) *IdentifierNode {
    return &IdentifierNode{NodeType: NodeIdentifier, Ident: ident}
}

# VariableNode holds a list of variable names, possibly with chained field
# accesses. The dollar sign is part of the (first) name.
type VariableNode struct {
    NodeType
    Pos
    tr    *Tree
    Ident []string # Variable name and fields in lexical order.

    func (v *VariableNode) Copy() Node {
        return &VariableNode{tr: v.tr, NodeType: NodeVariable, Pos: v.Pos, Ident: append([]string{}, v.Ident...)}
    }

# DotNode holds the special identifier '.'.
type DotNode struct {
    NodeType
    Pos
    tr *Tree

    func (d *DotNode) Type() NodeType {
        # Override method on embedded NodeType for API compatibility.
        # TODO: Not really a problem; could change API without effect but
        # api tool complains.
        return NodeDot
    }

    func (d *DotNode) Copy() Node {
        return d.tr.newDot(d.Pos)
    }

# NilNode holds the special identifier 'nil' representing an untyped nil constant.
type NilNode struct {
    NodeType
    Pos
    tr *Tree

    func (n *NilNode) Type() NodeType {
        # Override method on embedded NodeType for API compatibility.
        # TODO: Not really a problem; could change API without effect but
        # api tool complains.
        return NodeNil
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

    func (c *ChainNode) Copy() Node {
        return &ChainNode{tr: c.tr, NodeType: NodeChain, Pos: c.Pos, Node: c.Node, Field: append([]string{}, c.Field...)}
    }

# BoolNode holds a boolean constant.
type BoolNode struct {
    NodeType
    Pos
    tr   *Tree
    True bool # The value of the boolean constant.

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

    func (s *StringNode) Copy() Node {
        return s.tr.newString(s.Pos, s.Quoted, s.Text)
    }

# EndNode represents an {{end}} action.
# It does not appear in the final parse tree.
type EndNode struct {
    NodeType
    Pos
    tr *Tree

    func (e *EndNode) Copy() Node {
        return e.tr.newEnd(e.Pos)
    }

# ElseNode represents an {{else}} action. Does not appear in the final tree.
type ElseNode struct {
    NodeType
    Pos
    tr   *Tree
    Line int # The line number in the input. Deprecated: Kept for compatibility.

    func (e *ElseNode) Type() NodeType {
        return nodeElse
    }

    func (e *ElseNode) Copy() Node {
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

    func (i *IfNode) Copy() Node {
        return i.tr.newIf(i.Pos, i.Line, i.Pipe.CopyPipe(), i.List.CopyList(), i.ElseList.CopyList())
    }

# BreakNode represents a {{break}} action.
type BreakNode struct {
    tr *Tree
    NodeType
    Pos
    Line int

    func (b *BreakNode) Copy() Node                  { return b.tr.newBreak(b.Pos, b.Line) }

# ContinueNode represents a {{continue}} action.
type ContinueNode struct {
    tr *Tree
    NodeType
    Pos
    Line int

    func (c *ContinueNode) Copy() Node                  { return c.tr.newContinue(c.Pos, c.Line) }

# RangeNode represents a {{range}} action and its commands.
type RangeNode struct {
    BranchNode

    func (r *RangeNode) Copy() Node {
        return r.tr.newRange(r.Pos, r.Line, r.Pipe.CopyPipe(), r.List.CopyList(), r.ElseList.CopyList())
    }

# WithNode represents a {{with}} action and its commands.
type WithNode struct {
    BranchNode

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

    func (t *TemplateNode) Copy() Node {
        return t.tr.newTemplate(t.Pos, t.Line, t.Name, t.Pipe.CopyPipe())
    }
"""
