# Overview

Advanced collection types and utilities beyond the stdlib. Includes specialized maps, sets, caches, sorted collections,
persistent data structures, and collection manipulation utilities.

# Notable Collections

- **[cache](https://github.com/wrmsr/omlish/blob/master/omlish/collections/cache)** - Configurable LRU/LFU caches with
  TTL and size/weight limits. More flexible than `functools.lru_cache`.
- **[persistent](https://github.com/wrmsr/omlish/blob/master/omlish/collections/persistent)** - Persistent (immutable)
  data structures:
  - **[persistent](https://github.com/wrmsr/omlish/blob/master/omlish/collections/persistent/persistent.py)** -
    `PersistentMap` interface for immutable mappings.
  - **[treapmap](https://github.com/wrmsr/omlish/blob/master/omlish/collections/persistent/treapmap.py)** -
    `TreapMap`/`TreapDict` treap-backed persistent map implementation.
- **[sorted](https://github.com/wrmsr/omlish/blob/master/omlish/collections/sorted)** - Sorted collections:
  - **[sorted](https://github.com/wrmsr/omlish/blob/master/omlish/collections/sorted/sorted.py)** - `SortedCollection`,
    `SortedMapping` interfaces for value-sorted collections and key-sorted maps.
  - **[skiplist](https://github.com/wrmsr/omlish/blob/master/omlish/collections/sorted/skiplist.py)** -
    `SkipList`/`SkipListDict` skiplist-backed sorted collection implementation.
- **[kv](https://github.com/wrmsr/omlish/blob/master/omlish/collections/kv)** - Key-value store abstractions and
  implementations.
- **[identity](https://github.com/wrmsr/omlish/blob/master/omlish/collections/identity.py)** - Identity-keyed
  collections: `IdentitySet`, `IdentityKeyDict`, `IdentityWeakSet`, `IdentityWeakKeyDictionary`.
- **[hasheq](https://github.com/wrmsr/omlish/blob/master/omlish/collections/hasheq.py)** - `HashEqMap` dict with custom
  `__hash__`/`__eq__` implementations for keys.
- **[frozen](https://github.com/wrmsr/omlish/blob/master/omlish/collections/frozen.py)** - `FrozenDict`/`FrozenList`
  immutable wrappers with hash support.
- **[bimap](https://github.com/wrmsr/omlish/blob/master/omlish/collections/bimap.py)** - `BiMap` bidirectional map with
  inverse lookups.
- **[multimaps](https://github.com/wrmsr/omlish/blob/master/omlish/collections/multimaps.py)** - Maps with multiple
  values per key: `SequenceMultiMap`, `AbstractSetMultiMap`, `BiMultiMap`.
- **[mappings](https://github.com/wrmsr/omlish/blob/master/omlish/collections/mappings.py)** - Specialized mappings:
  - `TypeMap` - Map keyed by type with subclass lookups.
  - `DynamicTypeMap` - Type map with dynamic lookup via callable.
  - `MissingDict` - Dict with callable for missing keys.
  - `multikey_dict()` - Dict accessible by multiple key aliases.
- **[trie](https://github.com/wrmsr/omlish/blob/master/omlish/collections/trie.py)** - `Trie` prefix tree
  implementation.
- **[ordered](https://github.com/wrmsr/omlish/blob/master/omlish/collections/ordered.py)** - `OrderedSet` and
  `OrderedFrozenSet` for ordered unique collections.
- **[ranked](https://github.com/wrmsr/omlish/blob/master/omlish/collections/ranked.py)** - `RankedSeq` and
  `RankedSetSeq` for ranked/prioritized sequences.
- **[unmodifiable](https://github.com/wrmsr/omlish/blob/master/omlish/collections/unmodifiable.py)** - Unmodifiable
  wrappers: `UnmodifiableMapping`, `UnmodifiableSequence`, `UnmodifiableSet`.
- **[attrregistry](https://github.com/wrmsr/omlish/blob/master/omlish/collections/attrregistry.py)** - `AttrRegistry`
  for attribute-based registration and caching.

# Utilities

- **[coerce](https://github.com/wrmsr/omlish/blob/master/omlish/collections/coerce.py)** - Coercion functions for
  converting to immutable collection types: `seq()`, `abs_set()`, `map()`, `frozenset_()`, etc.
- **[utils](https://github.com/wrmsr/omlish/blob/master/omlish/collections/utils.py)** - Collection utilities:
  - `unique()` - Remove duplicates preserving order.
  - `partition()` - Split collections by predicate.
  - `make_map()` / `make_map_by()` - Build dicts from iterables.
  - `multi_map()` / `multi_map_by()` - Build multimaps from iterables.
  - `all_equal()` / `all_not_equal()` - Check element equality.
  - `indexes()` - Get indexes of elements matching predicate.
  - `key_cmp()` - Create comparison key functions.

# Example Usage

```python
from omlish import collections as col

# Persistent map (immutable)
m1 = col.new_treap_dict({'a': 1, 'b': 2})
m2 = m1.set('c', 3)  # m1 unchanged, m2 has new entry

# Sorted skiplist
sl = col.SkipList([3, 1, 4, 1, 5])  # Maintains sorted order

# Identity set (compares by id, not equality)
s = col.IdentitySet()
s.add([1, 2])  # Uses id([1, 2]), not [1, 2].__hash__()

# BiMap (bidirectional)
bm = col.make_bi_map({'a': 1, 'b': 2})
bm.inv[1]  # 'a'

# Coercion
col.seq([1, 2, 3])  # tuple[int, ...]
col.abs_set([1, 2, 3])  # frozenset[int]
