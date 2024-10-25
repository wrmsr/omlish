from .backends import DEFAULT_BACKED


##


dump = DEFAULT_BACKED.dump
dumps = DEFAULT_BACKED.dumps

load = DEFAULT_BACKED.load
loads = DEFAULT_BACKED.loads

dump_pretty = DEFAULT_BACKED.dump_pretty
dumps_pretty = DEFAULT_BACKED.dumps_pretty

dump_compact = DEFAULT_BACKED.dump_compact
dumps_compact = DEFAULT_BACKED.dumps_compact
