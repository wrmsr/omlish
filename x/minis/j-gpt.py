"""
https://rosettacode.org/wiki/Category:J
"""

import numpy as np


class Noun:
    def __init__(self, value):
        self.value = value


class Verb:
    def __init__(self, name):
        self.name = name


class Application:
    def __init__(self, verb, *args):
        self.verb = verb
        self.args = args


class Fork:
    def __init__(self, u, v, w):
        self.u = u
        self.v = v
        self.w = w


def tokenize(s):
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i].isdigit():
            num = ''
            while i < len(s) and s[i].isdigit():
                num += s[i]
                i += 1
            tokens.append(num)
        elif s[i] == '(' or s[i] == ')':
            tokens.append(s[i])
            i += 1
        elif s[i] in '+-*/%#':
            if s[i] == '+' and i + 1 < len(s) and s[i + 1] == '/':
                tokens.append('+/')
                i += 2
            else:
                tokens.append(s[i])
                i += 1
        else:
            raise ValueError(f'Unexpected character: {s[i]}')
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        else:
            return None

    def next(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        return self.parse_expr()

    def parse_expr(self):
        tok = self.peek()
        if tok == '(':
            fork = self.parse_fork()
            next_tok = self.peek()
            if next_tok is not None and next_tok.isdigit():
                arg = self.parse_noun()
                return Application(fork, arg)
            else:
                raise ValueError('Expected argument after fork')
        else:
            return self.parse_verb_app()

    def parse_fork(self):
        self.next()  # consume '('
        u = self.parse_verb()
        v = self.parse_verb()
        w = self.parse_verb()
        if self.next() != ')':
            raise ValueError("Expected ')'")
        return Fork(u, v, w)

    def parse_verb_app(self):
        tok = self.peek()
        if tok in ['+', '-', '*', '/', '%', '#', '+/']:
            verb = self.parse_verb()
            next_tok = self.peek()
            if next_tok is None:
                raise ValueError('Expected argument')
            elif next_tok.isdigit():
                arg = self.parse_noun()
                return Application(verb, arg)
            else:
                raise ValueError(f'Unexpected token: {next_tok}')
        elif tok.isdigit():
            left = self.parse_noun()
            tok = self.peek()
            if tok in ['+', '-', '*', '/', '%']:
                verb = self.parse_verb()
                right = self.parse_noun()
                return Application(verb, left, right)
            else:
                return left
        else:
            raise ValueError(f'Unexpected token: {tok}')

    def parse_verb(self):
        tok = self.next()
        if tok in ['+', '-', '*', '/', '%', '#', '+/']:
            return Verb(tok)
        else:
            raise ValueError(f'Expected verb, got: {tok}')

    def parse_noun(self):
        nums = []
        while True:
            tok = self.peek()
            if tok is not None and tok.isdigit():
                nums.append(int(self.next()))
            else:
                break
        if len(nums) == 1:
            return Noun(nums[0])
        else:
            return Noun(np.array(nums))


def evaluate(node, *args):
    if isinstance(node, Noun):
        return node.value
    elif isinstance(node, Verb):
        verb = node.name
        if len(args) == 1:
            arg = args[0]
            if verb == '#':
                return len(arg)
            elif verb == '+/':
                return np.sum(arg)
            else:
                raise ValueError(f'Unknown monadic verb: {verb}')
        elif len(args) == 2:
            arg1, arg2 = args
            if verb == '+':
                return arg1 + arg2
            elif verb == '-':
                return arg1 - arg2
            elif verb == '*':
                return arg1 * arg2
            elif verb == '/':
                return arg1 / arg2
            elif verb == '%':
                return arg1 / arg2
            else:
                raise ValueError(f'Unknown dyadic verb: {verb}')
        else:
            raise ValueError('Invalid number of arguments for verb')
    elif isinstance(node, Fork):
        y = args[0]
        left = evaluate(node.u, y)
        right = evaluate(node.w, y)
        return evaluate(node.v, left, right)
    elif isinstance(node, Application):
        verb = node.verb
        args = [evaluate(arg) for arg in node.args]
        return evaluate(verb, *args)
    else:
        raise ValueError('Unknown node type')


def run(s):
    tokens = tokenize(s)
    parser = Parser(tokens)
    ast = parser.parse()
    result = evaluate(ast)
    if isinstance(result, np.ndarray):
        print(result)
    elif isinstance(result, float) and result.is_integer():
        print(int(result))
    else:
        print(result)


if __name__ == '__main__':
    # Test cases
    run('+/ 1 2 3')  # Output: 6
    run('+/4 5 6')  # Output: 15
    run('# 1 2 3')  # Output: 3
    run('# 2 3 4')  # Output: 3
    run('6 % 3')  # Output: 2
    run('15 % 3')  # Output: 5
    run('(+/ % #) 4 5 6')  # Output: 5
    run('(+/ % #) 1 2 3')  # Output: 2
