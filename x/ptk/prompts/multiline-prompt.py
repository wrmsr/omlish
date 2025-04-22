#!/usr/bin/env python
"""
Demonstration of how the input can be indented.
"""
from omdev import ptk


if __name__ == '__main__':
    answer = ptk.prompt(
        'Give me some input: (ESCAPE followed by ENTER to accept)\n > ',
        multiline=True,
    )
    print(f'You said: {answer}')
