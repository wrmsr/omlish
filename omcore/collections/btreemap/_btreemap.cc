// @om-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"

#include <cassert>
#include <cstddef>
#include <cstring>


#define _MODULE_NAME "_btreemap"
#define _PACKAGE_NAME "omcore.collections.btreemap"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME


static constexpr Py_ssize_t MAX_LEAF_LEN = 32;
static constexpr Py_ssize_t MAX_BRANCH_LEN = 32;


typedef struct BtreeNode BtreeNode;
typedef struct BtreeIter BtreeIter;


typedef struct btree_state {
    PyTypeObject *BtreeNodeType;
    PyTypeObject *BtreeIterType;
} btree_state;


static btree_state *get_btree_state(PyObject *module) {
    void *state = PyModule_GetState(module);
    assert(state != nullptr);
    return (btree_state *)state;
}


//
// BtreeNode
//

struct BtreeNode {
    PyObject_VAR_HEAD

    Py_ssize_t count;
    unsigned short len;
    unsigned char is_leaf;

    // One-element trailing array. The actual allocation has 2 * len PyObject* slots, arranged as:
    //
    //   leaf:   items[0:len] = keys, items[len:2*len] = values
    //   branch: items[0:len] = child max keys, items[len:2*len] = children
    //
    PyObject *items[1];
};


static inline Py_ssize_t node_slots(BtreeNode *n) {
    return 2 * (Py_ssize_t)n->len;
}


static inline PyObject **node_keys(BtreeNode *n) {
    return n->items;
}


static inline PyObject **node_second(BtreeNode *n) {
    return n->items + n->len;
}


static inline PyObject *node_key(BtreeNode *n, Py_ssize_t i) {
    return node_keys(n)[i];
}


static inline PyObject *node_max(BtreeNode *n) {
    return node_key(n, n->len - 1);
}


static inline PyObject *leaf_value(BtreeNode *n, Py_ssize_t i) {
    return node_second(n)[i];
}


static inline BtreeNode *branch_child(BtreeNode *n, Py_ssize_t i) {
    return (BtreeNode *)node_second(n)[i];
}


// GC protocol notes, relied on non-locally:
//
//  - Instances of heap types (PyType_FromSpec) own a strong reference to their type -- the Py_DECREF(tp) in the
//    deallocs pays it back -- so tp_traverse must Py_VISIT the type, or instance -> type -> module cycles are invisible
//    to GC and the types/module state leak on interpreter teardown.
//
//  - BtreeNode deliberately has no tp_clear, tuple-style. Nodes are immutable after construction and built bottom-up
//    from already-finished objects, so a pure-node reference cycle is unconstructible; any real cycle through a node
//    also passes through some mutable participant (a dict, a module, a BtreeIter, ...), and GC breaks the cycle
//    *there*, after which node refcounts fall and ordinary dealloc runs. Consequence: a live node is never observable
//    in a partially-cleared state, which is what licenses the absence of any "cleared node" defensive checks in
//    find/iteration below.

static int BtreeNode_traverse(BtreeNode *self, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(self));

    for (Py_ssize_t i = 0; i < node_slots(self); ++i) {
        Py_VISIT(self->items[i]);
    }

    return 0;
}


static void BtreeNode_dealloc(BtreeNode *self) {
    PyTypeObject *tp = Py_TYPE(self);

    PyObject_GC_UnTrack(self);

    for (Py_ssize_t i = 0; i < node_slots(self); ++i) {
        Py_XDECREF(self->items[i]);
    }

    tp->tp_free((PyObject *)self);
    Py_DECREF(tp);
}


static PyObject *BtreeNode_repr(BtreeNode *self) {
    return PyUnicode_FromFormat(
        "BtreeNode(kind=%s, len=%hu, count=%zd)",
        self->is_leaf ? "leaf" : "branch",
        self->len,
        self->count
    );
}


static PyObject *BtreeNode_get_count(BtreeNode *self, void *closure) {
    return PyLong_FromSsize_t(self->count);
}


static PyObject *BtreeNode_get_len(BtreeNode *self, void *closure) {
    return PyLong_FromSsize_t((Py_ssize_t)self->len);
}


static PyObject *BtreeNode_get_is_leaf(BtreeNode *self, void *closure) {
    if (self->is_leaf) {
        Py_RETURN_TRUE;
    }

    Py_RETURN_FALSE;
}


// Forward declaration - needs BtreeIter type from module state.
static PyObject *BtreeNode_iter(PyObject *self);


static PyGetSetDef BtreeNode_getset[] = {
    {"count", (getter)BtreeNode_get_count, nullptr, nullptr, nullptr},
    {"len", (getter)BtreeNode_get_len, nullptr, nullptr, nullptr},
    {"is_leaf", (getter)BtreeNode_get_is_leaf, nullptr, nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr}
};


static PyType_Slot BtreeNode_slots[] = {
    {Py_tp_dealloc, (void *)BtreeNode_dealloc},
    {Py_tp_traverse, (void *)BtreeNode_traverse},
    {Py_tp_repr, (void *)BtreeNode_repr},
    {Py_tp_iter, (void *)BtreeNode_iter},
    {Py_tp_getset, (void *)BtreeNode_getset},
    {0, nullptr}
};


static PyType_Spec BtreeNode_spec = {
    .name = _MODULE_FULL_NAME ".BtreeNode",
    .basicsize = (int)offsetof(BtreeNode, items),
    .itemsize = (int)sizeof(PyObject *),
    .flags = (
        Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_DISALLOW_INSTANTIATION |
        Py_TPFLAGS_ITEMS_AT_END
    ),
    .slots = BtreeNode_slots,
};


//
// BtreeIter
//

struct BtreeIterFrame {
    BtreeNode *node;
    Py_ssize_t idx;
};


// What BtreeIter_next yields per element.
static constexpr int ITER_KIND_ITEMS = 0;
static constexpr int ITER_KIND_KEYS = 1;
static constexpr int ITER_KIND_VALUES = 2;


