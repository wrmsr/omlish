"""
~ https://github.com/grantjenks/python-diskcache/
- https://github.com/tinygrad/tinygrad/blob/7f642aa7ed8c2a47c7d1101b28e73db42c6c9285/tinygrad/helpers.py#L224 lol

--

DEFAULT_SETTINGS = {
    'statistics': 0,  # False
    'tag_index': 0,  # False
    'eviction_policy': 'least-recently-stored',
    'size_limit': 2**30,  # 1gb
    'cull_limit': 10,
    'sqlite_auto_vacuum': 1,  # FULL
    'sqlite_cache_size': 2**13,  # 8,192 pages
    'sqlite_journal_mode': 'wal',
    'sqlite_mmap_size': 2**26,  # 64mb
    'sqlite_synchronous': 1,  # NORMAL
    'disk_min_file_size': 2**15,  # 32kb
    'disk_pickle_protocol': pickle.HIGHEST_PROTOCOL,
}

CREATE TABLE IF NOT EXISTS Cache (
  rowid INTEGER PRIMARY KEY,
  key BLOB,
  raw INTEGER,
  store_time REAL,
  expire_time REAL,
  access_time REAL,
  access_count INTEGER DEFAULT 0,
  tag BLOB,
  size INTEGER DEFAULT 0,
  mode INTEGER DEFAULT 0,
  filename TEXT,
  value BLOB
)

class Cache:
    def directory(self):
    def timeout(self):
    def disk(self):
    def _con(self):
    def _sql(self):
    def _sql_retry(self):
    def transact(self, retry=False):
    def _transact(self, retry=False, filename=None):
    def set(self, key, value, expire=None, read=False, tag=None, retry=False):
    def __setitem__(self, key, value):
    def _row_update(self, rowid, now, columns):
    def _row_insert(self, key, raw, now, columns):
    def _cull(self, now, sql, cleanup, limit=None):
    def touch(self, key, expire=None, retry=False):
    def add(self, key, value, expire=None, read=False, tag=None, retry=False):
    def incr(self, key, delta=1, default=0, retry=False):
    def decr(self, key, delta=1, default=0, retry=False):
    def get(
        self,
        key,
        default=None,
        read=False,
        expire_time=False,
        tag=False,
        retry=False,
    ):
    def __getitem__(self, key):
    def read(self, key, retry=False):
    def __contains__(self, key):
    def pop(
        self, key, default=None, expire_time=False, tag=False, retry=False
    ):
    def __delitem__(self, key, retry=True):
    def delete(self, key, retry=False):
    def push(
        self,
        value,
        prefix=None,
        side='back',
        expire=None,
        read=False,
        tag=None,
        retry=False,
    ):
    def pull(
        self,
        prefix=None,
        default=(None, None),
        side='front',
        expire_time=False,
        tag=False,
        retry=False,
    ):
    def peek(
        self,
        prefix=None,
        default=(None, None),
        side='front',
        expire_time=False,
        tag=False,
        retry=False,
    ):
    def peekitem(self, last=True, expire_time=False, tag=False, retry=False):
    def memoize(
        self, name=None, typed=False, expire=None, tag=None, ignore=()
    ):
    def check(self, fix=False, retry=False):
    def create_tag_index(self):
    def drop_tag_index(self):
    def evict(self, tag, retry=False):
    def expire(self, now=None, retry=False):
    def cull(self, retry=False):
    def clear(self, retry=False):
    def _select_delete(
        self, select, args, row_index=0, arg_index=0, retry=False
    ):
    def iterkeys(self, reverse=False):
    def _iter(self, ascending=True):
    def __iter__(self):
    def __reversed__(self):
    def stats(self, enable=True, reset=False):
    def volume(self):
    def close(self):
    def __enter__(self):
    def __exit__(self, *exception):
    def __len__(self):
    def __getstate__(self):
    def __setstate__(self, state):
    def reset(self, key, value=ENOVAL, update=True):

"""
