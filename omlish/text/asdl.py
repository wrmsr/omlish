"""
https://github.com/python/cpython/blob/21d2a9ab2f4dcbf1be462d3b7f7a231a46bc1cb7/Parser/asdl.py

-------------------------------------------------------------------------------

Parser for ASDL [1] definition files. Reads in an ASDL description and parses it into an AST that describes it.

The EBNF we're parsing here: Figure 1 of the paper [1]. Extended to support modules and attributes after a product.
Words starting with Capital letters are terminals. Literal tokens are in "double quotes". Others are non-terminals. Id
is either TokenId or ConstructorId.

module        ::= "module" Id "{" [definitions] "}"
definitions   ::= { TypeId "=" type }
type          ::= product | sum
product       ::= fields ["attributes" fields]
fields        ::= "(" { field, "," } field ")"
field         ::= TypeId ["?" | "*"] [Id]
sum           ::= constructor { "|" constructor } ["attributes" fields]
constructor   ::= ConstructorId [fields]

[1] "The Zephyr Abstract Syntax Description Language" by Wang, et. al. See http://asdl.sourceforge.net/
"""
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2024 Python Software Foundation; All Rights
# Reserved" are retained in Python alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import abc
import dataclasses as dc
import enum
import re
import typing as ta

from .. import cached


##


# The following classes define nodes into which the ASDL description is parsed. Note: this is a "meta-AST". ASDL files
# (such as Python.asdl) describe the AST structure used by a programming language. But ASDL files themselves need to be
# parsed. This module parses ASDL files and uses a simple AST to represent them. See the EBNF at the top of the file to
# understand the logical connection between the various node types.

class AST(abc.ABC):
    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class Field(AST):
    type: str
    name: str | None = None
    seq: bool = False
    opt: bool = False

    def __str__(self) -> str:
        if self.seq:
            extra = "*"
        elif self.opt:
            extra = "?"
        else:
            extra = ""

        return "{}{} {}".format(self.type, extra, self.name)

    def __repr__(self) -> str:
        if self.seq:
            extra = ", seq=True"
        elif self.opt:
            extra = ", opt=True"
        else:
            extra = ""
        if self.name is None:
            return 'Field({0.type}{1})'.format(self, extra)
        else:
            return 'Field({0.type}, {0.name}{1})'.format(self, extra)


@dc.dataclass(frozen=True)
class Constructor(AST):
    name: str
    fields: ta.Sequence[Field] | None = None

    def __repr__(self) -> str:
        return 'Constructor({0.name}, {0.fields})'.format(self)


@dc.dataclass(frozen=True)
class Sum(AST):
    types: ta.Sequence[Constructor]
    attributes: ta.Sequence[Field] | None = None

    def __repr__(self) -> str:
        if self.attributes:
            return 'Sum({0.types}, {0.attributes})'.format(self)
        else:
            return 'Sum({0.types})'.format(self)


@dc.dataclass(frozen=True)
class Product(AST):
    fields: ta.Sequence[Field]
    attributes: ta.Sequence[Field] | None = None

    def __repr__(self) -> str:
        if self.attributes:
            return 'Product({0.fields}, {0.attributes})'.format(self)
        else:
            return 'Product({0.fields})'.format(self)


@dc.dataclass(frozen=True)
class Type(AST):
    name: str
    value: ta.Union[Sum, Product]

    def __repr__(self) -> str:
        return 'Type({0.name}, {0.value})'.format(self)


@dc.dataclass(frozen=True)
class Module(AST):
    name: str
    dfns: ta.Sequence[Type]

    @cached.property
    def types(self) -> ta.Mapping[str, ta.Union[Sum, Product]]:
        return {type.name: type.value for type in self.dfns}

    def __repr__(self) -> str:
        return 'Module({0.name}, {0.dfns})'.format(self)


##


# A generic visitor for the meta-AST that describes ASDL. This can be used by emitters. Note that this visitor does not
# provide a generic visit method, so a subclass needs to define visit methods from visitModule to as deep as the
# interesting node.
# We also define a Check visitor that makes sure the parsed ASDL is well-formed.