// Frames held inline in the BtreeIter allocation itself. 16 keeps the object under pymalloc's small-object limit
// (one pool allocation, no separate PyMem buffer), and with the >= 2-children invariant a height-17 tree needs
// > 2^16 keys in maximally degenerate shape -- iter_push's spill path is a correctness backstop, not a normal path.
static constexpr Py_ssize_t BTREE_ITER_INLINE_FRAMES = 16;


// Locking discipline (free-threaded builds): the post-construction mutable state (stack, stack_cap, stack_top, leaf,
// idx) is touched in exactly three contexts:
//
//   1. construction (make_iter / make_*_iter) -- the object is not yet visible to any other thread, so no locking is
//      needed;
//   2. BtreeIter_next -- guarded by a per-object critical section (a no-op on GIL builds);
//   3. tp_clear -- only ever invoked by GC, which is stop-the-world on free-threaded builds.
//
// Anything new that mutates an iterator after construction must join scheme 2. reverse and kind are immutable after
// construction and may be read without locking.

struct BtreeIter {
    PyObject_HEAD

    // Strong ref keeping the whole immutable tree alive.
    BtreeNode *root;

    // Borrowed refs into root. stack points at inline_stack until the depth exceeds BTREE_ITER_INLINE_FRAMES, after
    // which it spills to a PyMem allocation.
    BtreeIterFrame *stack;
    Py_ssize_t stack_cap;
    Py_ssize_t stack_top;

    BtreeNode *leaf;
    Py_ssize_t idx;

    unsigned char reverse;
    unsigned char kind;

    BtreeIterFrame inline_stack[BTREE_ITER_INLINE_FRAMES];
};


static int BtreeIter_traverse(BtreeIter *self, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->root);

    return 0;
}


// Kept (unlike BtreeNode's): clearing root is what lets GC break cycles of the form node -(value)-> iter -(root)->
// node, and it leaves the iterator in a safe exhausted state if anything resurrects it.
static int BtreeIter_clear(BtreeIter *self) {
    Py_CLEAR(self->root);

    self->stack_top = 0;
    self->leaf = nullptr;
    self->idx = 0;

    return 0;
}


static void BtreeIter_dealloc(BtreeIter *self) {
    PyTypeObject *tp = Py_TYPE(self);

    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->root);

    if (self->stack != self->inline_stack) {
        PyMem_Free(self->stack);
    }

    tp->tp_free((PyObject *)self);
    Py_DECREF(tp);
}


static PyObject *BtreeIter_iter(PyObject *self) {
    return Py_NewRef(self);
}


static int iter_push(BtreeIter *self, BtreeNode *node, Py_ssize_t idx) {
    if (self->stack_top >= self->stack_cap) {
        Py_ssize_t new_cap = self->stack_cap * 2;

        if (self->stack == self->inline_stack) {
            BtreeIterFrame *new_stack = (BtreeIterFrame *)PyMem_Malloc(
                (size_t)new_cap * sizeof(BtreeIterFrame)
            );

            if (new_stack == nullptr) {
                PyErr_NoMemory();
                return -1;
            }

            memcpy(new_stack, self->stack, (size_t)self->stack_top * sizeof(BtreeIterFrame));
            self->stack = new_stack;
        }
        else {
            BtreeIterFrame *new_stack = (BtreeIterFrame *)PyMem_Realloc(
                self->stack,
                (size_t)new_cap * sizeof(BtreeIterFrame)
            );

            if (new_stack == nullptr) {
                PyErr_NoMemory();
                return -1;
            }

            self->stack = new_stack;
        }

        self->stack_cap = new_cap;
    }

    self->stack[self->stack_top++] = BtreeIterFrame{node, idx};
    return 0;
}


static int iter_descend_first(BtreeIter *self, BtreeNode *n) {
    while (!n->is_leaf) {
        if (iter_push(self, n, 0) < 0) {
            return -1;
        }

        n = branch_child(n, 0);
    }

    self->leaf = n;
    self->idx = 0;

    return 0;
}


static int iter_descend_last(BtreeIter *self, BtreeNode *n) {
    while (!n->is_leaf) {
        Py_ssize_t idx = n->len - 1;

        if (iter_push(self, n, idx) < 0) {
            return -1;
        }

        n = branch_child(n, idx);
    }

    self->leaf = n;
    self->idx = n->len - 1;

    return 0;
}


static int iter_advance_leaf(BtreeIter *self) {
    while (self->stack_top > 0) {
        BtreeIterFrame frame = self->stack[--self->stack_top];

        Py_ssize_t idx = frame.idx + 1;

        if (idx < frame.node->len) {
            BtreeNode *n = branch_child(frame.node, idx);

            if (iter_push(self, frame.node, idx) < 0) {
                return -1;
            }

            return iter_descend_first(self, n);
        }
    }

    self->leaf = nullptr;
    self->idx = 0;

    return 0;
}


static int iter_retreat_leaf(BtreeIter *self) {
    while (self->stack_top > 0) {
        BtreeIterFrame frame = self->stack[--self->stack_top];

        Py_ssize_t idx = frame.idx - 1;

        if (idx >= 0) {
            BtreeNode *n = branch_child(frame.node, idx);

            if (iter_push(self, frame.node, idx) < 0) {
                return -1;
            }

            return iter_descend_last(self, n);
        }
    }

    self->leaf = nullptr;
    self->idx = -1;

    return 0;
}


static int iter_normalize(BtreeIter *self) {
    if (self->leaf == nullptr) {
        return 0;
    }

    if (self->reverse) {
        if (self->idx < 0) {
            return iter_retreat_leaf(self);
        }
    }
    else {
        if (self->idx >= self->leaf->len) {
            return iter_advance_leaf(self);
        }
    }

    return 0;
}


