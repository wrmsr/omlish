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

from omlish import check
from omlish import lang

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
    tree: ta.Optional['parse.Tree']

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

    text: str  # Comment text.

    def copy(self) -> Node:
        return TextNode(tree=self.tree, type=NodeType.COMMENT, pos=self.pos, text=self.text)


@dc.dataclass()
class PipeNode(Node):
    # PipeNode holds a pipeline with optional declaration

    line: int  # The line number in the input. Deprecated: Kept for compatibility.
    is_assign: bool = False  # The variables are being assigned, not declared.
    decl: list['VariableNode'] = dc.field(default_factory=list)  # Variables in lexical order.
    cmds: list['CommandNode'] = dc.field(default_factory=list)  # The commands in lexical order.

    def append(self, command: 'CommandNode') -> None:
        self.cmds.append(command)

    def copy_pipe(self) -> 'PipeNode':
        vars: list[VariableNode] = []  # noqa
        for d in self.decl:
            vars.append(check.isinstance(d.copy(), VariableNode))
        n = self.tree.new_pipeline(self.pos, self.line, vars)
        n.is_assign = self.is_assign
        for c in self.cmds:
            n.append(check.isinstance(c.copy(), CommandNode))
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


@dc.dataclass()
class CommandNode(Node):
    # CommandNode holds a command (a pipeline inside an evaluating action).

    args: list[Node] = dc.field(default_factory=list)  # Arguments in lexical order: Identifier, field, or constant.

    def append(self, arg: Node) -> None:
        self.args.append(arg)

    def copy(self) -> Node:
        n = self.tree.new_command(self.pos)
        for c in self.args:
            n.append(c.copy())
        return n


@dc.dataclass()
class IdentifierNode(Node):
    # IdentifierNode holds an identifier.

    ident: str  # The identifier's name.

    def set_pos(self, pos: Pos) -> 'IdentifierNode':
        # SetPos sets the position. [NewIdentifier] is a public method so we can't modify its signature. Chained for
        # convenience.
        # TODO: fix one day?
        self.pos = pos
        return self

    def set_tree(self, t: 'parse.Tree') -> 'IdentifierNode':
        # SetTree sets the parent tree for the node. [NewIdentifier] is a public method so we can't modify its
        # signature. Chained for convenience.
        # TODO: fix one day?
        self.tree = t
        return self

    def copy(self) -> Node:
        return new_identifier(self.ident).set_tree(self.tree).set_pos(self.pos)


# NewIdentifier returns a new [IdentifierNode] with the given identifier name.
def new_identifier(ident: str) -> IdentifierNode:
    return IdentifierNode(tree=None, pos=0, type=NodeType.IDENTIFIER, ident=ident)


@dc.dataclass()
class VariableNode(Node):
    # VariableNode holds a list of variable names, possibly with chained field accesses. The dollar sign is part of the
    # (first) name.

    ident: list[str]  # Variable name and fields in lexical order.

    def copy(self) -> Node:
        return VariableNode(tree=self.tree, type=NodeType.VARIABLE, pos=self.pos, ident=list(self.ident))


@dc.dataclass()
class DotNode(Node):
    # DotNode holds the special identifier '.'.

    # @property
    # def type(self) -> NodeType:
    #     # Override method on embedded NodeType for API compatibility.
    #     # TODO: Not really a problem; could change API without effect but api tool complains.
    #     return NodeType.DOT

    def copy(self) -> Node:
        return self.tree.new_dot(self.pos)


@dc.dataclass()
class NilNode(Node):
    # NilNode holds the special identifier 'nil' representing an untyped nil constant.

    # @property
    # def type(self) -> NodeType:
    #     # Override method on embedded NodeType for API compatibility.
    #     # TODO: Not really a problem; could change API without effect but api tool complains.
    #     return NodeType.NIL

    def copy(self) -> Node:
        return self.tree.new_nil(self.pos)


@dc.dataclass()
class FieldNode(Node):
    # FieldNode holds a field (identifier starting with '.'). The names may be chained ('.x.y'). The period is dropped
    # from each ident.

    ident: list[str] = dc.field(default_factory=list)  # The identifiers in lexical order.

    def copy(self) -> Node:
        return FieldNode(tree=self.tree, type=NodeType.FIELD, pos=self.pos, ident=list(self.ident))


@dc.dataclass()
class ChainNode(Node):
    # ChainNode holds a term followed by a chain of field accesses (identifier starting with '.'). The names may be
    # chained ('.x.y'). The periods are dropped from each ident.

    node: Node
    field: list[str] = dc.field(default_factory=list)  # The identifiers in lexical order.

    # Add adds the named field (which should start with a period) to the end of the chain.
    def add(self, field: str) -> None:
        if not field or field[0] != '.':
            raise ValueError('no dot in field')
        field = field[1:]  # Remove leading dot.
        if not field:
            raise ValueError('empty field')
        self.field.append(field)

    def copy(self) -> Node:
        return ChainNode(tree=self.tree, type=NodeType.CHAIN, pos=self.pos, node=self.node, field=list(self.field))


