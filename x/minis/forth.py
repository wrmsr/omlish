class ForthInterpreter:
    def __init__(self):
        self.stack = []  # The main stack
        self.words = {   # Built-in words (commands)
            '+': self.add,
            '-': self.sub,
            '*': self.mul,
            '/': self.div,
            'dup': self.dup,
            'drop': self.drop,
            'swap': self.swap,
            'over': self.over,
        }

    def run(self, code):
        """Runs Forth code."""
        tokens = code.split()
        for token in tokens:
            self.process_token(token)

    def process_token(self, token):
        """Process a single token."""
        if token.isdigit():  # If it's a number, push it onto the stack
            self.stack.append(int(token))
        elif token in self.words:  # If it's a known word, execute it
            self.words[token]()
        else:
            raise ValueError(f"Unknown token: {token}")

    # Built-in word implementations
    def add(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a + b)

    def sub(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a - b)

    def mul(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a * b)

    def div(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a // b)

    def dup(self):
        self.stack.append(self.stack[-1])

    def drop(self):
        self.stack.pop()

    def swap(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(b)
        self.stack.append(a)

    def over(self):
        self.stack.append(self.stack[-2])

    def __str__(self):
        """Returns the current state of the stack."""
        return f"Stack: {self.stack}"


# Example usage
if __name__ == "__main__":
    interpreter = ForthInterpreter()

    # Example Forth code
    code = "3 4 + 5 * dup -"
    print(f"Running code: {code}")
    interpreter.run(code)
    print(interpreter)