class VisitorBase:
    """Generic tree visitor for ASTs."""

    def __init__(self) -> None:
        super().__init__()
        self.cache = {}

    def visit(self, obj, *args):
        klass = obj.__class__
        meth = self.cache.get(klass)
        if meth is None:
            methname = "visit" + klass.__name__
            meth = getattr(self, methname, None)
            self.cache[klass] = meth
        if meth:
            try:
                meth(obj, *args)
            except Exception as e:
                print("Error visiting %r: %s" % (obj, e))
                raise


##


class Check(VisitorBase):
    """
    A visitor that checks a parsed ASDL tree for correctness.

    Errors are printed and accumulated.
    """

    def __init__(self) -> None:
        super().__init__()
        self.cons = {}
        self.errors = 0
        self.types = {}

    def visitModule(self, mod: Module) -> None:
        for dfn in mod.dfns:
            self.visit(dfn)

    def visitType(self, type: Type) -> None:
        self.visit(type.value, str(type.name))

    def visitSum(self, sum: Sum, name: str) -> None:
        for t in sum.types:
            self.visit(t, name)

    def visitConstructor(self, cons: Constructor, name: str) -> None:
        key = str(cons.name)
        conflict = self.cons.get(key)
        if conflict is None:
            self.cons[key] = name
        else:
            print('Redefinition of constructor {}'.format(key))
            print('Defined in {} and {}'.format(conflict, name))
            self.errors += 1
        for f in cons.fields:
            self.visit(f, key)

    def visitField(self, field: Field, name: str) -> None:
        key = str(field.type)
        l = self.types.setdefault(key, [])
        l.append(name)

    def visitProduct(self, prod: Product, name: str) -> None:
        for f in prod.fields:
            self.visit(f, name)


BUILTIN_TYPES: ta.AbstractSet[str] = {
    'identifier',
    'string',
    'int',
    'constant',
}


def check(mod: Module) -> bool:
    """
    Check the parsed ASDL tree for correctness.

    Return True if success. For failure, the errors are printed out and False is returned.
    """

    v = Check()
    v.visit(mod)

    for t in v.types:
        if t not in mod.types and t not in BUILTIN_TYPES:
            v.errors += 1
            uses = ", ".join(v.types[t])
            print('Undefined type {}, used in {}'.format(t, uses))
    return not v.errors


##


# Types for describing tokens in an ASDL specification.
class TokenKind(enum.IntEnum):
    """TokenKind is provides a scope for enumerated token kinds."""

    CONSTRUCTOR_ID = enum.auto()
    TYPE_ID = enum.auto()
    EQUALS = enum.auto()
    COMMA = enum.auto()
    QUESTION = enum.auto()
    PIPE = enum.auto()
    ASTERISK = enum.auto()
    L_PAREN = enum.auto()
    R_PAREN = enum.auto()
    L_BRACE = enum.auto()
    R_BRACE = enum.auto()


OPERATOR_TABLE: ta.Mapping[str, TokenKind] = {
    '=': TokenKind.EQUALS,
    ',': TokenKind.COMMA,
    '?': TokenKind.QUESTION,
    '|': TokenKind.PIPE,
    '(': TokenKind.L_PAREN,
    ')': TokenKind.R_PAREN,
    '*': TokenKind.ASTERISK,
    '{': TokenKind.L_BRACE,
    '}': TokenKind.R_BRACE,
}


@dc.dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str
    lineno: int


class ASDLSyntaxError(Exception):
    def __init__(self, msg: str, lineno: int | None = None) -> None:
        super().__init__()
        self.msg = msg
        self.lineno = lineno or '<unknown>'

    def __str__(self) -> str:
        return 'Syntax error on line {0.lineno}: {0.msg}'.format(self)