// Read-only exhaustion test; caller must hold the iterator's critical section (or be its sole owner, as during
// construction). Computes what iter_normalize would conclude without doing the work: an out-of-range idx is
// recoverable iff some stack frame still has a sibling in the iteration direction, and any sibling's subtree is
// non-empty (every node has len >= 1), so a sibling's existence guarantees an element's. Deliberately does *not*
// normalize -- that can allocate via iter_push, and a boolean peek should be infallible and non-mutating. This is
// what restores parity with the pure-python has_next contract: there, eager normalization at the end of next()
// makes the bare leaf check exact; here next() normalizes lazily, so `leaf != nullptr` alone would report a
// phantom element after the last item of the final leaf is consumed.
static int iter_has_next(BtreeIter *self) {
    if (self->leaf == nullptr) {
        return 0;
    }

    if (self->reverse) {
        if (self->idx >= 0) {
            return 1;
        }

        for (Py_ssize_t i = 0; i < self->stack_top; ++i) {
            if (self->stack[i].idx > 0) {
                return 1;
            }
        }
    }
    else {
        if (self->idx < self->leaf->len) {
            return 1;
        }

        for (Py_ssize_t i = 0; i < self->stack_top; ++i) {
            if (self->stack[i].idx + 1 < self->stack[i].node->len) {
                return 1;
            }
        }
    }

    return 0;
}


static PyObject *BtreeIter_next(BtreeIter *self) {
    PyObject *ret = nullptr;

    if (self->kind == ITER_KIND_ITEMS) {
        // Allocated speculatively, *outside* the critical section: PyTuple_New can trigger GC and run arbitrary Python
        // code, which must never happen while the lock is held. Nothing inside the section below can re-enter Python:
        // iter_normalize is pointer walks plus at most a PyMem alloc, and the rest is increfs and array stores. A side
        // benefit of preallocating is that a MemoryError here mutates nothing -- the element stays unconsumed. The
        // keys/values kinds allocate nothing at all: a bare incref is safe inside the section.
        ret = PyTuple_New(2);

        if (ret == nullptr) {
            return nullptr;
        }
    }

    int have = 0;

    Py_BEGIN_CRITICAL_SECTION((PyObject *)self);

    if (iter_normalize(self) == 0 && self->leaf != nullptr) {
        switch (self->kind) {
        case ITER_KIND_ITEMS:
            PyTuple_SET_ITEM(ret, 0, Py_NewRef(node_key(self->leaf, self->idx)));
            PyTuple_SET_ITEM(ret, 1, Py_NewRef(leaf_value(self->leaf, self->idx)));
            break;
        case ITER_KIND_KEYS:
            ret = Py_NewRef(node_key(self->leaf, self->idx));
            break;
        default:
            ret = Py_NewRef(leaf_value(self->leaf, self->idx));
            break;
        }

        if (self->reverse) {
            --self->idx;
        }
        else {
            ++self->idx;
        }

        have = 1;
    }

    Py_END_CRITICAL_SECTION();

    if (!have) {
        // Either iter_normalize failed (exception already set) or the iterator is exhausted (bare nullptr ==
        // StopIteration). ret is only non-null in items mode, whose tuple dealloc handles the null items.
        Py_XDECREF(ret);
        return nullptr;
    }

    return ret;
}


static PyObject *BtreeIter_has_next(BtreeIter *self, PyObject *Py_UNUSED(ignored)) {
    int has = 0;

    Py_BEGIN_CRITICAL_SECTION((PyObject *)self);

    has = iter_has_next(self);

    Py_END_CRITICAL_SECTION();

    return PyBool_FromLong(has);
}


static PyMethodDef BtreeIter_methods[] = {
    {"has_next", (PyCFunction)BtreeIter_has_next, METH_NOARGS, "has_next() -> bool"},
    {nullptr, nullptr, 0, nullptr}
};


static PyType_Slot BtreeIter_slots[] = {
    {Py_tp_dealloc, (void *)BtreeIter_dealloc},
    {Py_tp_traverse, (void *)BtreeIter_traverse},
    {Py_tp_clear, (void *)BtreeIter_clear},
    {Py_tp_iter, (void *)BtreeIter_iter},
    {Py_tp_iternext, (void *)BtreeIter_next},
    {Py_tp_methods, (void *)BtreeIter_methods},
    {0, nullptr}
};


static PyType_Spec BtreeIter_spec = {
    .name = _MODULE_FULL_NAME ".BtreeIter",
    .basicsize = sizeof(BtreeIter),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .slots = BtreeIter_slots,
};


//
// Helpers
//

static int do_cmp(PyObject *cmp, PyObject *a, PyObject *b, int *out) {
    if (cmp == nullptr) {
        int gt = PyObject_RichCompareBool(a, b, Py_GT);

        if (gt < 0) {
            return -1;
        }

        int lt = PyObject_RichCompareBool(a, b, Py_LT);

        if (lt < 0) {
            return -1;
        }

        *out = gt - lt;
        return 0;
    }

    PyObject *args[2] = {a, b};
    PyObject *result = PyObject_Vectorcall(cmp, args, 2, nullptr);

    if (result == nullptr) {
        return -1;
    }

    long val = PyLong_AsLong(result);
    Py_DECREF(result);

    if (val == -1 && PyErr_Occurred()) {
        return -1;
    }

    *out = (val > 0) - (val < 0);
    return 0;
}


// The binary searches only branch on "less" and the found checks only on "equal", so with the default comparator a
// single rich-compare suffices where do_cmp would pay two. The custom-cmp path necessarily still computes the full
// 3-way.

static int do_lt(PyObject *cmp, PyObject *a, PyObject *b, int *out) {
    if (cmp == nullptr) {
        int lt = PyObject_RichCompareBool(a, b, Py_LT);

        if (lt < 0) {
            return -1;
        }

        *out = lt;
        return 0;
    }

    int diff;

    if (do_cmp(cmp, a, b, &diff) < 0) {
        return -1;
    }

    *out = diff < 0;
    return 0;
}


static int do_eq(PyObject *cmp, PyObject *a, PyObject *b, int *out) {
    if (cmp == nullptr) {
        int eq = PyObject_RichCompareBool(a, b, Py_EQ);

        if (eq < 0) {
            return -1;
        }

        *out = eq;
        return 0;
    }

    int diff;

    if (do_cmp(cmp, a, b, &diff) < 0) {
        return -1;
    }

    *out = diff == 0;
    return 0;
}


