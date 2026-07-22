"""A fixture package exercising proxy_init's aliased and module-binding attr forms."""
from ...proxy import proxy_init


proxy_init(globals(), '.', [
    ('sub', 'alias'),
])

proxy_init(globals(), '.sub2', [
    (None, 'm2'),
])