def tokenize_asdl(buf: str) -> ta.Iterator[Token]:
    """Tokenize the given buffer. Yield Token objects."""

    for lineno, line in enumerate(buf.splitlines(), 1):
        for m in re.finditer(r'\s*(\w+|--.*|.)', line.strip()):
            c = m.group(1)
            if c[0].isalpha():
                # Some kind of identifier
                if c[0].isupper():
                    yield Token(TokenKind.CONSTRUCTOR_ID, c, lineno)
                else:
                    yield Token(TokenKind.TYPE_ID, c, lineno)
            elif c[:2] == '--':
                # Comment
                break
            else:
                # Operators
                try:
                    op_kind = OPERATOR_TABLE[c]
                except KeyError:
                    raise ASDLSyntaxError('Invalid operator %s' % c, lineno)
                yield Token(op_kind, c, lineno)


##


class ASDLParser:
    """
    Parser for ASDL files.

    Create, then call the parse method on a buffer containing ASDL. This is a simple recursive descent parser that uses
    tokenize_asdl for the lexing.
    """

    def __init__(self) -> None:
        super().__init__()
        self._tokenizer = None
        self.cur_token = None

    def parse(self, buf: str) -> Module:
        """Parse the ASDL in the buffer and return an AST with a Module root."""

        self._tokenizer = tokenize_asdl(buf)
        self._advance()
        return self._parse_module()

    def _parse_module(self) -> Module:
        if self._at_keyword('module'):
            self._advance()
        else:
            raise ASDLSyntaxError('Expected "module" (found {})'.format(self.cur_token.value), self.cur_token.lineno)
        name = self._match(self._id_kinds)
        self._match(TokenKind.L_BRACE)
        defs = self._parse_definitions()
        self._match(TokenKind.R_BRACE)
        return Module(name, defs)

    def _parse_definitions(self) -> ta.Sequence[Type]:
        defs = []
        while self.cur_token.kind == TokenKind.TYPE_ID:
            typename = self._advance()
            self._match(TokenKind.EQUALS)
            type = self._parse_type()
            defs.append(Type(typename, type))
        return defs

    def _parse_type(self) -> Sum | Product:
        if self.cur_token.kind == TokenKind.L_PAREN:
            # If we see a (, it's a product
            return self._parse_product()
        else:
            # Otherwise it's a sum. Look for ConstructorId
            sumlist = [Constructor(self._match(TokenKind.CONSTRUCTOR_ID), self._parse_optional_fields())]
            while self.cur_token.kind == TokenKind.PIPE:
                # More constructors
                self._advance()
                sumlist.append(Constructor(
                    self._match(TokenKind.CONSTRUCTOR_ID),
                    self._parse_optional_fields()),
                )
            return Sum(sumlist, self._parse_optional_attributes())

    def _parse_product(self) -> Product:
        return Product(self._parse_fields(), self._parse_optional_attributes())

    def _parse_fields(self) -> ta.Sequence[Field]:
        fields = []
        self._match(TokenKind.L_PAREN)
        while self.cur_token.kind == TokenKind.TYPE_ID:
            typename = self._advance()
            is_seq, is_opt = self._parse_optional_field_quantifier()
            id = self._advance() if self.cur_token.kind in self._id_kinds else None
            fields.append(Field(typename, id, seq=is_seq, opt=is_opt))
            if self.cur_token.kind == TokenKind.R_PAREN:
                break
            elif self.cur_token.kind == TokenKind.COMMA:
                self._advance()
        self._match(TokenKind.R_PAREN)
        return fields

    def _parse_optional_fields(self) -> ta.Sequence[Field] | None:
        if self.cur_token.kind == TokenKind.L_PAREN:
            return self._parse_fields()
        else:
            return None

    def _parse_optional_attributes(self) -> ta.Sequence[Field] | None:
        if self._at_keyword('attributes'):
            self._advance()
            return self._parse_fields()
        else:
            return None

    def _parse_optional_field_quantifier(self) -> tuple[bool, bool]:  # (seq, opt)
        is_seq, is_opt = False, False
        if self.cur_token.kind == TokenKind.ASTERISK:
            is_seq = True
            self._advance()
        elif self.cur_token.kind == TokenKind.QUESTION:
            is_opt = True
            self._advance()
        return is_seq, is_opt

    def _advance(self) -> str | None:
        """Return the value of the current token and read the next one into self.cur_token."""

        cur_val = None if self.cur_token is None else self.cur_token.value
        try:
            self.cur_token = next(self._tokenizer)
        except StopIteration:
            self.cur_token = None
        return cur_val

    _id_kinds = (TokenKind.CONSTRUCTOR_ID, TokenKind.TYPE_ID)

    def _match(self, kind: TokenKind | tuple[TokenKind, ...]) -> str:
        """The 'match' primitive of RD parsers.

        * Verifies that the current token is of the given kind (kind can be a tuple, in which the kind must match one of
          its members).
        * Returns the value of the current token
        * Reads in the next token
        """

        if isinstance(kind, tuple) and self.cur_token.kind in kind or self.cur_token.kind == kind:
            value = self.cur_token.value
            self._advance()
            return value
        else:
            raise ASDLSyntaxError(
                'Unmatched {} (found {})'.format(kind, self.cur_token.kind),
                self.cur_token.lineno,
            )

    def _at_keyword(self, keyword: str) -> bool:
        return self.cur_token.kind == TokenKind.TYPE_ID and self.cur_token.value == keyword