static int parse_node_arg(btree_state *state, PyObject *obj, BtreeNode **out) {
    if (obj == Py_None) {
        *out = nullptr;
        return 0;
    }

    if (Py_TYPE(obj) == state->BtreeNodeType) {
        *out = (BtreeNode *)obj;
        return 0;
    }

    PyErr_SetString(PyExc_TypeError, "expected BtreeNode or None");
    return -1;
}


static BtreeNode *alloc_node(
    btree_state *state,
    int is_leaf,
    Py_ssize_t len
) {
    assert(len > 0);
    assert(len <= MAX_BRANCH_LEN + 1);

    BtreeNode *node = PyObject_GC_NewVar(
        BtreeNode,
        state->BtreeNodeType,
        2 * len
    );

    if (node == nullptr) {
        return nullptr;
    }

    node->count = 0;
    node->len = (unsigned short)len;
    node->is_leaf = (unsigned char)is_leaf;

    for (Py_ssize_t i = 0; i < node_slots(node); ++i) {
        node->items[i] = nullptr;
    }

    return node;
}


static BtreeNode *make_leaf(
    btree_state *state,
    PyObject **keys,
    PyObject **values,
    Py_ssize_t len
) {
    assert(len > 0);
    assert(len <= MAX_LEAF_LEN);

    BtreeNode *node = alloc_node(state, 1, len);

    if (node == nullptr) {
        return nullptr;
    }

    PyObject **dst_keys = node_keys(node);
    PyObject **dst_values = node_second(node);

    for (Py_ssize_t i = 0; i < len; ++i) {
        dst_keys[i] = Py_NewRef(keys[i]);
        dst_values[i] = Py_NewRef(values[i]);
    }

    node->count = len;

    PyObject_GC_Track(node);
    return node;
}


static BtreeNode *make_branch_direct(
    btree_state *state,
    PyObject **keys,
    BtreeNode **children,
    Py_ssize_t len,
    Py_ssize_t count
) {
    assert(len > 0);
    assert(len <= MAX_BRANCH_LEN);

    if (len == 1) {
        return (BtreeNode *)Py_NewRef((PyObject *)children[0]);
    }

    BtreeNode *node = alloc_node(state, 0, len);

    if (node == nullptr) {
        return nullptr;
    }

    PyObject **dst_keys = node_keys(node);
    PyObject **dst_children = node_second(node);

    for (Py_ssize_t i = 0; i < len; ++i) {
        dst_keys[i] = Py_NewRef(keys[i]);
        dst_children[i] = Py_NewRef((PyObject *)children[i]);
    }

    node->count = count;

    PyObject_GC_Track(node);
    return node;
}


static BtreeNode *make_branch(
    btree_state *state,
    BtreeNode **children,
    Py_ssize_t len
) {
    assert(len > 0);
    assert(len <= MAX_BRANCH_LEN);

    if (len == 1) {
        return (BtreeNode *)Py_NewRef((PyObject *)children[0]);
    }

    PyObject *keys[MAX_BRANCH_LEN];
    Py_ssize_t count = 0;

    for (Py_ssize_t i = 0; i < len; ++i) {
        keys[i] = node_max(children[i]);
        count += children[i]->count;
    }

    return make_branch_direct(state, keys, children, len, count);
}


static PyObject *node_to_pyobject(BtreeNode *node) {
    if (node != nullptr) {
        return (PyObject *)node;
    }

    if (PyErr_Occurred()) {
        return nullptr;
    }

    Py_RETURN_NONE;
}


static int key_index(
    BtreeNode *n,
    PyObject *k,
    PyObject *cmp,
    Py_ssize_t *out_idx,
    int *out_found
) {
    Py_ssize_t lo = 0;
    Py_ssize_t hi = n->len;

    while (lo < hi) {
        Py_ssize_t mid = (lo + hi) / 2;

        int lt;
        if (do_lt(cmp, node_key(n, mid), k, &lt) < 0) {
            return -1;
        }

        if (lt) {
            lo = mid + 1;
        }
        else {
            hi = mid;
        }
    }

    int found = 0;

    if (lo < n->len) {
        if (do_eq(cmp, node_key(n, lo), k, &found) < 0) {
            return -1;
        }
    }

    *out_idx = lo;
    *out_found = found;

    return 0;
}


static int child_index(
    BtreeNode *n,
    PyObject *k,
    PyObject *cmp,
    Py_ssize_t *out_idx
) {
    Py_ssize_t lo = 0;
    Py_ssize_t hi = n->len;

    while (lo < hi) {
        Py_ssize_t mid = (lo + hi) / 2;

        int lt;
        if (do_lt(cmp, node_key(n, mid), k, &lt) < 0) {
            return -1;
        }

        if (lt) {
            lo = mid + 1;
        }
        else {
            hi = mid;
        }
    }

    if (lo == n->len) {
        lo = n->len - 1;
    }

    *out_idx = lo;
    return 0;
}


//
// Owned temporary vector for deletion compaction.
//
// Entries are always owned strong refs. This deliberately pays a few INCREFs around deletion to keep the merge/cleanup
// logic boring and correct.
//

struct NodeVec {
    BtreeNode *items[MAX_BRANCH_LEN + 1];
    Py_ssize_t len;
};


static void node_vec_init(NodeVec *v) {
    v->len = 0;

    for (Py_ssize_t i = 0; i < MAX_BRANCH_LEN + 1; ++i) {
        v->items[i] = nullptr;
    }
}


static void node_vec_clear(NodeVec *v) {
    for (Py_ssize_t i = 0; i < v->len; ++i) {
        Py_XDECREF(v->items[i]);
        v->items[i] = nullptr;
    }

    v->len = 0;
}


static void node_vec_append_newref(NodeVec *v, BtreeNode *n) {
    assert(v->len < MAX_BRANCH_LEN + 1);

    v->items[v->len++] = (BtreeNode *)Py_NewRef((PyObject *)n);
}


static void node_vec_append_steal(NodeVec *v, BtreeNode *n) {
    assert(v->len < MAX_BRANCH_LEN + 1);

    v->items[v->len++] = n;
}


