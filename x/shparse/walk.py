# Copyright (c) 2016, Daniel Martí. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#   products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
r"""
import functools
import typng as ta

from omlish import lnag


##


# walk traverses a syntax tree in depth-first order: It starts by calling
# f(node); node must not be nil. If f returns true, Walk invokes f
# recursively for each of the non-nil children of node, followed by
# f(nil).
def walk(node: Node, f: ta.Callable[[Node | None], bool]) -> None:
    if not f(node):
        return

    defers: list[ta.Callable[[], None] = []

    if isinstance(node, File):
        walk_list(node.Stmts, f)
        walk_comments(node.Last, f)
    elif isinstance(node, (Comment, Stmt)):
        for c in node.comments:
            if not node.end().after(c.pos()):
                defers.append(functools.partial(walk, c, f))
                break
            walk(c, f)
        if node.cmd is not None:
            walk(node.cmd, f)
        walk_list(node.redirs, f)
    elif isinstance(node, Assign):
        walk_nilable(node.name, f)
        walk_nilable(node.value, f)
        walk_nilable(node.index, f)
        walk_nilable(node.array, f)
    elif isinstance(node, Redirect):
        walk_nilable(node.n, f)
        walk(node.word, f)
        walk_nilable(node.hdoc, f)
    elif isinstance(node, CallExpr):
        walk_list(node.assigns, f)
        walk_list(node.args, f)
    elif isinstance(node, Subshell):
        walk_list(node.stmts, f)
        walk_comments(node.Last, f)
    elif isinstance(node, Block):
        walk_list(node.stmts, f)
        walk_comments(node.Last, f)
    elif isinstance(node, IfClause):
        walk_list(node.cond, f)
        walk_comments(node.cond_last, f)
        walk_list(node.then, f)
        walk_comments(node.then_last, f)
        walk_nilable(node.else_, f)
    elif isinstance(node, WhileClause):
        walk_list(node.cond, f)
        walk_comments(node.cond_last, f)
        walk_list(node.do, f)
        walk_comments(node.do_last, f)
    elif isinstance(node, ForClause):
        walk(node.loop, f)
        walk_list(node.do, f)
        walk_comments(node.do_last, f)
    elif isinstance(node, WordIter):
        walk(node.name, f)
        walk_list(node.items, f)
    elif isinstance(node, CStyleLoop):
        walk_nilable(node.init, f)
        walk_nilable(node.cond, f)
        walk_nilable(node.post, f)
    elif isinstance(node, BinaryCmd):
        walk(node.x, f)
        walk(node.y, f)
    elif isinstance(node, FuncDecl):
        walk_nilable(node.name, f)
        walk_list(node.names, f)
        walk(node.body, f)
    elif isinstance(node, Word):
        walk_list(node.parts, f)
    elif isinstance(node, (Lit, SglQuoted, DblQuoted)):
        walk_list(node.parts, f)
    elif isinstance(node, CmdSubst):
        walk_list(node.stmts, f)
        walk_comments(node.last, f)
    elif isinstance(node, ParamExp):
        walk_nilable(node.flags, f)
        walk_nilable(node.param, f)
        walk_nilable(node.nested_param, f)
        walk_nilable(node.index, f)
        if node.slice is not None:
            walk_nilable(node.slice.offset, f)
            walk_nilable(node.slice.length, f)
        if node.repl is not None:
            walk_nilable(node.repl.orig, f)
            walk_nilable(node.repl.with, f)
        if node.exp is not None:
            walk_nilable(node.exp.word, f)
    elif isinstance(node, ArithmExp):
        walk(node.x, f)
    elif isinstance(node, ArithmCmd):
        walk(node.x, f)
    elif isinstance(node, BinaryArithm):
        walk(node.x, f)
        walk(node.y, f)
    elif isinstance(node, BinaryTest):
        walk(node.x, f)
        walk(node.y, f)
    elif isinstance(node, UnaryArithm):
        walk(node.x, f)
    elif isinstance(node, UnaryTest):
        walk(node.x, f)
    elif isinstance(node, ParenArithm):
        walk(node.x, f)
    elif isinstance(node, FlagsArithm):
        walk(node.flags, f)
        if node.x is not None:
            walk(node.x, f)
    elif isinstance(node, ParenTest):
        walk(node.x, f)
    elif isinstance(node, CaseClause):
        walk(node.word, f)
        walk_list(node.items, f)
        walk_comments(node.last, f)
    elif isinstance(node, CaseItem):
        for c in node.comments:
            if c.pos().after(node.pos()):
                defers.append(functools.partial(walk, c, f))
                break
            walk(c, f)
        walk_list(node.patterns, f)
        walk_list(node.stmts, f)
        walk_comments(node.last, f)
    elif isinstance(node, TestClause):
        walk(node.x, f)
    elif isinstance(node, DeclClause):
        walk_list(node.args, f)
    elif isinstance(node, ArrayExpr):
        walk_list(node.elems, f)
        walk_comments(node.last, f)
    elif isinstance(node, ArrayElem):
        for c in node.comments:
            if c.pos().after(node.pos()):
                defers.append(functools.partial(walk, c, f))
                break
            walk(c, f)
        walk_nilable(node.index, f)
        walk_nilable(node.value, f)
    elif isinstance(node, ExtGlob):
        walk(node.pattern, f)
    elif isinstance(node, ProcSubst):
        walk_list(node.stmts, f)
        walk_comments(node.last, f)
    elif isinstance(node, TimeClause):
        walk_nilable(node.stmt, f)
    elif isinstance(node, CoprocClause):
        walk_nilable(node.name, f)
        walk(node.stmt, f)
    elif isinstance(node, LetClause):
        walk_list(node.exprs, f)
    elif isinstance(node, TestDecl):
        walk(node.description, f)
        walk(node.body, f)
    default:
        raise TypeError(node)

    f(None)
    
    for defer in defers:
        defer()


class NilableNode(Node, lang.Abstract):
    Node

    # comparable # pointer nodes, which can be compared to nil


NilableNodeT = ta.TypeVar('NilableNodeT', bound=NilableNode)


def walk_nilable(node: NilableNodeT | None, f: ta.Callable[[Node], bool]) -> None:
    if node is not None:
        walk(node, f)


NodeT = ta.TypeVar('NodeT', bound=Node)


def walk_list(lst: ta.Sequence[NodeT], f: ta.Callable[[Node], bool]) -> None:
    for node in lst:
        walk(node, f)


def walk_comments(lst: ta.Sequence[Comment], f: ta.Callable[[Node], bool]) -> None:
    # Note that []Comment does not satisfy the generic constraint []Node.
    for n in lst:
        walk(n, f)


# DebugPrint prints the provided syntax tree, spanning multiple lines and with
# indentation. Can be useful to investigate the content of a syntax tree.

class DebugPrinter:
    out   io.Writer
    level int
    err   error

    def __init__(self, w io.Writer, node Node) error {
        p := debugPrinter{out: w}
        p.print(reflect.ValueOf(node))
        p.printf("\n")
        return p.err

    def printf(self, format string, args ...any) -> None:
        _, err := fmt.Fprintf(p.out, format, args...)
        if err != nil && p.err == nil {
            p.err = err

    def newline(self) -> None:
        p.printf("\n")
        for range p.level {
            p.printf(".  ")

    def print(self, x reflect.Value) -> None:
        switch x.Kind() {
        case reflect.Interface:
            if x.IsNil() {
                p.printf("nil")
                return
            p.print(x.Elem())
        case reflect.Pointer:
            if x.IsNil() {
                p.printf("nil")
                return
            p.printf("*")
            p.print(x.Elem())
        case reflect.Slice:
            p.printf("%s (len = %d) {", x.Type(), x.Len())
            if x.Len() > 0 {
                p.level++
                p.newline()
                for i := range x.Len() {
                    p.printf("%d: ", i)
                    p.print(x.Index(i))
                    if i == x.Len()-1 {
                        p.level--
                    p.newline()
            p.printf("}")

        case reflect.Struct:
            if v, ok := x.Interface().(Pos); ok {
                if v.IsRecovered() {
                    p.printf("<recovered>")
                    return
                p.printf("%v:%v", v.Line(), v.Col())
                return
            t := x.Type()
            p.printf("%s {", t)
            p.level++
            p.newline()
            for i := range t.NumField() {
                p.printf("%s: ", t.Field(i).Name)
                p.print(x.Field(i))
                if i == x.NumField()-1 {
                    p.level--
                p.newline()
            p.printf("}")
        default:
            if s, ok := x.Interface().(fmt.Stringer); ok && !x.IsZero() {
                p.printf("%#v (%s)", x.Interface(), s)
            else {
                p.printf("%#v", x.Interface())
"""  # noqa
