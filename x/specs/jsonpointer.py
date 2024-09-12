"""
https://www.rfc-editor.org/rfc/rfc6901

https://github.com/stefankoegl/python-json-pointer/blob/f3643addecf9dc66cb7bd120532a8373f19b1e23/jsonpointer.py
https://rosettacode.org/wiki/JSON_pointer
"""
import functools


class JsonPointer:
    def __init__(self, pstring):
        super().__init__()

        self.tokens = parse(pstring)

    def resolve(self, data):
        return functools.reduce(get_item, self.tokens, data)

    def encode(self):
        ret = ''
        for tok in self.tokens:
            ret = ret + '/' + tok.replace('~', '~0').replace('/', '~1')
        return ret

    def to_string(self):
        return self.encode()


def parse(pst):
    if pst == '':
        return []
    if pst[0] != '/':
        raise ValueError('Non-empty Json pointers must begin with /')
    return [a.replace('~1', '/').replace('~0', '~') for a in pst.split('/')][1:]


def get_item(obj, token):
    if isinstance(obj, list) and isinstance(token, str):
        return obj[int(token)]
    return obj[token]


if __name__ == '__main__':
    DOC = {
        'wiki': {
            'links': [
                'https://rosettacode.org/wiki/Rosetta_Code',
                'https://discord.com/channels/1011262808001880065',
            ],
        },
        '': 'Rosetta',
        ' ': 'Code',
        'g/h': 'chrestomathy',
        'i~j': 'site',
        'abc': ['is', 'a'],
        'def': {'': 'programming'},
    }

    EXAMPLES = [
        '',
        '/',
        '/ ',
        '/abc',
        '/def/',
        '/g~1h',
        '/i~0j',
        '/wiki/links/0',
        '/wiki/links/1',
        '/wiki/links/2',
        '/wiki/name',
        '/no/such/thing',
        'bad/pointer',
    ]

    for exa in EXAMPLES:
        try:
            pointer = JsonPointer(exa)
            result = pointer.resolve(DOC)
            print(f'"{exa}" -> "{result}"')
        except (ValueError, IndexError, KeyError) as error:
            print(f'Error: {exa} does not exist: {error}')
