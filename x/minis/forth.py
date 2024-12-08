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
        self.user_words = {}  # Dictionary for user-defined words
        self.defining_word = None  # Current word being defined

    def run(self, code):
        """Runs Forth code."""
        tokens = code.split()
        for token in tokens:
            self.process_token(token)

    def process_token(self, token):
        """Process a single token."""
        if self.defining_word == ':':
            self.defining_word = token
            self.user_words[self.defining_word] = []
        elif self.defining_word is not None:
            # Add tokens to the current definition until ';' is encountered
            if token == ";":
                self.defining_word = None
            else:
                self.user_words[self.defining_word].append(token)
        elif token == ":":
            # Begin defining a new word
            if self.defining_word is not None:
                raise ValueError("Cannot define a word inside another definition.")
            self.defining_word = ':'
        elif token.isdigit():  # If it's a number, push it onto the stack
            self.stack.append(int(token))
        elif token in self.words:  # If it's a built-in word, execute it
            self.words[token]()
        elif token in self.user_words:  # If it's a user-defined word, execute its definition
            self.run(" ".join(self.user_words[token]))
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

    # Example Forth code with a user-defined word
    code = """
    : square dup * ;
    5 square
    """
    print(f"Running code:\n{code}")
    interpreter.run(code)
    print(interpreter)