##


FlatFieldArity: ta.TypeAlias = ta.Literal[1, '?', '*']


@dc.dataclass(frozen=True)
class FlatField:
    name: str
    type: str
    n: FlatFieldArity = 1


@dc.dataclass(frozen=True)
class FlatNode(abc.ABC):
    name: str
    fields: ta.Sequence[FlatField] = dc.field(default=(), kw_only=True)
    attributes: ta.Sequence[FlatField] = dc.field(default=(), kw_only=True)


@dc.dataclass(frozen=True)
class FlatSum(FlatNode):
    constructors: ta.Sequence[str] = dc.field(default=(), kw_only=True)


@dc.dataclass(frozen=True)
class FlatProduct(FlatNode):
    pass


@dc.dataclass(frozen=True)
class FlatConstructor(FlatNode):
    sum: str = dc.field(kw_only=True)


def flatten(mod: Module) -> ta.Mapping[str, FlatNode]:
    lst: list[FlatNode] = []

    def mk_field(af: Field) -> FlatField:
        return FlatField(
            af.name,
            af.type,
            n='*' if af.seq else '?' if af.opt else 1,
        )

    def mk_fields(afs: ta.Iterable[Field] | None) -> ta.Sequence[FlatField]:
        return list(map(mk_field, afs or []))

    for ty in mod.dfns:
        v = ty.value

        if isinstance(v, Sum):
            lst.append(FlatSum(
                ty.name,
                attributes=mk_fields(v.attributes),
                constructors=[c.name for c in v.types],
            ))

            for c in v.types:
                lst.append(FlatConstructor(
                    c.name,
                    fields=mk_fields(c.fields),
                    sum=ty.name,
                ))

        elif isinstance(v, Product):
            lst.append(FlatProduct(
                ty.name,
                fields=mk_fields(v.fields),
                attributes=mk_fields(v.attributes),
            ))

        else:
            raise TypeError(v)

    #

    dct: dict[str, FlatNode] = {}

    for n in lst:
        if n.name in dct:
            raise KeyError(n.name)
        dct[n.name] = n

    return dct


#


def build_fields_info(
        nodes: ta.Mapping[str, FlatNode],
) -> ta.Mapping[str, ta.Mapping[str, tuple[str, FlatFieldArity]]]:
    dct: dict[str, dict[str, tuple[str, FlatFieldArity]]] = {}
    for n in nodes.values():
        cur = {}
        f: FlatField
        for f in [*n.fields, *n.attributes]:
            if f.type in BUILTIN_TYPES:
                continue
            if f.type not in nodes:
                raise KeyError(f.type)
            cur[f.name] = (f.type, f.n)
        if cur:
            dct[n.name] = cur
    return dct