static int can_merge(BtreeNode *a, BtreeNode *b) {
    if (a->is_leaf != b->is_leaf) {
        return 0;
    }

    if (a->is_leaf) {
        return (Py_ssize_t)a->len + (Py_ssize_t)b->len <= MAX_LEAF_LEN;
    }

    return (Py_ssize_t)a->len + (Py_ssize_t)b->len <= MAX_BRANCH_LEN;
}


static BtreeNode *merge_nodes(
    btree_state *state,
    BtreeNode *a,
    BtreeNode *b
) {
    assert(a->is_leaf == b->is_leaf);

    Py_ssize_t len = (Py_ssize_t)a->len + (Py_ssize_t)b->len;

    if (a->is_leaf) {
        PyObject *keys[MAX_LEAF_LEN];
        PyObject *values[MAX_LEAF_LEN];

        for (Py_ssize_t i = 0; i < a->len; ++i) {
            keys[i] = node_key(a, i);
            values[i] = leaf_value(a, i);
        }

        for (Py_ssize_t i = 0; i < b->len; ++i) {
            keys[a->len + i] = node_key(b, i);
            values[a->len + i] = leaf_value(b, i);
        }

        return make_leaf(state, keys, values, len);
    }

    PyObject *keys[MAX_BRANCH_LEN];
    BtreeNode *children[MAX_BRANCH_LEN];

    for (Py_ssize_t i = 0; i < a->len; ++i) {
        keys[i] = node_key(a, i);
        children[i] = branch_child(a, i);
    }

    for (Py_ssize_t i = 0; i < b->len; ++i) {
        keys[a->len + i] = node_key(b, i);
        children[a->len + i] = branch_child(b, i);
    }

    return make_branch_direct(state, keys, children, len, a->count + b->count);
}


static int compact_owned_children(
    btree_state *state,
    NodeVec *src,
    NodeVec *out
) {
    node_vec_init(out);

    for (Py_ssize_t i = 0; i < src->len; ++i) {
        BtreeNode *child = src->items[i];
        src->items[i] = nullptr;

        if (out->len > 0 && can_merge(out->items[out->len - 1], child)) {
            BtreeNode *prev = out->items[out->len - 1];
            out->items[out->len - 1] = nullptr;
            --out->len;

            BtreeNode *merged = merge_nodes(state, prev, child);

            Py_DECREF(prev);
            Py_DECREF(child);

            if (merged == nullptr) {
                node_vec_clear(out);
                node_vec_clear(src);
                return -1;
            }

            node_vec_append_steal(out, merged);
        }
        else {
            node_vec_append_steal(out, child);
        }
    }

    src->len = 0;
    return 0;
}


//
// Core B+ tree algorithms
//

struct InsertResult {
    int split;
    BtreeNode *node;
    BtreeNode *left;
    BtreeNode *right;
};


static void insert_result_init(InsertResult *r) {
    r->split = 0;
    r->node = nullptr;
    r->left = nullptr;
    r->right = nullptr;
}


static void insert_result_clear(InsertResult *r) {
    Py_XDECREF(r->node);
    Py_XDECREF(r->left);
    Py_XDECREF(r->right);

    insert_result_init(r);
}


static int btree_insert_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *v,
    PyObject *cmp,
    InsertResult *out
);


static int leaf_insert_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *v,
    PyObject *cmp,
    InsertResult *out
) {
    assert(n->is_leaf);

    Py_ssize_t idx;
    int found;

    if (key_index(n, k, cmp, &idx, &found) < 0) {
        return -1;
    }

    if (found && leaf_value(n, idx) == v) {
        // No-op by identity, mirroring the delete miss path: every level above short-circuits on pointer equality, so
        // an identical-value reinsert reuses the entire tree.
        out->split = 0;
        out->node = (BtreeNode *)Py_NewRef((PyObject *)n);
        return 0;
    }

    Py_ssize_t len = n->len + (found ? 0 : 1);

    PyObject *keys[MAX_LEAF_LEN + 1];
    PyObject *values[MAX_LEAF_LEN + 1];

    if (found) {
        for (Py_ssize_t i = 0; i < n->len; ++i) {
            keys[i] = node_key(n, i);
            values[i] = (i == idx) ? v : leaf_value(n, i);
        }
    }
    else {
        for (Py_ssize_t i = 0; i < idx; ++i) {
            keys[i] = node_key(n, i);
            values[i] = leaf_value(n, i);
        }

        keys[idx] = k;
        values[idx] = v;

        for (Py_ssize_t i = idx; i < n->len; ++i) {
            keys[i + 1] = node_key(n, i);
            values[i + 1] = leaf_value(n, i);
        }
    }

    if (len <= MAX_LEAF_LEN) {
        out->split = 0;
        out->node = make_leaf(state, keys, values, len);
        return out->node == nullptr ? -1 : 0;
    }

    Py_ssize_t mid = len / 2;

    BtreeNode *left = make_leaf(state, keys, values, mid);

    if (left == nullptr) {
        return -1;
    }

    BtreeNode *right = make_leaf(state, keys + mid, values + mid, len - mid);

    if (right == nullptr) {
        Py_DECREF(left);
        return -1;
    }

    out->split = 1;
    out->left = left;
    out->right = right;

    return 0;
}


static BtreeNode *replace_child(
    btree_state *state,
    BtreeNode *b,
    Py_ssize_t idx,
    BtreeNode *new_child
) {
    BtreeNode *old_child = branch_child(b, idx);
    PyObject *keys[MAX_BRANCH_LEN];
    BtreeNode *children[MAX_BRANCH_LEN];

    PyObject *new_max = node_max(new_child);

    for (Py_ssize_t i = 0; i < b->len; ++i) {
        keys[i] = (i == idx) ? new_max : node_key(b, i);
        children[i] = (i == idx) ? new_child : branch_child(b, i);
    }

    return make_branch_direct(
        state,
        keys,
        children,
        b->len,
        b->count - old_child->count + new_child->count
    );
}


