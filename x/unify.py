"""
https://eli.thegreenplace.net/2018/unification/
https://github.com/eliben/code-for-blog/blob/main/2018/unif/unifier.py

https://github.com/pythological/unification

https://www.ericpfahl.com/from-pattern-matching-to-unification/
https://cs.stackexchange.com/questions/35280/can-someone-clarify-this-unification-algorithm
"""
import re


##


class Token:
    """A simple Token structure. Contains the token type, value and position."""
    def __init__(self, type, val, pos):
        super().__init__()
        self.type = type
        self.val = val
        self.pos = pos

    def __str__(self):
        return '%s(%s) at %s' % (self.type, self.val, self.pos)


class LexerError(Exception):
    """
    Lexer error exception.

        pos:
            Position in the input line where the error occurred.
    """
    def __init__(self, pos):
        super().__init__()
        self.pos = pos


class Lexer:
    """
    A simple regex-based lexer/tokenizer.

    See below for an example of usage.
    """
    def __init__(self, rules, skip_whitespace=True):
        """ Create a lexer.

            rules:
                A list of rules. Each rule is a `regex, type` pair, where `regex` is the regular expression used to
                recognize the token and `type` is the type of the token to return when it's recognized.

            skip_whitespace:
                If True, whitespace (\\s+) will be skipped and not reported by the lexer. Otherwise, you have to specify
                your rules for whitespace, or it will be flagged as an error.
        """
        super().__init__()
        # All the regexes are concatenated into a single one with named groups. Since the group names must be valid
        # Python identifiers, but the token types used by the user are arbitrary strings, we auto-generate the group
        # names and map them to token types.
        idx = 1
        regex_parts = []
        self.group_type = {}

        for regex, type in rules:
            groupname = 'GROUP%s' % idx
            regex_parts.append('(?P<%s>%s)' % (groupname, regex))
            self.group_type[groupname] = type
            idx += 1

        self.regex = re.compile('|'.join(regex_parts))
        self.skip_whitespace = skip_whitespace
        self.re_ws_skip = re.compile(r'\S')

    def input(self, buf):
        """Initialize the lexer with a buffer as input."""
        self.buf = buf
        self.pos = 0

    def token(self):
        """
        Return the next token (a Token object) found in the input buffer. None is returned if the end of the buffer was
        reached. In case of a lexing error (the current chunk of the buffer matches no rule), a LexerError is raised
        with the position of the error.
        """
        if self.pos >= len(self.buf):
            return None
        else:
            if self.skip_whitespace:
                m = self.re_ws_skip.search(self.buf, self.pos)

                if m:
                    self.pos = m.start()
                else:
                    return None

            m = self.regex.match(self.buf, self.pos)
            if m:
                groupname = m.lastgroup
                tok_type = self.group_type[groupname]
                tok = Token(tok_type, m.group(groupname), self.pos)
                self.pos = m.end()
                return tok

            # if we're here, no rule matched
            raise LexerError(self.pos)

    def tokens(self):
        """Returns an iterator to the tokens found in the buffer."""
        while 1:
            tok = self.token()
            if tok is None: break
            yield tok


##


class Term:
    pass


# In App, function names are always considered to be constants, not variables. This simplifies things and doesn't affect
# expressivity. We can always model variable functions by envisioning an apply(FUNCNAME, ... args ...).
class App(Term):
    def __init__(self, fname, args=()):
        super().__init__()
        self.fname = fname
        self.args = args

    def __str__(self):
        return '{0}({1})'.format(self.fname, ','.join(map(str, self.args)))

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.fname == other.fname and
            all(self.args[i] == other.args[i] for i in range(len(self.args)))
        )

    __repr__ = __str__


class Var(Term):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    __repr__ = __str__


class Const(Term):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    __repr__ = __str__


class ParseError(Exception):
    pass


def parse_term(s):
    """Parses a term from string s, returns a Term."""
    parser = TermParser(s)
    return parser.parse_term()


