// @om-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"

#include <cassert>
#include <cstddef>
#include <cstring>


#define _MODULE_NAME "_btreeseq"
#define _PACKAGE_NAME "omcore.collections.btreeseq"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME


static constexpr Py_ssize_t MAX_LEAF_LEN = 32;
static constexpr Py_ssize_t MAX_BRANCH_LEN = 32;


typedef struct BtreeSeqNode BtreeSeqNode;
typedef struct BtreeSeqIter BtreeSeqIter;


typedef struct btree_seq_state {
    PyTypeObject *BtreeSeqNodeType;
    PyTypeObject *BtreeSeqIterType;
} btree_seq_state;


static btree_seq_state *get_btree_seq_state(PyObject *module) {
    void *state = PyModule_GetState(module);
    assert(state != nullptr);
    return (btree_seq_state *)state;
}


//
// BtreeSeqNode
//

struct BtreeSeqNode {
    PyObject_VAR_HEAD

    Py_ssize_t count;
    int height;
    unsigned short len;
    unsigned char is_leaf;

    // One-element trailing array. Leaves allocate len slots holding the elements; branches allocate 2 * len slots,
    // arranged as:
    //
    //   branch: items[0:len] = children, items[len:2*len] = cumulative counts (raw Py_ssize_t, NOT objects)
    //
    // offsets[i] is the total count of children[:i + 1] -- offsets[len - 1] == count -- so child i spans positions
    // [offsets[i - 1], offsets[i]) with an implicit leading 0, letting descents binary-search instead of scanning.
    // GC traverse and dealloc must touch only the first len slots; the offsets half is not PyObject*.
    PyObject *items[1];
};


static_assert(sizeof(Py_ssize_t) == sizeof(PyObject *), "branch offsets alias object-pointer slots");


static inline PyObject **leaf_items(BtreeSeqNode *n) {
    return n->items;
}


static inline BtreeSeqNode *branch_child(BtreeSeqNode *n, Py_ssize_t i) {
    return (BtreeSeqNode *)n->items[i];
}


static inline Py_ssize_t *branch_offsets(BtreeSeqNode *n) {
    return (Py_ssize_t *)(n->items + n->len);
}


// GC protocol notes, relied on non-locally:
//
//  - Instances of heap types (PyType_FromSpec) own a strong reference to their type -- the Py_DECREF(tp) in the
//    deallocs pays it back -- so tp_traverse must Py_VISIT the type, or instance -> type -> module cycles are invisible
//    to GC and the types/module state leak on interpreter teardown.
//
//  - BtreeSeqNode deliberately has no tp_clear, tuple-style. Nodes are immutable after construction and built
//    bottom-up from already-finished objects, so a pure-node reference cycle is unconstructible; any real cycle
//    through a node also passes through some mutable participant (a dict, a module, a BtreeSeqIter, ...), and GC
//    breaks the cycle *there*, after which node refcounts fall and ordinary dealloc runs. Consequence: a live node is
//    never observable in a partially-cleared state, which is what licenses the absence of any "cleared node"
//    defensive checks in get/iteration below.

static int BtreeSeqNode_traverse(BtreeSeqNode *self, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(self));

    // Only the first len slots are objects -- a branch's offsets half is raw integers.
    for (Py_ssize_t i = 0; i < self->len; ++i) {
        Py_VISIT(self->items[i]);
    }

    return 0;
}


static void BtreeSeqNode_dealloc(BtreeSeqNode *self) {
    PyTypeObject *tp = Py_TYPE(self);

    PyObject_GC_UnTrack(self);

    for (Py_ssize_t i = 0; i < self->len; ++i) {
        Py_XDECREF(self->items[i]);
    }

    tp->tp_free((PyObject *)self);
    Py_DECREF(tp);
}


static PyObject *BtreeSeqNode_repr(BtreeSeqNode *self) {
    // %zd, not %hu: PyUnicode_FromFormat supports only a fixed subset of printf codes, and short modifiers are not
    // in it (they fail at runtime with SystemError, not at compile time).
    return PyUnicode_FromFormat(
        "BtreeSeqNode(kind=%s, len=%zd, count=%zd, height=%d)",
        self->is_leaf ? "leaf" : "branch",
        (Py_ssize_t)self->len,
        self->count,
        self->height
    );
}


static PyObject *BtreeSeqNode_get_count(BtreeSeqNode *self, void *closure) {
    return PyLong_FromSsize_t(self->count);
}


static PyObject *BtreeSeqNode_get_len(BtreeSeqNode *self, void *closure) {
    return PyLong_FromSsize_t((Py_ssize_t)self->len);
}


static PyObject *BtreeSeqNode_get_is_leaf(BtreeSeqNode *self, void *closure) {
    if (self->is_leaf) {
        Py_RETURN_TRUE;
    }

    Py_RETURN_FALSE;
}


static PyObject *BtreeSeqNode_get_height(BtreeSeqNode *self, void *closure) {
    return PyLong_FromSsize_t((Py_ssize_t)self->height);
}


// Forward declaration - needs BtreeSeqIter type from module state.
static PyObject *BtreeSeqNode_iter(PyObject *self);


static PyGetSetDef BtreeSeqNode_getset[] = {
    {"count", (getter)BtreeSeqNode_get_count, nullptr, nullptr, nullptr},
    {"len", (getter)BtreeSeqNode_get_len, nullptr, nullptr, nullptr},
    {"is_leaf", (getter)BtreeSeqNode_get_is_leaf, nullptr, nullptr, nullptr},
    {"height", (getter)BtreeSeqNode_get_height, nullptr, nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr}
};


static PyType_Slot BtreeSeqNode_slots[] = {
    {Py_tp_dealloc, (void *)BtreeSeqNode_dealloc},
    {Py_tp_traverse, (void *)BtreeSeqNode_traverse},
    {Py_tp_repr, (void *)BtreeSeqNode_repr},
    {Py_tp_iter, (void *)BtreeSeqNode_iter},
    {Py_tp_getset, (void *)BtreeSeqNode_getset},
    {0, nullptr}
};


static PyType_Spec BtreeSeqNode_spec = {
    .name = _MODULE_FULL_NAME ".BtreeSeqNode",
    .basicsize = (int)offsetof(BtreeSeqNode, items),
    .itemsize = (int)sizeof(PyObject *),
    .flags = (
        Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_DISALLOW_INSTANTIATION |
        Py_TPFLAGS_ITEMS_AT_END
    ),
    .slots = BtreeSeqNode_slots,
};