static int branch_insert_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *v,
    PyObject *cmp,
    InsertResult *out
) {
    assert(!n->is_leaf);

    Py_ssize_t idx;

    if (child_index(n, k, cmp, &idx) < 0) {
        return -1;
    }

    BtreeNode *old_child = branch_child(n, idx);

    InsertResult res;
    insert_result_init(&res);

    if (btree_insert_impl(state, old_child, k, v, cmp, &res) < 0) {
        return -1;
    }

    if (!res.split) {
        if (res.node == old_child) {
            insert_result_clear(&res);

            out->split = 0;
            out->node = (BtreeNode *)Py_NewRef((PyObject *)n);
            return 0;
        }

        out->split = 0;
        out->node = replace_child(state, n, idx, res.node);

        insert_result_clear(&res);
        return out->node == nullptr ? -1 : 0;
    }

    Py_ssize_t len = n->len + 1;
    BtreeNode *children[MAX_BRANCH_LEN + 1];

    for (Py_ssize_t i = 0; i < idx; ++i) {
        children[i] = branch_child(n, i);
    }

    children[idx] = res.left;
    children[idx + 1] = res.right;

    for (Py_ssize_t i = idx + 1; i < n->len; ++i) {
        children[i + 1] = branch_child(n, i);
    }

    if (len > MAX_BRANCH_LEN) {
        Py_ssize_t mid = len / 2;

        BtreeNode *left = make_branch(state, children, mid);

        if (left == nullptr) {
            insert_result_clear(&res);
            return -1;
        }

        BtreeNode *right = make_branch(state, children + mid, len - mid);

        if (right == nullptr) {
            Py_DECREF(left);
            insert_result_clear(&res);
            return -1;
        }

        out->split = 1;
        out->left = left;
        out->right = right;

        insert_result_clear(&res);
        return 0;
    }

    PyObject *keys[MAX_BRANCH_LEN];

    for (Py_ssize_t i = 0; i < idx; ++i) {
        keys[i] = node_key(n, i);
    }

    keys[idx] = node_max(res.left);
    keys[idx + 1] = node_max(res.right);

    for (Py_ssize_t i = idx + 1; i < n->len; ++i) {
        keys[i + 1] = node_key(n, i);
    }

    out->split = 0;
    out->node = make_branch_direct(
        state,
        keys,
        children,
        len,
        n->count - old_child->count + res.left->count + res.right->count
    );

    insert_result_clear(&res);
    return out->node == nullptr ? -1 : 0;
}


static int btree_insert_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *v,
    PyObject *cmp,
    InsertResult *out
) {
    if (n->is_leaf) {
        return leaf_insert_impl(state, n, k, v, cmp, out);
    }

    return branch_insert_impl(state, n, k, v, cmp, out);
}


struct DeleteResult {
    int changed;
    BtreeNode *node;
};


static void delete_result_init(DeleteResult *r) {
    r->changed = 0;
    r->node = nullptr;
}


static void delete_result_clear(DeleteResult *r) {
    Py_XDECREF(r->node);
    delete_result_init(r);
}


static int btree_delete_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *cmp,
    DeleteResult *out
);


static int leaf_delete_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *cmp,
    DeleteResult *out
) {
    assert(n->is_leaf);

    Py_ssize_t idx;
    int found;

    if (key_index(n, k, cmp, &idx, &found) < 0) {
        return -1;
    }

    if (!found) {
        out->changed = 0;
        return 0;
    }

    Py_ssize_t len = n->len - 1;

    out->changed = 1;

    if (len == 0) {
        out->node = nullptr;
        return 0;
    }

    PyObject *keys[MAX_LEAF_LEN];
    PyObject *values[MAX_LEAF_LEN];

    for (Py_ssize_t i = 0; i < idx; ++i) {
        keys[i] = node_key(n, i);
        values[i] = leaf_value(n, i);
    }

    for (Py_ssize_t i = idx + 1; i < n->len; ++i) {
        keys[i - 1] = node_key(n, i);
        values[i - 1] = leaf_value(n, i);
    }

    out->node = make_leaf(state, keys, values, len);
    return out->node == nullptr ? -1 : 0;
}


static int branch_delete_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *cmp,
    DeleteResult *out
) {
    assert(!n->is_leaf);

    Py_ssize_t idx;

    if (child_index(n, k, cmp, &idx) < 0) {
        return -1;
    }

    BtreeNode *old_child = branch_child(n, idx);

    DeleteResult res;
    delete_result_init(&res);

    if (btree_delete_impl(state, old_child, k, cmp, &res) < 0) {
        return -1;
    }

    if (!res.changed) {
        out->changed = 0;
        return 0;
    }

    NodeVec children;
    node_vec_init(&children);

    for (Py_ssize_t i = 0; i < idx; ++i) {
        node_vec_append_newref(&children, branch_child(n, i));
    }

    if (res.node != nullptr) {
        node_vec_append_steal(&children, res.node);
        res.node = nullptr;
    }

    for (Py_ssize_t i = idx + 1; i < n->len; ++i) {
        node_vec_append_newref(&children, branch_child(n, i));
    }

    delete_result_clear(&res);

    out->changed = 1;

    if (children.len == 0) {
        out->node = nullptr;
        return 0;
    }

    NodeVec compacted;

    if (compact_owned_children(state, &children, &compacted) < 0) {
        return -1;
    }

    // make_branch recomputes keys/count from the children (O(1) node_max per child, all warm from the can_merge sweep)
    // and performs the unary collapse itself, so no delete-side fast path earns its weight. Contrast replace_child on
    // the insert path, which is hot and whose manual key copy avoids touching the children at all.
    out->node = make_branch(state, compacted.items, compacted.len);
    node_vec_clear(&compacted);

    return out->node == nullptr ? -1 : 0;
}


static int btree_delete_impl(
    btree_state *state,
    BtreeNode *n,
    PyObject *k,
    PyObject *cmp,
    DeleteResult *out
) {
    if (n->is_leaf) {
        return leaf_delete_impl(state, n, k, cmp, out);
    }

    return branch_delete_impl(state, n, k, cmp, out);
}


