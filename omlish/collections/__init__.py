# fmt: off
# ruff: noqa: I001
from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .attrregistry import (  # noqa
        AttrRegistry,

        AttrRegistryCache,
        SimpleAttrRegistryCache,
    )

    from .bimap import (  # noqa
        BiMap,

        make_bi_map,
    )

    from . import cache  # noqa

    from .coerce import (  # noqa
        abs_set,
        abs_set_of,
        abs_set_of_or_none,
        abs_set_or_none,
        frozenset_,
        frozenset_of,
        frozenset_of_or_none,
        frozenset_or_none,
        map,  # noqa
        map_of,
        map_of_or_none,
        map_or_none,
        opt_abs_set,
        opt_abs_set_of,
        opt_frozenset,
        opt_frozenset_of,
        opt_map,
        opt_map_of,
        opt_seq,
        opt_seq_of,
        seq,
        seq_of,
        seq_of_or_none,
        seq_or_none,
    )

    from .frozen import (  # noqa
        Frozen,
        FrozenDict,
        FrozenList,
        frozendict,
        frozenlist,
    )

    from .hasheq import (  # noqa
        HashEq,
        HashEqMap,
        HashEq_,
        hash_eq,
    )

    from .identity import (  # noqa
        IdentityKeyDict,
        IdentitySet,
        IdentityWeakKeyDictionary,
        IdentityWeakSet,
    )

    from . import kv  # noqa

    from .mappings import (  # noqa
        DynamicTypeMap,
        MissingDict,
        TypeMap,
        dict_factory,
        guarded_map_update,
        multikey_dict,
    )

    from .multimaps import (  # noqa
        MultiMap,

        SequenceMultiMap,
        AbstractSetMultiMap,

        BiMultiMap,
        InverseBiMultiMap,

        SequenceBiMultiMap,
        AbstractSetBiMultiMap,

        TupleBiMultiMap,
        seq_bi_multi_map,

        FrozensetBiMultiMap,
        abs_set_bi_multi_map,
    )

    from .ordered import (  # noqa
        OrderedFrozenSet,
        OrderedSet,
    )

    from .persistent.persistent import (  # noqa
        PersistentMap,
        PersistentMapping,
    )

    from .persistent.treapmap import (  # noqa
        TreapDict,
        TreapMap,
        new_treap_dict,
        new_treap_map,
    )

    from .ranked import (  # noqa
        RankedSeq,
        RankedSetSeq,
    )

    from .sorted.skiplist import (  # noqa
        SkipList,
        SkipListDict,
    )

    from .sorted.sorted import (  # noqa
        SortedCollection,
        SortedItems,
        SortedIter,
        SortedListDict,
        SortedMapping,
        SortedMutableMapping,
    )

    from .trie import (  # noqa
        Trie,
    )

    from .unmodifiable import (  # noqa
        Unmodifiable,
        UnmodifiableMapping,
        UnmodifiableSequence,
        UnmodifiableSet,
    )

    from .utils import (  # noqa
        PartitionResult,
        all_equal,
        all_not_equal,
        indexes,
        key_cmp,
        make_map,
        make_map_by,
        multi_map,
        multi_map_by,
        partition,
        unique,
    )