@dc.dataclass()
class BoolNode(Node):
    # BoolNode holds a boolean constant.

    is_true: bool  # The value of the boolean constant.

    def copy(self) -> Node:
        return self.tree.new_bool(self.pos, self.is_true)


@dc.dataclass()
class NumberNode(Node):
    # NumberNode holds a number: signed or unsigned integer, float, or complex. The value is parsed and stored under all
    # the types that can represent the value. This simulates in a small amount of code the behavior of Go's ideal
    # constants.

    text: str  # The original textual representation from the input.

    v: int | float | complex = 0

    def simplify(self) -> None:
        if isinstance(self.v, complex) and self.v.imag == 0:
            self.v = self.v.real
        if isinstance(self.v, float) and self.v.is_integer():
            self.v = int(self.v)

    def copy(self) -> Node:
        nn = NumberNode(**dc.asdict(self))
        return nn


@dc.dataclass()
class StringNode(Node):
    # StringNode holds a string constant. The value has been "unquoted".

    quoted: str  # The original text of the string, with quotes.
    text: str  # The string, after quote processing.

    def copy(self) -> Node:
        return self.tree.new_string(self.pos, self.quoted, self.text)


@dc.dataclass()
class EndNode(Node):
    # EndNode represents an {{end}} action. It does not appear in the final parse tree.

    def copy(self) -> Node:
        return self.tree.new_end(self.pos)


@dc.dataclass()
class ElseNode(Node):
    # ElseNode represents an {{else}} action. Does not appear in the final tree.

    line: int  # The line number in the input. Deprecated: Kept for compatibility.

    # @property
    # def type(self) -> NodeType:
    #     return NodeType.ELSE

    def copy(self) -> Node:
        return self.tree.new_else(self.pos, self.line)


@dc.dataclass()
class BranchNode(Node, lang.Abstract):
    # BranchNode is the common representation of if, range, and with.

    line: int  # The line number in the input. Deprecated: Kept for compatibility.
    pipe: PipeNode  # The pipeline to be evaluated.
    lst: ListNode  # What to execute if the value is non-empty.
    else_lst: ListNode  # What to execute if the value is empty (nil if absent).

    def copy(self) -> Node:
        if self.type == NodeType.IF:
            return self.tree.new_if(self.pos, self.line, self.pipe, self.lst, self.else_lst)
        elif self.type == NodeType.RANGE:
            return self.tree.new_range(self.pos, self.line, self.pipe, self.lst, self.else_lst)
        elif self.type == NodeType.WITH:
            return self.tree.new_with(self.pos, self.line, self.pipe, self.lst, self.else_lst)
        else:
            raise TypeError(self)


@dc.dataclass()
class IfNode(BranchNode):
    # IfNode represents an {{if}} action and its commands.

    def copy(self) -> Node:
        return self.tree.new_if(self.pos, self.line, self.pipe.copy_pipe(), self.lst.copy_list(), self.else_lst.copy_list())  # noqa


@dc.dataclass()
class BreakNode(Node):
    # BreakNode represents a {{break}} action.

    line: int

    def copy(self) -> Node:
        return self.tree.new_break(self.pos, self.line)


@dc.dataclass()
class ContinueNode(Node):
    # ContinueNode represents a {{continue}} action.

    line: int

    def copy(self) -> Node:
        return self.tree.new_continue(self.pos, self.line)


@dc.dataclass()
class RangeNode(BranchNode):
    # RangeNode represents a {{range}} action and its commands.

    def copy(self) -> Node:
        return self.tree.new_range(self.pos, self.line, self.pipe.copy_pipe(), self.lst.copy_list(), self.else_lst.copy_list())  # noqa


@dc.dataclass()
class WithNode(BranchNode):
    # WithNode represents a {{with}} action and its commands.

    def copy(self) -> Node:
        return self.tree.new_with(self.pos, self.line, self.pipe.copy_pipe(), self.lst.copy_list(), self.else_lst.copy_list())  # noqa


@dc.dataclass()
class TemplateNode(Node):
    # TemplateNode represents a {{template}} action.

    line: int  # The line number in the input. Deprecated: Kept for compatibility.
    name: str  # The name of the template (unquoted).
    pipe: PipeNode  # The command to evaluate as dot for the template.

    def copy(self) -> Node:
        return self.tree.new_template(self.pos, self.line, self.name, self.pipe.copy_pipe())