//
// BtreeSeqIter
//

struct BtreeSeqIterFrame {
    BtreeSeqNode *node;
    Py_ssize_t idx;
};


// Frames held inline in the BtreeSeqIter allocation itself. 16 keeps the object under pymalloc's small-object limit
// (one pool allocation, no separate PyMem buffer), and with the >= 2-children invariant a height-17 tree needs
// > 2^16 elements in maximally degenerate shape -- iter_push's spill path is a correctness backstop, not a normal
// path.
static constexpr Py_ssize_t BTREE_SEQ_ITER_INLINE_FRAMES = 16;


// Locking discipline (free-threaded builds): the post-construction mutable state (stack, stack_cap, stack_top, leaf,
// idx) is touched in exactly three contexts:
//
//   1. construction (make_seq_iter / make_seq_*_iter) -- the object is not yet visible to any other thread, so no
//      locking is needed;
//   2. BtreeSeqIter_next -- guarded by a per-object critical section (a no-op on GIL builds);
//   3. tp_clear -- only ever invoked by GC, which is stop-the-world on free-threaded builds.
//
// Anything new that mutates an iterator after construction must join scheme 2. reverse is immutable after
// construction and may be read without locking.

struct BtreeSeqIter {
    PyObject_HEAD

    // Strong ref keeping the whole immutable tree alive.
    BtreeSeqNode *root;

    // Borrowed refs into root. stack points at inline_stack until the depth exceeds BTREE_SEQ_ITER_INLINE_FRAMES,
    // after which it spills to a PyMem allocation.
    BtreeSeqIterFrame *stack;
    Py_ssize_t stack_cap;
    Py_ssize_t stack_top;

    BtreeSeqNode *leaf;
    Py_ssize_t idx;

    unsigned char reverse;

    BtreeSeqIterFrame inline_stack[BTREE_SEQ_ITER_INLINE_FRAMES];
};


static int BtreeSeqIter_traverse(BtreeSeqIter *self, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->root);

    return 0;
}


// Kept (unlike BtreeSeqNode's): clearing root is what lets GC break cycles of the form node -(element)-> iter
// -(root)-> node, and it leaves the iterator in a safe exhausted state if anything resurrects it.
static int BtreeSeqIter_clear(BtreeSeqIter *self) {
    Py_CLEAR(self->root);

    self->stack_top = 0;
    self->leaf = nullptr;
    self->idx = 0;

    return 0;
}


static void BtreeSeqIter_dealloc(BtreeSeqIter *self) {
    PyTypeObject *tp = Py_TYPE(self);

    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->root);

    if (self->stack != self->inline_stack) {
        PyMem_Free(self->stack);
    }

    tp->tp_free((PyObject *)self);
    Py_DECREF(tp);
}


static PyObject *BtreeSeqIter_iter(PyObject *self) {
    return Py_NewRef(self);
}


static int iter_push(BtreeSeqIter *self, BtreeSeqNode *node, Py_ssize_t idx) {
    if (self->stack_top >= self->stack_cap) {
        Py_ssize_t new_cap = self->stack_cap * 2;

        if (self->stack == self->inline_stack) {
            BtreeSeqIterFrame *new_stack = (BtreeSeqIterFrame *)PyMem_Malloc(
                (size_t)new_cap * sizeof(BtreeSeqIterFrame)
            );

            if (new_stack == nullptr) {
                PyErr_NoMemory();
                return -1;
            }

            memcpy(new_stack, self->stack, (size_t)self->stack_top * sizeof(BtreeSeqIterFrame));
            self->stack = new_stack;
        }
        else {
            BtreeSeqIterFrame *new_stack = (BtreeSeqIterFrame *)PyMem_Realloc(
                self->stack,
                (size_t)new_cap * sizeof(BtreeSeqIterFrame)
            );

            if (new_stack == nullptr) {
                PyErr_NoMemory();
                return -1;
            }

            self->stack = new_stack;
        }

        self->stack_cap = new_cap;
    }

    self->stack[self->stack_top++] = BtreeSeqIterFrame{node, idx};
    return 0;
}