class TermParser:
    """Term parser.

    Use the top-level parse_term() instead of instantiating this class directly.
    """

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.cur_token = None
        lexrules = (
            (r'\d+', 'NUMBER'),
            (r'[a-zA-Z_]\w*', 'ID'),
            (r',', 'COMMA'),
            (r'\(', 'LP'),
            (r'\)', 'RP'),
        )
        self.lexer = Lexer(lexrules, skip_whitespace=True)
        self.lexer.input(text)
        self._get_next_token()

    def _get_next_token(self):
        try:
            self.cur_token = self.lexer.token()

            if self.cur_token is None:
                self.cur_token = Token(None, None, None)
        except LexerError as e:
            self._error('Lexer error at position %d' % e.pos)

    def _error(self, msg):
        raise ParseError(msg)

    def parse_term(self):
        if self.cur_token.type == 'NUMBER':
            term = Const(self.cur_token.val)
            # Consume the current token and return the Const term.
            self._get_next_token()
            return term
        elif self.cur_token.type == 'ID':
            # We have to look at the next token to distinguish between App and
            # Var.
            idtok = self.cur_token
            self._get_next_token()
            if self.cur_token.type == 'LP':
                if idtok.val.isupper():
                    self._error("Function names should be constant")
                self._get_next_token()
                args = []
                while True:
                    args.append(self.parse_term())
                    if self.cur_token.type == 'RP':
                        break
                    elif self.cur_token.type == 'COMMA':
                        # Consume the comma and continue to the next arg
                        self._get_next_token()
                    else:
                        self._error("Expected ',' or ')' in application")
                # Consume the ')'
                self._get_next_token()
                return App(fname=idtok.val, args=args)
            else:
                if idtok.val.isupper():
                    return Var(idtok.val)
                else:
                    return Const(idtok.val)


def occurs_check(v, term, subst):
    """Does the variable v occur anywhere inside term?

    Variables in term are looked up in subst and the check is applied
    recursively.
    """
    assert isinstance(v, Var)
    if v == term:
        return True
    elif isinstance(term, Var) and term.name in subst:
        return occurs_check(v, subst[term.name], subst)
    elif isinstance(term, App):
        return any(occurs_check(v, arg, subst) for arg in term.args)
    else:
        return False


def unify(x, y, subst):
    """Unifies term x and y with initial subst.

    Returns a subst (map of name->term) that unifies x and y, or None if
    they can't be unified. Pass subst={} if no subst are initially
    known. Note that {} means valid (but empty) subst.
    """
    if subst is None:
        return None
    elif x == y:
        return subst
    elif isinstance(x, Var):
        return unify_variable(x, y, subst)
    elif isinstance(y, Var):
        return unify_variable(y, x, subst)
    elif isinstance(x, App) and isinstance(y, App):
        if x.fname != y.fname or len(x.args) != len(y.args):
            return None
        else:
            for i in range(len(x.args)):
                subst = unify(x.args[i], y.args[i], subst)
            return subst
    else:
        return None


def apply_unifier(x, subst):
    """Applies the unifier subst to term x.

    Returns a term where all occurrences of variables bound in subst
    were replaced (recursively); on failure returns None.
    """
    if subst is None:
        return None
    elif len(subst) == 0:
        return x
    elif isinstance(x, Const):
        return x
    elif isinstance(x, Var):
        if x.name in subst:
            return apply_unifier(subst[x.name], subst)
        else:
            return x
    elif isinstance(x, App):
        newargs = [apply_unifier(arg, subst) for arg in x.args]
        return App(x.fname, newargs)
    else:
        return None


def unify_variable(v, x, subst):
    """Unifies variable v with term x, using subst.

    Returns updated subst or None on failure.
    """
    assert isinstance(v, Var)
    if v.name in subst:
        return unify(subst[v.name], x, subst)
    elif isinstance(x, Var) and x.name in subst:
        return unify(v, subst[x.name], subst)
    elif occurs_check(v, x, subst):
        return None
    else:
        # v is not yet in subst and can't simplify x. Extend subst.
        return {**subst, v.name: x}


if __name__ == '__main__':
    s1 = 'f(X,h(X),Y,g(Y))'
    s2 = 'f(g(Z),W,Z,X)'
    subst = unify(parse_term(s1), parse_term(s2), {})
    print(subst)

    print(apply_unifier(parse_term(s1), subst))
    print(apply_unifier(parse_term(s2), subst))

    # assert unify(parse_term('f(a, b, bar(t))'), parse_term('f(a, V, X)'), {}) == {'V': b, 'X': bar(t)}
    #
    # assert unify(parse_term('f(a, V, bar(D))'), parse_term('f(D, k, bar(a))'), {}) == {'D': a, 'V': k}
    # assert unify(parse_term('f(X, Y)'), parse_term('f(Z, g(X))'), {}) == {'X': Z, 'Y': g(X)}
    #
    # assert unify(parse_term('f(X, Y, X)'), parse_term('f(r, g(X), p)'), {}) is None