static PyObject *btree_find_impl(
    BtreeNode *n,
    PyObject *k,
    PyObject *cmp
) {
    while (n != nullptr) {
        if (n->is_leaf) {
            Py_ssize_t idx;
            int found;

            if (key_index(n, k, cmp, &idx, &found) < 0) {
                return nullptr;
            }

            if (!found) {
                return nullptr;
            }

            return Py_NewRef(leaf_value(n, idx));
        }

        Py_ssize_t idx;

        if (child_index(n, k, cmp, &idx) < 0) {
            return nullptr;
        }

        n = branch_child(n, idx);
    }

    return nullptr;
}


//
// Iterator creation
//
// Construction-time descents (iter_push / iter_descend_* / iter_normalize calls below) mutate the iterator without
// locking: the object is not visible to any other thread until it is returned.
//

static BtreeIter *make_iter(
    btree_state *state,
    BtreeNode *root,
    int reverse,
    int kind
) {
    BtreeIter *iter = PyObject_GC_New(BtreeIter, state->BtreeIterType);

    if (iter == nullptr) {
        return nullptr;
    }

    iter->root = nullptr;
    iter->stack = iter->inline_stack;
    iter->stack_cap = BTREE_ITER_INLINE_FRAMES;
    iter->stack_top = 0;
    iter->leaf = nullptr;
    iter->idx = 0;
    iter->reverse = (unsigned char)reverse;
    iter->kind = (unsigned char)kind;

    if (root != nullptr) {
        iter->root = (BtreeNode *)Py_NewRef((PyObject *)root);
    }

    PyObject_GC_Track(iter);
    return iter;
}