static int iter_descend_first(BtreeSeqIter *self, BtreeSeqNode *n) {
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


static int iter_descend_last(BtreeSeqIter *self, BtreeSeqNode *n) {
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


static int iter_advance_leaf(BtreeSeqIter *self) {
    while (self->stack_top > 0) {
        BtreeSeqIterFrame frame = self->stack[--self->stack_top];

        Py_ssize_t idx = frame.idx + 1;

        if (idx < frame.node->len) {
            BtreeSeqNode *n = branch_child(frame.node, idx);

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


static int iter_retreat_leaf(BtreeSeqIter *self) {
    while (self->stack_top > 0) {
        BtreeSeqIterFrame frame = self->stack[--self->stack_top];

        Py_ssize_t idx = frame.idx - 1;

        if (idx >= 0) {
            BtreeSeqNode *n = branch_child(frame.node, idx);

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


static int iter_normalize(BtreeSeqIter *self) {
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
// normalize -- that can allocate via iter_push, and a boolean peek should be infallible and non-mutating.
static int iter_has_next(BtreeSeqIter *self) {
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


static PyObject *BtreeSeqIter_next(BtreeSeqIter *self) {
    PyObject *ret = nullptr;

    Py_BEGIN_CRITICAL_SECTION((PyObject *)self);

    // Unlike the map iterator there is no result tuple to preallocate -- the element is returned directly, and a bare
    // incref is safe inside the critical section. Nothing here can re-enter Python: iter_normalize is pointer walks
    // plus at most a PyMem alloc.
    if (iter_normalize(self) == 0 && self->leaf != nullptr) {
        ret = Py_NewRef(self->leaf->items[self->idx]);

        if (self->reverse) {
            --self->idx;
        }
        else {
            ++self->idx;
        }
    }

    Py_END_CRITICAL_SECTION();

    // nullptr: either iter_normalize failed (exception already set) or the iterator is exhausted (bare nullptr ==
    // StopIteration).
    return ret;
}


static PyObject *BtreeSeqIter_has_next(BtreeSeqIter *self, PyObject *Py_UNUSED(ignored)) {
    int has = 0;

    Py_BEGIN_CRITICAL_SECTION((PyObject *)self);

    has = iter_has_next(self);

    Py_END_CRITICAL_SECTION();

    return PyBool_FromLong(has);
}


static PyMethodDef BtreeSeqIter_methods[] = {
    {"has_next", (PyCFunction)BtreeSeqIter_has_next, METH_NOARGS, "has_next() -> bool"},
    {nullptr, nullptr, 0, nullptr}
};


static PyType_Slot BtreeSeqIter_slots[] = {
    {Py_tp_dealloc, (void *)BtreeSeqIter_dealloc},
    {Py_tp_traverse, (void *)BtreeSeqIter_traverse},
    {Py_tp_clear, (void *)BtreeSeqIter_clear},
    {Py_tp_iter, (void *)BtreeSeqIter_iter},
    {Py_tp_iternext, (void *)BtreeSeqIter_next},
    {Py_tp_methods, (void *)BtreeSeqIter_methods},
    {0, nullptr}
};


static PyType_Spec BtreeSeqIter_spec = {
    .name = _MODULE_FULL_NAME ".BtreeSeqIter",
    .basicsize = sizeof(BtreeSeqIter),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .slots = BtreeSeqIter_slots,
};


//
// Helpers
//

static int parse_node_arg(btree_seq_state *state, PyObject *obj, BtreeSeqNode **out) {
    if (obj == Py_None) {
        *out = nullptr;
        return 0;
    }

    if (Py_TYPE(obj) == state->BtreeSeqNodeType) {
        *out = (BtreeSeqNode *)obj;
        return 0;
    }

    PyErr_SetString(PyExc_TypeError, "expected BtreeSeqNode or None");
    return -1;
}


static BtreeSeqNode *alloc_seq_node(
    btree_seq_state *state,
    int is_leaf,
    Py_ssize_t len,
    int height
) {
    assert(len > 0);
    assert(len <= (is_leaf ? MAX_LEAF_LEN : MAX_BRANCH_LEN));

    BtreeSeqNode *node = PyObject_GC_NewVar(
        BtreeSeqNode,
        state->BtreeSeqNodeType,
        is_leaf ? len : 2 * len
    );

    if (node == nullptr) {
        return nullptr;
    }

    node->count = 0;
    node->height = height;
    node->len = (unsigned short)len;
    node->is_leaf = (unsigned char)is_leaf;

    // Only the object slots -- a branch's offsets half is filled by the caller before any failure is possible.
    for (Py_ssize_t i = 0; i < len; ++i) {
        node->items[i] = nullptr;
    }

    return node;
}


static BtreeSeqNode *make_seq_leaf(
    btree_seq_state *state,
    PyObject **items,
    Py_ssize_t len
) {
    assert(len > 0);
    assert(len <= MAX_LEAF_LEN);

    BtreeSeqNode *node = alloc_seq_node(state, 1, len, 0);

    if (node == nullptr) {
        return nullptr;
    }

    for (Py_ssize_t i = 0; i < len; ++i) {
        node->items[i] = Py_NewRef(items[i]);
    }

    node->count = len;

    PyObject_GC_Track(node);
    return node;
}


static BtreeSeqNode *make_seq_leaf2(
    btree_seq_state *state,
    PyObject **a,
    Py_ssize_t alen,
    PyObject **b,
    Py_ssize_t blen
) {
    assert(alen + blen <= MAX_LEAF_LEN);

    PyObject *buf[MAX_LEAF_LEN];

    for (Py_ssize_t i = 0; i < alen; ++i) {
        buf[i] = a[i];
    }

    for (Py_ssize_t i = 0; i < blen; ++i) {
        buf[alen + i] = b[i];
    }

    return make_seq_leaf(state, buf, alen + blen);
}


static BtreeSeqNode *make_seq_branch(
    btree_seq_state *state,
    BtreeSeqNode **children,
    Py_ssize_t len
) {
    assert(len > 0);
    assert(len <= MAX_BRANCH_LEN);

    // Unary collapse: maintains the >= 2-children invariant, and height == 0 <=> leaf along with it.
    if (len == 1) {
        return (BtreeSeqNode *)Py_NewRef((PyObject *)children[0]);
    }

    int height = 0;

    for (Py_ssize_t i = 0; i < len; ++i) {
        if (children[i]->height > height) {
            height = children[i]->height;
        }
    }

    BtreeSeqNode *node = alloc_seq_node(state, 0, len, height + 1);

    if (node == nullptr) {
        return nullptr;
    }

    Py_ssize_t *offsets = branch_offsets(node);
    Py_ssize_t total = 0;

    for (Py_ssize_t i = 0; i < len; ++i) {
        node->items[i] = Py_NewRef((PyObject *)children[i]);
        total += children[i]->count;
        offsets[i] = total;
    }

    node->count = total;

    PyObject_GC_Track(node);
    return node;
}


static PyObject *seq_node_to_pyobject(BtreeSeqNode *node) {
    if (node != nullptr) {
        return (PyObject *)node;
    }

    if (PyErr_Occurred()) {
        return nullptr;
    }

    Py_RETURN_NONE;
}


// First child whose end offset exceeds idx, plus the position within it. An out-of-range idx lands on len and the
// caller's child access is what breaks -- the module-level functions validate/clamp, mirroring the wrapper-owned
// contract of the pure-python backend.
static Py_ssize_t seq_find_child(BtreeSeqNode *n, Py_ssize_t idx, Py_ssize_t *sub_idx) {
    Py_ssize_t *offs = branch_offsets(n);
    Py_ssize_t lo = 0;
    Py_ssize_t hi = n->len;

    while (lo < hi) {
        Py_ssize_t mid = (lo + hi) / 2;

        if (offs[mid] <= idx) {
            lo = mid + 1;
        }
        else {
            hi = mid;
        }
    }

    *sub_idx = idx - (lo > 0 ? offs[lo - 1] : 0);
    return lo;
}


//
// Owned temporary vector for structural rebuilds.
//
// Entries are always owned strong refs. This deliberately pays a few INCREFs around packing to keep the merge/cleanup
// logic boring and correct. Capacity 2 * MAX_BRANCH_LEN covers the worst case (concat of two full same-height
// branches).
//

static constexpr Py_ssize_t SEQ_VEC_CAP = 2 * MAX_BRANCH_LEN;


struct SeqNodeVec {
    BtreeSeqNode *items[SEQ_VEC_CAP];
    Py_ssize_t len;
};


static void seq_vec_init(SeqNodeVec *v) {
    v->len = 0;

    for (Py_ssize_t i = 0; i < SEQ_VEC_CAP; ++i) {
        v->items[i] = nullptr;
    }
}


static void seq_vec_clear(SeqNodeVec *v) {
    for (Py_ssize_t i = 0; i < v->len; ++i) {
        Py_XDECREF(v->items[i]);
        v->items[i] = nullptr;
    }

    v->len = 0;
}


static void seq_vec_append_newref(SeqNodeVec *v, BtreeSeqNode *n) {
    assert(v->len < SEQ_VEC_CAP);

    v->items[v->len++] = (BtreeSeqNode *)Py_NewRef((PyObject *)n);
}


static void seq_vec_append_steal(SeqNodeVec *v, BtreeSeqNode *n) {
    assert(v->len < SEQ_VEC_CAP);

    v->items[v->len++] = n;
}


static int can_merge_seq(BtreeSeqNode *a, BtreeSeqNode *b) {
    if (a->is_leaf != b->is_leaf) {
        return 0;
    }

    if (a->is_leaf) {
        return (Py_ssize_t)a->len + (Py_ssize_t)b->len <= MAX_LEAF_LEN;
    }

    return (Py_ssize_t)a->len + (Py_ssize_t)b->len <= MAX_BRANCH_LEN;
}


static BtreeSeqNode *merge_seq_nodes(
    btree_seq_state *state,
    BtreeSeqNode *a,
    BtreeSeqNode *b
) {
    assert(a->is_leaf == b->is_leaf);

    if (a->is_leaf) {
        return make_seq_leaf2(state, leaf_items(a), a->len, leaf_items(b), b->len);
    }

    BtreeSeqNode *children[MAX_BRANCH_LEN];

    for (Py_ssize_t i = 0; i < a->len; ++i) {
        children[i] = branch_child(a, i);
    }

    for (Py_ssize_t i = 0; i < b->len; ++i) {
        children[a->len + i] = branch_child(b, i);
    }

    return make_seq_branch(state, children, (Py_ssize_t)a->len + (Py_ssize_t)b->len);
}


// In-place adjacent same-kind merge over an array of owned refs. Consumed slots are nulled as it goes; on failure
// everything is released and -1 returned, otherwise the new length.
static Py_ssize_t compact_seq_nodes(
    btree_seq_state *state,
    BtreeSeqNode **arr,
    Py_ssize_t len
) {
    Py_ssize_t out = 0;

    for (Py_ssize_t i = 0; i < len; ++i) {
        BtreeSeqNode *cur = arr[i];
        arr[i] = nullptr;

        if (out > 0 && can_merge_seq(arr[out - 1], cur)) {
            BtreeSeqNode *prev = arr[out - 1];
            arr[out - 1] = nullptr;
            --out;

            BtreeSeqNode *merged = merge_seq_nodes(state, prev, cur);

            Py_DECREF(prev);
            Py_DECREF(cur);

            if (merged == nullptr) {
                for (Py_ssize_t j = 0; j < out; ++j) {
                    Py_XDECREF(arr[j]);
                    arr[j] = nullptr;
                }

                for (Py_ssize_t j = i + 1; j < len; ++j) {
                    Py_XDECREF(arr[j]);
                    arr[j] = nullptr;
                }

                return -1;
            }

            arr[out++] = merged;
        }
        else {
            arr[out++] = cur;
        }
    }

    return out;
}


// The py backend's _pack_children: compact adjacent mergeables, then group into branches of MAX_BRANCH_LEN,
// repeating until a single (possibly collapsed) node remains. Operates in place on an array of owned refs of
// arbitrary length, consuming every entry -- including on failure.
static int pack_seq_children(
    btree_seq_state *state,
    BtreeSeqNode **arr,
    Py_ssize_t len,
    BtreeSeqNode **out
) {
    for (;;) {
        len = compact_seq_nodes(state, arr, len);

        if (len < 0) {
            return -1;
        }

        if (len == 0) {
            *out = nullptr;
            return 0;
        }

        if (len <= MAX_BRANCH_LEN) {
            BtreeSeqNode *node = make_seq_branch(state, arr, len);

            for (Py_ssize_t i = 0; i < len; ++i) {
                Py_DECREF(arr[i]);
                arr[i] = nullptr;
            }

            *out = node;
            return node == nullptr ? -1 : 0;
        }

        Py_ssize_t out_len = 0;

        for (Py_ssize_t i = 0; i < len; i += MAX_BRANCH_LEN) {
            Py_ssize_t g = len - i < MAX_BRANCH_LEN ? len - i : MAX_BRANCH_LEN;

            BtreeSeqNode *b = make_seq_branch(state, arr + i, g);

            for (Py_ssize_t j = i; j < i + g; ++j) {
                Py_DECREF(arr[j]);
                arr[j] = nullptr;
            }

            if (b == nullptr) {
                for (Py_ssize_t j = 0; j < out_len; ++j) {
                    Py_DECREF(arr[j]);
                    arr[j] = nullptr;
                }

                for (Py_ssize_t j = i + g; j < len; ++j) {
                    Py_DECREF(arr[j]);
                    arr[j] = nullptr;
                }

                return -1;
            }

            // out_len <= i / MAX_BRANCH_LEN < i + g, so this never clobbers an unconsumed source slot.
            arr[out_len++] = b;
        }

        len = out_len;
    }
}


static int pack_seq_vec(btree_seq_state *state, SeqNodeVec *v, BtreeSeqNode **out) {
    int r = pack_seq_children(state, v->items, v->len, out);

    // pack_seq_children consumes every entry, success or failure.
    v->len = 0;

    return r;
}


//
// Core algorithms
//
// All take borrowed node arguments (nullptr == empty) and produce owned results via *out; -1 means an exception is
// set. Indices are assumed pre-normalized by the wrapper, but _take/_drop are total (they clamp), and the
// module-level splice function clamps as crash insurance.
//

static int seq_take(
    btree_seq_state *state,
    BtreeSeqNode *n,
    Py_ssize_t idx,
    BtreeSeqNode **out
) {
    // Prefix [:idx]. With seq_drop, replaces a two-sided split: only the kept side is ever constructed, so a splice
    // needs no intermediate 'rest' tree and never packs a discarded segment.
    if (n == nullptr || idx >= n->count) {
        *out = (BtreeSeqNode *)Py_XNewRef((PyObject *)n);
        return 0;
    }

    if (idx <= 0) {
        *out = nullptr;
        return 0;
    }

    if (n->is_leaf) {
        *out = make_seq_leaf(state, leaf_items(n), idx);
        return *out == nullptr ? -1 : 0;
    }

    // bisect_left: first child whose end offset reaches idx.
    Py_ssize_t *offs = branch_offsets(n);
    Py_ssize_t lo = 0;
    Py_ssize_t hi = n->len;

    while (lo < hi) {
        Py_ssize_t mid = (lo + hi) / 2;

        if (offs[mid] < idx) {
            lo = mid + 1;
        }
        else {
            hi = mid;
        }
    }

    Py_ssize_t base = lo > 0 ? offs[lo - 1] : 0;

    // 0 < idx - base <= children[lo].count here, so the recursion yields a node -- possibly children[lo] itself,
    // shared whole, when idx lands exactly on its end.
    BtreeSeqNode *sub;

    if (seq_take(state, branch_child(n, lo), idx - base, &sub) < 0) {
        return -1;
    }

    SeqNodeVec v;
    seq_vec_init(&v);

    for (Py_ssize_t i = 0; i < lo; ++i) {
        seq_vec_append_newref(&v, branch_child(n, i));
    }

    seq_vec_append_steal(&v, sub);

    return pack_seq_vec(state, &v, out);
}


static int seq_drop(
    btree_seq_state *state,
    BtreeSeqNode *n,
    Py_ssize_t idx,
    BtreeSeqNode **out
) {
    // Suffix [idx:].
    if (n == nullptr || idx <= 0) {
        *out = (BtreeSeqNode *)Py_XNewRef((PyObject *)n);
        return 0;
    }

    if (idx >= n->count) {
        *out = nullptr;
        return 0;
    }

    if (n->is_leaf) {
        *out = make_seq_leaf(state, leaf_items(n) + idx, n->len - idx);
        return *out == nullptr ? -1 : 0;
    }

    Py_ssize_t sub_idx;
    Py_ssize_t ci = seq_find_child(n, idx, &sub_idx);

    // 0 <= sub_idx < children[ci].count here, so the recursion yields a node -- possibly children[ci] itself, shared
    // whole, when idx lands exactly on its start.
    BtreeSeqNode *sub;

    if (seq_drop(state, branch_child(n, ci), sub_idx, &sub) < 0) {
        return -1;
    }

    SeqNodeVec v;
    seq_vec_init(&v);

    seq_vec_append_steal(&v, sub);

    for (Py_ssize_t i = ci + 1; i < n->len; ++i) {
        seq_vec_append_newref(&v, branch_child(n, i));
    }

    return pack_seq_vec(state, &v, out);
}


static int seq_concat(
    btree_seq_state *state,
    BtreeSeqNode *a,
    BtreeSeqNode *b,
    BtreeSeqNode **out
) {
    // Height-guided, rope-style: descend the taller side's spine until heights match, merge there, and repack on the
    // way back up -- see the py backend's _concat for the full rationale. On the unequal-height paths the recursive
    // result is bounded by the taller side's own height; when it *reaches* that bound (a merge one level down
    // overflowed and packed into a fresh parent), its children are spliced in as siblings -- b+tree split
    // propagation. Keeping it as an opaque child instead would nest one level per overflow, degenerating a spine of
    // repeated appends into a linked list of packed pairs.
    if (a == nullptr) {
        *out = (BtreeSeqNode *)Py_XNewRef((PyObject *)b);
        return 0;
    }

    if (b == nullptr) {
        *out = (BtreeSeqNode *)Py_NewRef((PyObject *)a);
        return 0;
    }

    if (a->height == b->height) {
        if (a->is_leaf) {
            if ((Py_ssize_t)a->len + (Py_ssize_t)b->len <= MAX_LEAF_LEN) {
                *out = make_seq_leaf2(state, leaf_items(a), a->len, leaf_items(b), b->len);
                return *out == nullptr ? -1 : 0;
            }

            SeqNodeVec v;
            seq_vec_init(&v);

            seq_vec_append_newref(&v, a);
            seq_vec_append_newref(&v, b);

            return pack_seq_vec(state, &v, out);
        }

        SeqNodeVec v;
        seq_vec_init(&v);

        for (Py_ssize_t i = 0; i < a->len; ++i) {
            seq_vec_append_newref(&v, branch_child(a, i));
        }

        for (Py_ssize_t i = 0; i < b->len; ++i) {
            seq_vec_append_newref(&v, branch_child(b, i));
        }

        return pack_seq_vec(state, &v, out);
    }

    if (a->height > b->height) {
        BtreeSeqNode *sub;

        if (seq_concat(state, branch_child(a, a->len - 1), b, &sub) < 0) {
            return -1;
        }

        SeqNodeVec v;
        seq_vec_init(&v);

        for (Py_ssize_t i = 0; i < a->len - 1; ++i) {
            seq_vec_append_newref(&v, branch_child(a, i));
        }

        if (sub->height == a->height) {
            for (Py_ssize_t i = 0; i < sub->len; ++i) {
                seq_vec_append_newref(&v, branch_child(sub, i));
            }

            Py_DECREF(sub);
        }
        else {
            seq_vec_append_steal(&v, sub);
        }

        return pack_seq_vec(state, &v, out);
    }

    BtreeSeqNode *sub;

    if (seq_concat(state, a, branch_child(b, 0), &sub) < 0) {
        return -1;
    }

    SeqNodeVec v;
    seq_vec_init(&v);

    if (sub->height == b->height) {
        for (Py_ssize_t i = 0; i < sub->len; ++i) {
            seq_vec_append_newref(&v, branch_child(sub, i));
        }

        Py_DECREF(sub);
    }
    else {
        seq_vec_append_steal(&v, sub);
    }

    for (Py_ssize_t i = 1; i < b->len; ++i) {
        seq_vec_append_newref(&v, branch_child(b, i));
    }

    return pack_seq_vec(state, &v, out);
}


static int seq_replace_same(
    btree_seq_state *state,
    BtreeSeqNode *n,
    Py_ssize_t start,
    PyObject **items,
    Py_ssize_t off,
    Py_ssize_t lim,
    BtreeSeqNode **out
) {
    // Same-length replacement of positions [start, start + (lim - off)) with items[off:lim] -- see the py backend's
    // _replace_same. Shape-preserving by induction, so make_seq_branch's recomputation below reproduces the same
    // offsets and height.
    if (off >= lim) {
        *out = (BtreeSeqNode *)Py_NewRef((PyObject *)n);
        return 0;
    }

    if (n->is_leaf) {
        Py_ssize_t stop = start + (lim - off);

        int same = 1;

        for (Py_ssize_t i = off; i < lim; ++i) {
            if (n->items[start - off + i] != items[i]) {
                same = 0;
                break;
            }
        }

        if (same) {
            // Identity no-op, mirroring btreemap's identical-value reinsert: the branch level below short-circuits on
            // pointer equality, so replacing a run with the very same objects reuses the whole tree (and the wrapper's
            // 'root is self._root' check then returns self).
            *out = (BtreeSeqNode *)Py_NewRef((PyObject *)n);
            return 0;
        }

        PyObject *buf[MAX_LEAF_LEN];

        for (Py_ssize_t i = 0; i < start; ++i) {
            buf[i] = n->items[i];
        }

        for (Py_ssize_t i = off; i < lim; ++i) {
            buf[start - off + i] = items[i];
        }

        for (Py_ssize_t i = stop; i < n->len; ++i) {
            buf[i] = n->items[i];
        }

        *out = make_seq_leaf(state, buf, n->len);
        return *out == nullptr ? -1 : 0;
    }

    Py_ssize_t end = start + (lim - off);
    Py_ssize_t *offs = branch_offsets(n);

    // bisect_right: first child containing position start.
    Py_ssize_t lo = 0;
    Py_ssize_t hi = n->len;

    while (lo < hi) {
        Py_ssize_t mid = (lo + hi) / 2;

        if (offs[mid] <= start) {
            lo = mid + 1;
        }
        else {
            hi = mid;
        }
    }

    Py_ssize_t base = lo > 0 ? offs[lo - 1] : 0;
    Py_ssize_t item_off = off;
    int changed = 0;

    SeqNodeVec v;
    seq_vec_init(&v);

    for (Py_ssize_t i = 0; i < lo; ++i) {
        seq_vec_append_newref(&v, branch_child(n, i));
    }

    Py_ssize_t i = lo;

    for (; i < n->len; ++i) {
        if (base >= end) {
            break;
        }

        BtreeSeqNode *child = branch_child(n, i);
        Py_ssize_t nxt = offs[i];

        Py_ssize_t child_start = (start > base ? start : base) - base;
        Py_ssize_t child_stop = (end < nxt ? end : nxt) - base;
        Py_ssize_t item_lim = item_off + (child_stop - child_start);

        BtreeSeqNode *sub;

        if (seq_replace_same(state, child, child_start, items, item_off, item_lim, &sub) < 0) {
            seq_vec_clear(&v);
            return -1;
        }

        if (sub != child) {
            changed = 1;
        }

        seq_vec_append_steal(&v, sub);

        item_off = item_lim;
        base = nxt;
    }

    if (!changed) {
        seq_vec_clear(&v);

        *out = (BtreeSeqNode *)Py_NewRef((PyObject *)n);
        return 0;
    }

    for (; i < n->len; ++i) {
        seq_vec_append_newref(&v, branch_child(n, i));
    }

    // v.len == n->len >= 2, so make_seq_branch's unary collapse cannot apply.
    *out = make_seq_branch(state, v.items, v.len);
    seq_vec_clear(&v);

    return *out == nullptr ? -1 : 0;
}


static int seq_append_small(
    btree_seq_state *state,
    BtreeSeqNode *n,
    PyObject **items,
    Py_ssize_t k,
    BtreeSeqNode **out
) {
    // Right-spine append fast path: when the run fits in the rightmost leaf, rebuild just the spine -- no packing
    // sweeps. *out == nullptr with no exception means the run doesn't fit and the general splice path (whose
    // seq_concat compacts and splits as needed) should handle it -- that happens at most once per MAX_LEAF_LEN
    // single-item appends, keeping the amortized cost low.
    if (n->is_leaf) {
        if (n->len + k > MAX_LEAF_LEN) {
            *out = nullptr;
            return 0;
        }

        *out = make_seq_leaf2(state, leaf_items(n), n->len, items, k);
        return *out == nullptr ? -1 : 0;
    }

    BtreeSeqNode *sub;

    if (seq_append_small(state, branch_child(n, n->len - 1), items, k, &sub) < 0) {
        return -1;
    }

    if (sub == nullptr) {
        *out = nullptr;
        return 0;
    }

    // sub has the same height as the child it replaces (by induction: leaves stay leaves, branches reuse their
    // shape), so make_seq_branch reproduces this node's height and sibling structure exactly.
    BtreeSeqNode *children[MAX_BRANCH_LEN];

    for (Py_ssize_t i = 0; i < n->len - 1; ++i) {
        children[i] = branch_child(n, i);
    }

    children[n->len - 1] = sub;

    *out = make_seq_branch(state, children, n->len);

    Py_DECREF(sub);

    return *out == nullptr ? -1 : 0;
}


static int seq_from_items(
    btree_seq_state *state,
    PyObject **items,
    Py_ssize_t k,
    BtreeSeqNode **out
) {
    if (k == 0) {
        *out = nullptr;
        return 0;
    }

    Py_ssize_t nleaves = (k + MAX_LEAF_LEN - 1) / MAX_LEAF_LEN;

    BtreeSeqNode *small[SEQ_VEC_CAP];
    BtreeSeqNode **arr = small;

    if (nleaves > SEQ_VEC_CAP) {
        arr = (BtreeSeqNode **)PyMem_Malloc((size_t)nleaves * sizeof(BtreeSeqNode *));

        if (arr == nullptr) {
            PyErr_NoMemory();
            return -1;
        }
    }

    Py_ssize_t built = 0;

    for (Py_ssize_t i = 0; i < k; i += MAX_LEAF_LEN) {
        Py_ssize_t g = k - i < MAX_LEAF_LEN ? k - i : MAX_LEAF_LEN;

        BtreeSeqNode *leaf = make_seq_leaf(state, items + i, g);

        if (leaf == nullptr) {
            for (Py_ssize_t j = 0; j < built; ++j) {
                Py_DECREF(arr[j]);
            }

            if (arr != small) {
                PyMem_Free(arr);
            }

            return -1;
        }

        arr[built++] = leaf;
    }

    int r = pack_seq_children(state, arr, built, out);

    if (arr != small) {
        PyMem_Free(arr);
    }

    return r;
}


static int seq_splice_impl(
    btree_seq_state *state,
    BtreeSeqNode *n,
    Py_ssize_t start,
    Py_ssize_t stop,
    PyObject **items,
    Py_ssize_t k,
    BtreeSeqNode **out
) {
    if (n == nullptr) {
        return seq_from_items(state, items, k, out);
    }

    Py_ssize_t remove_len = stop - start;

    if (remove_len == k) {
        if (k == 0) {
            *out = (BtreeSeqNode *)Py_NewRef((PyObject *)n);
            return 0;
        }

        return seq_replace_same(state, n, start, items, 0, k, out);
    }

    if (start == n->count && stop == n->count && k > 0) {
        BtreeSeqNode *res;

        if (seq_append_small(state, n, items, k, &res) < 0) {
            return -1;
        }

        if (res != nullptr) {
            *out = res;
            return 0;
        }
    }

    BtreeSeqNode *left;

    if (seq_take(state, n, start, &left) < 0) {
        return -1;
    }

    BtreeSeqNode *right;

    if (seq_drop(state, n, stop, &right) < 0) {
        Py_XDECREF(left);
        return -1;
    }

    BtreeSeqNode *mid;

    if (seq_from_items(state, items, k, &mid) < 0) {
        Py_XDECREF(left);
        Py_XDECREF(right);
        return -1;
    }

    BtreeSeqNode *lm;
    int r = seq_concat(state, left, mid, &lm);

    Py_XDECREF(left);
    Py_XDECREF(mid);

    if (r < 0) {
        Py_XDECREF(right);
        return -1;
    }

    r = seq_concat(state, lm, right, out);

    Py_XDECREF(lm);
    Py_XDECREF(right);

    return r;
}


static PyObject *seq_get_impl(BtreeSeqNode *n, Py_ssize_t idx) {
    while (!n->is_leaf) {
        Py_ssize_t sub_idx;
        Py_ssize_t ci = seq_find_child(n, idx, &sub_idx);

        n = branch_child(n, ci);
        idx = sub_idx;
    }

    return Py_NewRef(n->items[idx]);
}


//
// Iterator creation
//
// Construction-time descents (iter_push / iter_descend_* calls below) mutate the iterator without locking: the
// object is not visible to any other thread until it is returned.
//

static BtreeSeqIter *make_seq_iter(
    btree_seq_state *state,
    BtreeSeqNode *root,
    int reverse
) {
    BtreeSeqIter *iter = PyObject_GC_New(BtreeSeqIter, state->BtreeSeqIterType);

    if (iter == nullptr) {
        return nullptr;
    }

    iter->root = nullptr;
    iter->stack = iter->inline_stack;
    iter->stack_cap = BTREE_SEQ_ITER_INLINE_FRAMES;
    iter->stack_top = 0;
    iter->leaf = nullptr;
    iter->idx = 0;
    iter->reverse = (unsigned char)reverse;

    if (root != nullptr) {
        iter->root = (BtreeSeqNode *)Py_NewRef((PyObject *)root);
    }

    PyObject_GC_Track(iter);
    return iter;
}


static PyObject *make_seq_first_iter(
    btree_seq_state *state,
    BtreeSeqNode *root
) {
    BtreeSeqIter *iter = make_seq_iter(state, root, 0);

    if (iter == nullptr) {
        return nullptr;
    }

    if (root != nullptr && iter_descend_first(iter, root) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    return (PyObject *)iter;
}


static PyObject *make_seq_last_iter(
    btree_seq_state *state,
    BtreeSeqNode *root
) {
    BtreeSeqIter *iter = make_seq_iter(state, root, 1);

    if (iter == nullptr) {
        return nullptr;
    }

    if (root != nullptr && iter_descend_last(iter, root) < 0) {
        Py_DECREF(iter);
        return nullptr;
    }

    return (PyObject *)iter;
}


static PyObject *make_seq_from_iter(
    btree_seq_state *state,
    BtreeSeqNode *root,
    Py_ssize_t idx
) {
    BtreeSeqIter *iter = make_seq_iter(state, root, 0);

    if (iter == nullptr) {
        return nullptr;
    }

    if (root == nullptr || idx >= root->count) {
        return (PyObject *)iter;
    }

    if (idx < 0) {
        idx = 0;
    }

    BtreeSeqNode *n = root;

    while (!n->is_leaf) {
        Py_ssize_t sub_idx;
        Py_ssize_t ci = seq_find_child(n, idx, &sub_idx);

        if (iter_push(iter, n, ci) < 0) {
            Py_DECREF(iter);
            return nullptr;
        }

        n = branch_child(n, ci);
        idx = sub_idx;
    }

    // idx < leaf len: 0 <= idx < count threads down through seq_find_child at every level.
    iter->leaf = n;
    iter->idx = idx;

    return (PyObject *)iter;
}


static PyObject *BtreeSeqNode_iter(PyObject *self) {
    BtreeSeqNode *node = (BtreeSeqNode *)self;

    PyObject *module = PyType_GetModule(Py_TYPE(self));

    if (module == nullptr) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    return make_seq_first_iter(state, node);
}


//
// Module-level Python functions
//

static PyObject *seq_from_iterable_func(PyObject *module, PyObject *args) {
    PyObject *items_obj;

    if (!PyArg_ParseTuple(args, "O:from_iterable", &items_obj)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    // A tuple, not PySequence_Fast: the borrowed item array must stay valid across node allocations, which can run
    // GC and arbitrary finalizers -- a source *list* could be resized under us.
    PyObject *tup = PySequence_Tuple(items_obj);

    if (tup == nullptr) {
        return nullptr;
    }

    BtreeSeqNode *root;
    int r = seq_from_items(state, PySequence_Fast_ITEMS(tup), PyTuple_GET_SIZE(tup), &root);

    Py_DECREF(tup);

    if (r < 0) {
        return nullptr;
    }

    return seq_node_to_pyobject(root);
}


static PyObject *seq_len_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:len_", &n_obj)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    BtreeSeqNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return PyLong_FromSsize_t(n == nullptr ? 0 : n->count);
}


static PyObject *seq_get_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    Py_ssize_t idx;

    if (!PyArg_ParseTuple(args, "On:get", &n_obj, &idx)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    BtreeSeqNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    // Crash insurance only -- the wrapper owns normalization (see the py backend's contract note); a violated
    // contract must raise, not walk off the node arrays.
    if (n == nullptr || idx < 0 || idx >= n->count) {
        PyErr_SetObject(PyExc_IndexError, PyTuple_GET_ITEM(args, 1));
        return nullptr;
    }

    return seq_get_impl(n, idx);
}


static PyObject *seq_slice_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    Py_ssize_t start;
    Py_ssize_t stop;

    if (!PyArg_ParseTuple(args, "Onn:slice", &n_obj, &start, &stop)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    BtreeSeqNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    if (n == nullptr || start >= stop) {
        Py_RETURN_NONE;
    }

    // seq_take and seq_drop are total (out-of-range indices clamp), so no explicit validation is needed here.
    BtreeSeqNode *dropped;

    if (seq_drop(state, n, start, &dropped) < 0) {
        return nullptr;
    }

    BtreeSeqNode *out;
    int r = seq_take(state, dropped, stop - start, &out);

    Py_XDECREF(dropped);

    if (r < 0) {
        return nullptr;
    }

    return seq_node_to_pyobject(out);
}


static PyObject *seq_splice_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    Py_ssize_t start;
    Py_ssize_t stop;
    PyObject *items_obj;

    if (!PyArg_ParseTuple(args, "OnnO:splice", &n_obj, &start, &stop, &items_obj)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    BtreeSeqNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    // Crash insurance only -- the wrapper owns normalization; clamping keeps a violated contract memory-safe (the
    // replace-same leaf rebuild indexes item arrays directly).
    if (n != nullptr) {
        if (start < 0) {
            start = 0;
        }

        if (start > n->count) {
            start = n->count;
        }

        if (stop < start) {
            stop = start;
        }

        if (stop > n->count) {
            stop = n->count;
        }
    }

    // A tuple, not PySequence_Fast -- see seq_from_iterable_func.
    PyObject *tup = PySequence_Tuple(items_obj);

    if (tup == nullptr) {
        return nullptr;
    }

    BtreeSeqNode *out;
    int r = seq_splice_impl(state, n, start, stop, PySequence_Fast_ITEMS(tup), PyTuple_GET_SIZE(tup), &out);

    Py_DECREF(tup);

    if (r < 0) {
        return nullptr;
    }

    return seq_node_to_pyobject(out);
}


static PyObject *seq_iter_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:iter", &n_obj)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    BtreeSeqNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return make_seq_first_iter(state, n);
}


static PyObject *seq_riter_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;

    if (!PyArg_ParseTuple(args, "O:riter", &n_obj)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    BtreeSeqNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return make_seq_last_iter(state, n);
}


static PyObject *seq_iter_from_func(PyObject *module, PyObject *args) {
    PyObject *n_obj;
    Py_ssize_t idx;

    if (!PyArg_ParseTuple(args, "On:iter_from", &n_obj, &idx)) {
        return nullptr;
    }

    btree_seq_state *state = get_btree_seq_state(module);

    BtreeSeqNode *n;

    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    return make_seq_from_iter(state, n, idx);
}


//
// Module definition
//

PyDoc_STRVAR(btree_seq_doc, "Native C++ implementation of persistent B+ tree sequence operations.");


static PyMethodDef btree_seq_methods[] = {
    {"from_iterable", (PyCFunction)seq_from_iterable_func, METH_VARARGS, "from_iterable(items)"},
    {"len_", (PyCFunction)seq_len_func, METH_VARARGS, "len_(root)"},
    {"get", (PyCFunction)seq_get_func, METH_VARARGS, "get(root, idx)"},
    {"slice", (PyCFunction)seq_slice_func, METH_VARARGS, "slice(root, start, stop)"},
    {"splice", (PyCFunction)seq_splice_func, METH_VARARGS, "splice(root, start, stop, items)"},
    {"iter", (PyCFunction)seq_iter_func, METH_VARARGS, "iter(root)"},
    {"riter", (PyCFunction)seq_riter_func, METH_VARARGS, "riter(root)"},
    {"iter_from", (PyCFunction)seq_iter_from_func, METH_VARARGS, "iter_from(root, idx)"},
    {nullptr, nullptr, 0, nullptr}
};


static int btree_seq_exec(PyObject *module) {
    btree_seq_state *state = get_btree_seq_state(module);

    state->BtreeSeqNodeType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &BtreeSeqNode_spec,
        nullptr
    );

    if (state->BtreeSeqNodeType == nullptr) {
        return -1;
    }

    if (PyModule_AddType(module, state->BtreeSeqNodeType) < 0) {
        return -1;
    }

    state->BtreeSeqIterType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &BtreeSeqIter_spec,
        nullptr
    );

    if (state->BtreeSeqIterType == nullptr) {
        return -1;
    }

    if (PyModule_AddType(module, state->BtreeSeqIterType) < 0) {
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


static int btree_seq_traverse(PyObject *module, visitproc visit, void *arg) {
    btree_seq_state *state = get_btree_seq_state(module);

    Py_VISIT(state->BtreeSeqNodeType);
    Py_VISIT(state->BtreeSeqIterType);

    return 0;
}


static int btree_seq_clear(PyObject *module) {
    btree_seq_state *state = get_btree_seq_state(module);

    Py_CLEAR(state->BtreeSeqNodeType);
    Py_CLEAR(state->BtreeSeqIterType);

    return 0;
}


static void btree_seq_free(void *module) {
    btree_seq_clear((PyObject *)module);
}


static struct PyModuleDef_Slot btree_seq_slots[] = {
    {Py_mod_exec, (void *)btree_seq_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, nullptr}
};


static struct PyModuleDef btree_seq_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = btree_seq_doc,
    .m_size = sizeof(btree_seq_state),
    .m_methods = btree_seq_methods,
    .m_slots = btree_seq_slots,
    .m_traverse = btree_seq_traverse,
    .m_clear = btree_seq_clear,
    .m_free = btree_seq_free,
};


extern "C" {

PyMODINIT_FUNC PyInit__btreeseq(void) {
    return PyModuleDef_Init(&btree_seq_module);
}

}
