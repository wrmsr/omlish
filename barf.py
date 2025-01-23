from omlish import lang

lang.proxy_init(globals(), 'math', [
    'isnan',
    ('pi', 'pix'),
])