static PyObject *make_first_iter(
    btree_state *state,
    BtreeNode *root,
    int kind
) {
    BtreeIter *iter = make_iter(state, root, 0, kind);

    if (iter == nullptr) {
        return nullptr;
    }

    if (root != nullptr && iter_descend_first(iter, root) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    return (PyObject *)iter;
}


static PyObject *make_last_iter(
    btree_state *state,
    BtreeNode *root
) {
    BtreeIter *iter = make_iter(state, root, 1, ITER_KIND_ITEMS);

    if (iter == nullptr) {
        return nullptr;
    }

    if (root != nullptr && iter_descend_last(iter, root) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    return (PyObject *)iter;
}


static PyObject *make_from_iter(
    btree_state *state,
    BtreeNode *root,
    PyObject *k,
    PyObject *cmp
) {
    BtreeIter *iter = make_iter(state, root, 0, ITER_KIND_ITEMS);

    if (iter == nullptr) {
        return nullptr;
    }

    if (root == nullptr) {
        return (PyObject *)iter;
    }

    int max_diff;

    if (do_cmp(cmp, k, node_max(root), &max_diff) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    if (max_diff > 0) {
        return (PyObject *)iter;
    }

    BtreeNode *n = root;

    while (!n->is_leaf) {
        Py_ssize_t idx;

        if (child_index(n, k, cmp, &idx) < 0) {
            Py_DECREF(iter);
            return nullptr;
        }

        if (iter_push(iter, n, idx) < 0) {
            Py_DECREF(iter);
            return nullptr;
        }

        n = branch_child(n, idx);
    }

    Py_ssize_t idx;
    int found;

    if (key_index(n, k, cmp, &idx, &found) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    iter->leaf = n;
    iter->idx = idx;

    return (PyObject *)iter;
}


static PyObject *make_from_reverse_iter(
    btree_state *state,
    BtreeNode *root,
    PyObject *k,
    PyObject *cmp
) {
    BtreeIter *iter = make_iter(state, root, 1, ITER_KIND_ITEMS);

    if (iter == nullptr) {
        return nullptr;
    }

    if (root == nullptr) {
        return (PyObject *)iter;
    }

    BtreeNode *n = root;

    while (!n->is_leaf) {
        Py_ssize_t idx;

        if (child_index(n, k, cmp, &idx) < 0) {
            Py_DECREF(iter);
            return nullptr;
        }

        if (iter_push(iter, n, idx) < 0) {
            Py_DECREF(iter);
            return nullptr;
        }

        n = branch_child(n, idx);
    }

    Py_ssize_t idx;
    int found;

    if (key_index(n, k, cmp, &idx, &found) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    if (!found) {
        --idx;
    }

    iter->leaf = n;
    iter->idx = idx;

    if (iter_normalize(iter) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    return (PyObject *)iter;
}


static PyObject *BtreeNode_iter(PyObject *self) {
    BtreeNode *node = (BtreeNode *)self;

    PyObject *module = PyType_GetModule(Py_TYPE(self));

    if (module == nullptr) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    return make_first_iter(state, node, ITER_KIND_ITEMS);
}


//
// Module-level Python functions
//

static PyObject *btree_new_func(PyObject *module, PyObject *args) {
    PyObject *key;
    PyObject *value;

    if (!PyArg_ParseTuple(args, "OO:new", &key, &value)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    PyObject *keys[1] = {key};
    PyObject *values[1] = {value};

    return (PyObject *)make_leaf(state, keys, values, 1);
}


static PyObject *btree_find_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    PyObject *key;
    PyObject *c_obj;

    if (!PyArg_ParseTuple(args, "OOO:find", &n_obj, &key, &c_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    PyObject *ret = btree_find_impl(n, key, cmp);

    if (ret != nullptr) {
        return ret;
    }

    if (PyErr_Occurred()) {
        return nullptr;
    }

    PyErr_SetObject(PyExc_KeyError, key);
    return nullptr;
}


static PyObject *btree_find_or_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    PyObject *key;
    PyObject *default_obj;
    PyObject *c_obj;

    if (!PyArg_ParseTuple(args, "OOOO:find_or", &n_obj, &key, &default_obj, &c_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    PyObject *ret = btree_find_impl(n, key, cmp);

    if (ret != nullptr) {
        return ret;
    }

    if (PyErr_Occurred()) {
        return nullptr;
    }

    return Py_NewRef(default_obj);
}


static PyObject *btree_insert_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    PyObject *key;
    PyObject *value;
    PyObject *c_obj;

    if (!PyArg_ParseTuple(args, "OOOO:insert", &n_obj, &key, &value, &c_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    if (n == nullptr) {
        PyObject *keys[1] = {key};
        PyObject *values[1] = {value};

        return (PyObject *)make_leaf(state, keys, values, 1);
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    InsertResult res;
    insert_result_init(&res);

    if (btree_insert_impl(state, n, key, value, cmp, &res) < 0) {
        return nullptr;
    }

    if (res.split) {
        BtreeNode *children[2] = {res.left, res.right};
        BtreeNode *root = make_branch(state, children, 2);

        insert_result_clear(&res);

        return node_to_pyobject(root);
    }

    BtreeNode *root = res.node;
    res.node = nullptr;
    insert_result_clear(&res);

    return node_to_pyobject(root);
}


static PyObject *btree_delete_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    PyObject *key;
    PyObject *c_obj;

    if (!PyArg_ParseTuple(args, "OOO:delete", &n_obj, &key, &c_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    if (n == nullptr) {
        Py_RETURN_NONE;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    DeleteResult res;
    delete_result_init(&res);

    if (btree_delete_impl(state, n, key, cmp, &res) < 0) {
        return nullptr;
    }

    if (!res.changed) {
        return Py_NewRef((PyObject *)n);
    }

    BtreeNode *root = res.node;
    res.node = nullptr;
    delete_result_clear(&res);

    return node_to_pyobject(root);
}


static PyObject *btree_len_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:len", &n_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return PyLong_FromSsize_t(n == nullptr ? 0 : n->count);
}


static PyObject *btree_iter_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:iter", &n_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return make_first_iter(state, n, ITER_KIND_ITEMS);
}


static PyObject *btree_iter_keys_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:iter_keys", &n_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return make_first_iter(state, n, ITER_KIND_KEYS);
}


static PyObject *btree_iter_values_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:iter_values", &n_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return make_first_iter(state, n, ITER_KIND_VALUES);
}


static PyObject *btree_riter_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:riter", &n_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return make_last_iter(state, n);
}


static PyObject *btree_iter_from_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    PyObject *key;
    PyObject *c_obj;

    if (!PyArg_ParseTuple(args, "OOO:iter_from", &n_obj, &key, &c_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    return make_from_iter(state, n, key, cmp);
}


static PyObject *btree_riter_from_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    PyObject *key;
    PyObject *c_obj;

    if (!PyArg_ParseTuple(args, "OOO:riter_from", &n_obj, &key, &c_obj)) {
        return nullptr;
    }

    btree_state *state = get_btree_state(module);

    BtreeNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    return make_from_reverse_iter(state, n, key, cmp);
}


//
// Module definition
//

PyDoc_STRVAR(btree_doc, "Native C++ implementation of persistent B+ tree map operations.");


static PyMethodDef btree_methods[] = {
    {"new", (PyCFunction)btree_new_func, METH_VARARGS, "new(key, value)"},
    {"find", (PyCFunction)btree_find_func, METH_VARARGS, "find(root, key, cmp)"},
    {"find_or", (PyCFunction)btree_find_or_func, METH_VARARGS, "find_or(root, key, default, cmp)"},
    {"insert", (PyCFunction)btree_insert_func, METH_VARARGS, "insert(root, key, value, cmp)"},
    {"delete", (PyCFunction)btree_delete_func, METH_VARARGS, "delete(root, key, cmp)"},
    {"len_", (PyCFunction)btree_len_func, METH_VARARGS, "len(root)"},
    {"iter", (PyCFunction)btree_iter_func, METH_VARARGS, "iter(root)"},
    {"iter_keys", (PyCFunction)btree_iter_keys_func, METH_VARARGS, "iter_keys(root)"},
    {"iter_values", (PyCFunction)btree_iter_values_func, METH_VARARGS, "iter_values(root)"},
    {"riter", (PyCFunction)btree_riter_func, METH_VARARGS, "riter(root)"},
    {"iter_from", (PyCFunction)btree_iter_from_func, METH_VARARGS, "iter_from(root, key, cmp)"},
    {"riter_from", (PyCFunction)btree_riter_from_func, METH_VARARGS, "riter_from(root, key, cmp)"},
    {nullptr, nullptr, 0, nullptr}
};


static int btree_exec(PyObject *module) {
    btree_state *state = get_btree_state(module);

    state->BtreeNodeType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &BtreeNode_spec,
        nullptr
    );

    if (state->BtreeNodeType == nullptr) {
        return -1;
    }

    if (PyModule_AddType(module, state->BtreeNodeType) < 0) {
        return -1;
    }

    state->BtreeIterType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &BtreeIter_spec,
        nullptr
    );

    if (state->BtreeIterType == nullptr) {
        return -1;
    }

    if (PyModule_AddType(module, state->BtreeIterType) < 0) {
        return -1;
    }

    if (PyModule_AddIntConstant(module, "MAX_LEAF_LEN", MAX_LEAF_LEN) < 0) {
        return -1;
    }

    if (PyModule_AddIntConstant(module, "MAX_BRANCH_LEN", MAX_BRANCH_LEN) < 0) {
        return -1;
    }

    return 0;
}


static int btree_traverse(PyObject *module, visitproc visit, void *arg) {
    btree_state *state = get_btree_state(module);

    Py_VISIT(state->BtreeNodeType);
    Py_VISIT(state->BtreeIterType);

    return 0;
}


static int btree_clear(PyObject *module) {
    btree_state *state = get_btree_state(module);

    Py_CLEAR(state->BtreeNodeType);
    Py_CLEAR(state->BtreeIterType);

    return 0;
}


static void btree_free(void *module) {
    btree_clear((PyObject *)module);
}


static struct PyModuleDef_Slot btree_slots[] = {
    {Py_mod_exec, (void *)btree_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, nullptr}
};


static struct PyModuleDef btree_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = btree_doc,
    .m_size = sizeof(btree_state),
    .m_methods = btree_methods,
    .m_slots = btree_slots,
    .m_traverse = btree_traverse,
    .m_clear = btree_clear,
    .m_free = btree_free,
};


extern "C" {

PyMODINIT_FUNC PyInit__btreemap(void) {
    return PyModuleDef_Init(&btree_module);
}

}
