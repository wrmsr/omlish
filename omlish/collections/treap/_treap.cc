// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <random>

//

#define _MODULE_NAME "_treap"
#define _PACKAGE_NAME "omlish.collections.treap"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//

typedef struct TreapNode TreapNode;
typedef struct TreapIter TreapIter;

typedef struct treap_state {
    PyTypeObject *TreapNodeType;
    PyTypeObject *TreapIterType;
} treap_state;

static inline treap_state *get_treap_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != nullptr);
    return (treap_state *)state;
}

//
// TreapNode
//

struct TreapNode {
    PyObject_HEAD
    PyObject *value;
    long priority;
    TreapNode *left;
    TreapNode *right;
    Py_ssize_t count;
};

static int TreapNode_traverse(TreapNode *self, visitproc visit, void *arg)
{
    Py_VISIT(self->value);
    Py_VISIT(self->left);
    Py_VISIT(self->right);
    return 0;
}

static int TreapNode_clear(TreapNode *self)
{
    Py_CLEAR(self->value);
    Py_CLEAR(self->left);
    Py_CLEAR(self->right);
    return 0;
}

static void TreapNode_dealloc(TreapNode *self)
{
    PyObject_GC_UnTrack(self);
    TreapNode_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *TreapNode_repr(TreapNode *self) {
    if (self->value == nullptr) {
        return PyUnicode_FromFormat(
            "TreapNode(<cleared>, priority=%ld, count=%zd)",
            self->priority,
            self->count
        );
    }

    return PyUnicode_FromFormat(
        "TreapNode(value=%R, priority=%ld, count=%zd)",
        self->value,
        self->priority,
        self->count
    );
}

static PyObject *TreapNode_get_value(TreapNode *self, void *closure)
{
    if (self->value == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, "TreapNode has been cleared");
        return nullptr;
    }
    return Py_NewRef(self->value);
}

static PyObject *TreapNode_get_priority(TreapNode *self, void *closure)
{
    return PyLong_FromLong(self->priority);
}

static PyObject *TreapNode_get_left(TreapNode *self, void *closure)
{
    if (self->left == nullptr) {
        Py_RETURN_NONE;
    }
    return Py_NewRef((PyObject *)self->left);
}

static PyObject *TreapNode_get_right(TreapNode *self, void *closure)
{
    if (self->right == nullptr) {
        Py_RETURN_NONE;
    }
    return Py_NewRef((PyObject *)self->right);
}

static PyObject *TreapNode_get_count(TreapNode *self, void *closure)
{
    return PyLong_FromSsize_t(self->count);
}

// Forward declaration - needs TreapIter type from module state.
static PyObject *TreapNode_iter(PyObject *self);

static PyGetSetDef TreapNode_getset[] = {
    {"value", (getter)TreapNode_get_value, nullptr, nullptr, nullptr},
    {"priority", (getter)TreapNode_get_priority, nullptr, nullptr, nullptr},
    {"left", (getter)TreapNode_get_left, nullptr, nullptr, nullptr},
    {"right", (getter)TreapNode_get_right, nullptr, nullptr, nullptr},
    {"count", (getter)TreapNode_get_count, nullptr, nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr}
};

static PyType_Slot TreapNode_slots[] = {
    {Py_tp_dealloc, (void *)TreapNode_dealloc},
    {Py_tp_traverse, (void *)TreapNode_traverse},
    {Py_tp_clear, (void *)TreapNode_clear},
    {Py_tp_repr, (void *)TreapNode_repr},
    {Py_tp_iter, (void *)TreapNode_iter},
    {Py_tp_getset, (void *)TreapNode_getset},
    {0, nullptr}
};

static PyType_Spec TreapNode_spec = {
    .name = _MODULE_FULL_NAME ".TreapNode",
    .basicsize = sizeof(TreapNode),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .slots = TreapNode_slots,
};

//
// TreapIter - inorder iterator over TreapNode tree
//
// Holds a single strong ref to the root node, which keeps the entire immutable tree alive. Stack entries and current
// pointer are borrowed refs into that tree.
//

struct TreapIter {
    PyObject_HEAD
    TreapNode *root;
    TreapNode **stack;
    Py_ssize_t stack_cap;
    Py_ssize_t stack_top;
    TreapNode *current;
};

static int TreapIter_traverse(TreapIter *self, visitproc visit, void *arg)
{
    Py_VISIT(self->root);
    return 0;
}

static int TreapIter_clear(TreapIter *self)
{
    Py_CLEAR(self->root);
    self->current = nullptr;
    self->stack_top = 0;
    return 0;
}

static void TreapIter_dealloc(TreapIter *self)
{
    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->root);
    PyMem_Free(self->stack);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *TreapIter_next(TreapIter *self)
{
    TreapNode *current = self->current;

    while (current != nullptr) {
        if (self->stack_top >= self->stack_cap) {
            Py_ssize_t new_cap = self->stack_cap * 2;
            TreapNode **new_stack = (TreapNode **) PyMem_Realloc(
                self->stack,
                (size_t) new_cap * sizeof(TreapNode *)
            );
            if (new_stack == nullptr) {
                return PyErr_NoMemory();
            }
            self->stack = new_stack;
            self->stack_cap = new_cap;
        }
        self->stack[self->stack_top++] = current;
        current = current->left;
    }

    if (self->stack_top == 0) {
        return nullptr;  // StopIteration
    }

    TreapNode *node = self->stack[--self->stack_top];
    self->current = node->right;

    if (node->value == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, "iterated over a cleared TreapNode");
        return nullptr;
    }

    return Py_NewRef(node->value);
}

static PyObject *TreapIter_iter(PyObject *self)
{
    return Py_NewRef(self);
}

static PyType_Slot TreapIter_slots[] = {
    {Py_tp_dealloc, (void *)TreapIter_dealloc},
    {Py_tp_traverse, (void *)TreapIter_traverse},
    {Py_tp_clear, (void *)TreapIter_clear},
    {Py_tp_iter, (void *)TreapIter_iter},
    {Py_tp_iternext, (void *)TreapIter_next},
    {0, nullptr}
};

static PyType_Spec TreapIter_spec = {
    .name = _MODULE_FULL_NAME ".TreapIter",
    .basicsize = sizeof(TreapIter),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .slots = TreapIter_slots,
};

// TreapNode.__iter__ implementation

static PyObject *TreapNode_iter(PyObject *self)
{
    TreapNode *node = (TreapNode *)self;
    if (node->value == nullptr) {
        PyErr_SetString(PyExc_ValueError, "cannot iterate a cleared TreapNode");
        return nullptr;
    }

    PyObject *module = PyType_GetModule(Py_TYPE(self));
    if (module == nullptr) {
        return nullptr;
    }
    treap_state *state = get_treap_state(module);

    TreapIter *iter = PyObject_GC_New(TreapIter, state->TreapIterType);
    if (iter == nullptr) {
        return nullptr;
    }

    iter->root = (TreapNode *)Py_NewRef(self);
    iter->stack_cap = 64;
    iter->stack = (TreapNode **)PyMem_Malloc((size_t)iter->stack_cap * sizeof(TreapNode *));
    if (iter->stack == nullptr) {
        Py_DECREF(iter);
        return PyErr_NoMemory();
    }
    iter->stack_top = 0;
    iter->current = node;

    PyObject_GC_Track(iter);
    return (PyObject *)iter;
}

//
// Helpers
//

static long new_priority()
{
    thread_local std::mt19937 rng{std::random_device{}()};
    return (long)rng();
}

// Comparator helper. Returns 0 on success, -1 on error.
// *out is set to negative / zero / positive per comparison.
// When cmp is nullptr, uses richcompare (equivalent to lang.cmp).
static int do_cmp(PyObject *cmp, PyObject *a, PyObject *b, int *out)
{
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

static int parse_node_arg(treap_state *state, PyObject *obj, TreapNode **out)
{
    if (obj == Py_None) {
        *out = nullptr;
        return 0;
    }
    if (Py_TYPE(obj) == state->TreapNodeType) {
        *out = (TreapNode *)obj;
        return 0;
    }
    PyErr_SetString(PyExc_TypeError, "expected TreapNode or None");
    return -1;
}

// Creates a new TreapNode.
//   value: borrowed ref (will be incref'd)
//   left, right: stolen refs (will NOT be incref'd; nullptr is valid; decref'd on alloc failure)
static TreapNode *make_node(
    treap_state *state,
    PyObject *value,
    long priority,
    TreapNode *left,
    TreapNode *right)
{
    TreapNode *node = PyObject_GC_New(TreapNode, state->TreapNodeType);
    if (node == nullptr) {
        Py_XDECREF(left);
        Py_XDECREF(right);
        return nullptr;
    }

    node->value = Py_NewRef(value);
    node->priority = priority;
    node->left = left;
    node->right = right;
    node->count = 1 + (left ? left->count : 0) + (right ? right->count : 0);

    PyObject_GC_Track(node);
    return node;
}

// Converts internal TreapNode* result to PyObject* for return to Python.
//   non-null: returns it (transfers ownership)
//   null + exception: returns nullptr (propagates error)
//   null + no exception: returns Py_None
static inline PyObject *node_to_pyobject(TreapNode *node)
{
    if (node != nullptr) {
        return (PyObject *)node;
    }
    if (PyErr_Occurred()) {
        return nullptr;
    }
    Py_RETURN_NONE;
}

//
// Core treap algorithms
//
// Functions returning TreapNode* follow this convention:
//   - Success: returns new reference (may be nullptr for "empty/None")
//   - Error: returns nullptr with exception set
//   - Callers check PyErr_Occurred() when receiving nullptr
//

static TreapNode *treap_find_impl(
    treap_state *state,
    TreapNode *n,
    PyObject *v,
    PyObject *cmp)
{
    (void)state;

    while (n != nullptr) {
        int diff;
        if (do_cmp(cmp, n->value, v, &diff) < 0) {
            return nullptr;
        }

        if (diff == 0) {
            return (TreapNode *)Py_NewRef((PyObject *)n);
        } else if (diff < 0) {
            n = n->right;
        } else {
            n = n->left;
        }
    }

    return nullptr;
}

// split returns 0 on success, -1 on error. Output params receive new refs (or nullptr).
static int treap_split_impl(
    treap_state *state,
    TreapNode *n,
    PyObject *v,
    PyObject *cmp,
    TreapNode **out_left,
    TreapNode **out_dupe,
    TreapNode **out_right)
{
    if (n == nullptr) {
        *out_left = nullptr;
        *out_dupe = nullptr;
        *out_right = nullptr;
        return 0;
    }

    int diff;
    if (do_cmp(cmp, n->value, v, &diff) < 0) {
        return -1;
    }

    if (diff < 0) {
        // n->value < v: n belongs in the left split, recurse into n->right.
        TreapNode *left_split, *dupe, *right_split;
        if (treap_split_impl(state, n->right, v, cmp, &left_split, &dupe, &right_split) < 0) {
            return -1;
        }

        TreapNode *new_left = make_node(
            state, n->value, n->priority,
            (TreapNode *)Py_XNewRef((PyObject *)n->left),  // borrow -> incref for steal
            left_split);  // stolen
        if (new_left == nullptr) {
            Py_XDECREF(dupe);
            Py_XDECREF(right_split);
            return -1;
        }

        *out_left = new_left;
        *out_dupe = dupe;
        *out_right = right_split;
        return 0;
    }

    if (diff > 0) {
        // n->value > v: n belongs in the right split, recurse into n->left.
        TreapNode *left_split, *dupe, *right_split;
        if (treap_split_impl(state, n->left, v, cmp, &left_split, &dupe, &right_split) < 0) {
            return -1;
        }

        TreapNode *new_right = make_node(
            state, n->value, n->priority,
            right_split,  // stolen
            (TreapNode *)Py_XNewRef((PyObject *)n->right));  // borrow -> incref for steal
        if (new_right == nullptr) {
            Py_XDECREF(left_split);
            Py_XDECREF(dupe);
            return -1;
        }

        *out_left = left_split;
        *out_dupe = dupe;
        *out_right = new_right;
        return 0;
    }

    // diff == 0: exact match. Isolate the duplicate node (no children).
    TreapNode *dupe = make_node(state, n->value, n->priority, nullptr, nullptr);
    if (dupe == nullptr) {
        return -1;
    }

    *out_left = (TreapNode *)Py_XNewRef((PyObject *)n->left);
    *out_dupe = dupe;
    *out_right = (TreapNode *)Py_XNewRef((PyObject *)n->right);
    return 0;
}

static TreapNode *treap_join_impl(
    treap_state *state,
    TreapNode *n,
    TreapNode *other)
{
    if (n == nullptr) {
        Py_XINCREF(other);
        return other;
    }
    if (other == nullptr) {
        Py_INCREF(n);
        return n;
    }

    if (n->priority >= other->priority) {
        TreapNode *right_joined = treap_join_impl(state, n->right, other);
        if (right_joined == nullptr && PyErr_Occurred()) {
            return nullptr;
        }

        return make_node(
            state,
            n->value,
            n->priority,
            (TreapNode *) Py_XNewRef((PyObject *)n->left),
            right_joined
        );
    } else {
        TreapNode *left_joined = treap_join_impl(state, n, other->left);
        if (left_joined == nullptr && PyErr_Occurred()) {
            return nullptr;
        }

        return make_node(
            state,
            other->value,
            other->priority,
            left_joined,
            (TreapNode *) Py_XNewRef((PyObject *)other->right)
        );
    }
}

static TreapNode *treap_union_impl(
    treap_state *state,
    TreapNode *n,
    TreapNode *other,
    PyObject *cmp,
    int overwrite)
{
    if (n == nullptr) {
        Py_XINCREF(other);
        return other;
    }
    if (other == nullptr) {
        Py_INCREF(n);
        return n;
    }

    if (n->priority < other->priority) {
        TreapNode *tmp = n;
        n = other;
        other = tmp;
        overwrite = !overwrite;
    }

    TreapNode *left, *dupe, *right;
    if (treap_split_impl(state, other, n->value, cmp, &left, &dupe, &right) < 0) {
        return nullptr;
    }

    PyObject *value = n->value;
    if (overwrite && dupe != nullptr) {
        value = dupe->value;
    }

    TreapNode *new_left = treap_union_impl(state, n->left, left, cmp, overwrite);
    Py_XDECREF(left);
    if (new_left == nullptr && PyErr_Occurred()) {
        Py_XDECREF(dupe);
        Py_XDECREF(right);
        return nullptr;
    }

    TreapNode *new_right = treap_union_impl(state, n->right, right, cmp, overwrite);
    Py_XDECREF(right);
    if (new_right == nullptr && PyErr_Occurred()) {
        Py_XDECREF(dupe);
        Py_XDECREF(new_left);
        return nullptr;
    }

    // make_node steals new_left and new_right
    TreapNode *result = make_node(state, value, n->priority, new_left, new_right);
    Py_XDECREF(dupe);
    return result;
}

static TreapNode *treap_intersect_impl(
    treap_state *state,
    TreapNode *n,
    TreapNode *other,
    PyObject *cmp)
{
    if (n == nullptr || other == nullptr) {
        return nullptr;
    }

    if (n->priority < other->priority) {
        TreapNode *tmp = n;
        n = other;
        other = tmp;
    }

    TreapNode *left, *found, *right;
    if (treap_split_impl(state, other, n->value, cmp, &left, &found, &right) < 0) {
        return nullptr;
    }

    TreapNode *new_left = treap_intersect_impl(state, n->left, left, cmp);
    Py_XDECREF(left);
    if (new_left == nullptr && PyErr_Occurred()) {
        Py_XDECREF(found);
        Py_XDECREF(right);
        return nullptr;
    }

    TreapNode *new_right = treap_intersect_impl(state, n->right, right, cmp);
    Py_XDECREF(right);
    if (new_right == nullptr && PyErr_Occurred()) {
        Py_XDECREF(found);
        Py_XDECREF(new_left);
        return nullptr;
    }

    if (found == nullptr) {
        TreapNode *result = treap_join_impl(state, new_left, new_right);
        Py_XDECREF(new_left);
        Py_XDECREF(new_right);
        return result;
    }

    Py_DECREF(found);
    return make_node(state, n->value, n->priority, new_left, new_right);
}

static TreapNode *treap_delete_impl(
    treap_state *state,
    TreapNode *n,
    PyObject *v,
    PyObject *cmp)
{
    TreapNode *left, *dupe, *right;
    if (treap_split_impl(state, n, v, cmp, &left, &dupe, &right) < 0) {
        return nullptr;
    }

    Py_XDECREF(dupe);

    TreapNode *result = treap_join_impl(state, left, right);
    Py_XDECREF(left);
    Py_XDECREF(right);
    return result;
}

static TreapNode *treap_diff_impl(
    treap_state *state,
    TreapNode *n,
    TreapNode *other,
    PyObject *cmp)
{
    if (n == nullptr || other == nullptr) {
        Py_XINCREF(n);
        return n;
    }

    if (n->priority >= other->priority) {
        TreapNode *left, *dupe, *right;
        if (treap_split_impl(state, other, n->value, cmp, &left, &dupe, &right) < 0) {
            return nullptr;
        }

        TreapNode *new_left = treap_diff_impl(state, n->left, left, cmp);
        Py_XDECREF(left);
        if (new_left == nullptr && PyErr_Occurred()) {
            Py_XDECREF(dupe);
            Py_XDECREF(right);
            return nullptr;
        }

        TreapNode *new_right = treap_diff_impl(state, n->right, right, cmp);
        Py_XDECREF(right);
        if (new_right == nullptr && PyErr_Occurred()) {
            Py_XDECREF(dupe);
            Py_XDECREF(new_left);
            return nullptr;
        }

        if (dupe != nullptr) {
            Py_DECREF(dupe);
            TreapNode *result = treap_join_impl(state, new_left, new_right);
            Py_XDECREF(new_left);
            Py_XDECREF(new_right);
            return result;
        }

        // dupe is nullptr, no need to decref
        return make_node(state, n->value, n->priority, new_left, new_right);
    }

    // n->priority < other->priority
    TreapNode *left, *unused_dupe, *right;
    if (treap_split_impl(state, n, other->value, cmp, &left, &unused_dupe, &right) < 0) {
        return nullptr;
    }
    Py_XDECREF(unused_dupe);

    TreapNode *new_left = treap_diff_impl(state, left, other->left, cmp);
    Py_XDECREF(left);
    if (new_left == nullptr && PyErr_Occurred()) {
        Py_XDECREF(right);
        return nullptr;
    }

    TreapNode *new_right = treap_diff_impl(state, right, other->right, cmp);
    Py_XDECREF(right);
    if (new_right == nullptr && PyErr_Occurred()) {
        Py_XDECREF(new_left);
        return nullptr;
    }

    TreapNode *result = treap_join_impl(state, new_left, new_right);
    Py_XDECREF(new_left);
    Py_XDECREF(new_right);
    return result;
}

static PyObject *treap_place_impl(
    treap_state *state,
    TreapNode *n,
    PyObject *v,
    PyObject *cmp,
    int desc)
{
    PyObject *list = PyList_New(0);
    if (list == nullptr) {
        return nullptr;
    }

    while (n != nullptr) {
        int diff;
        if (do_cmp(cmp, n->value, v, &diff) < 0) {
            Py_DECREF(list);
            return nullptr;
        }

        if (diff == 0) {
            if (PyList_Append(list, (PyObject *)n) < 0) {
                Py_DECREF(list);
                return nullptr;
            }
            break;
        } else if (diff < 0) {
            if (desc) {
                if (PyList_Append(list, (PyObject *)n) < 0) {
                    Py_DECREF(list);
                    return nullptr;
                }
            }
            n = n->right;
        } else {
            if (!desc) {
                if (PyList_Append(list, (PyObject *)n) < 0) {
                    Py_DECREF(list);
                    return nullptr;
                }
            }
            n = n->left;
        }
    }

    return list;
}

//
// Module-level Python functions
//

static PyObject *treap_new_func(PyObject *module, PyObject *args, PyObject *kwargs)
{
    static const char *kwlist[] = {"value", "priority", nullptr};
    PyObject *value;
    PyObject *priority_obj = Py_None;

    if (!PyArg_ParseTupleAndKeywords(
        args,
        kwargs,
        "O|O:new",
        (char **) kwlist,
        &value,
        &priority_obj
    )) {
        return nullptr;
    }

    long priority;
    if (priority_obj == Py_None) {
        priority = new_priority();
    } else {
        priority = PyLong_AsLong(priority_obj);
        if (priority == -1 && PyErr_Occurred())
            return nullptr;
    }

    treap_state *state = get_treap_state(module);
    return (PyObject *)make_node(state, value, priority, nullptr, nullptr);
}

static PyObject *treap_find_func(PyObject *module, PyObject *args)
{
    PyObject *n_obj, *v, *c_obj;
    if (!PyArg_ParseTuple(args, "OOO:find", &n_obj, &v, &c_obj)) {
        return nullptr;
    }

    treap_state *state = get_treap_state(module);

    TreapNode *n;
    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;
    return node_to_pyobject(treap_find_impl(state, n, v, cmp));
}

static PyObject *treap_place_func(PyObject *module, PyObject *args)
{
    PyObject *n_obj, *v, *c_obj, *desc_obj;
    if (!PyArg_ParseTuple(args, "OOOO:place", &n_obj, &v, &c_obj, &desc_obj)) {
        return nullptr;
    }

    treap_state *state = get_treap_state(module);

    TreapNode *n;
    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    int desc = PyObject_IsTrue(desc_obj);
    if (desc < 0) {
        return nullptr;
    }

    return treap_place_impl(state, n, v, cmp, desc);
}

static PyObject *treap_split_func(PyObject *module, PyObject *args)
{
    PyObject *n_obj, *v, *c_obj;
    if (!PyArg_ParseTuple(args, "OOO:split", &n_obj, &v, &c_obj)) {
        return nullptr;
    }

    treap_state *state = get_treap_state(module);

    TreapNode *n;
    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    TreapNode *left, *dupe, *right;
    if (treap_split_impl(state, n, v, cmp, &left, &dupe, &right) < 0) {
        return nullptr;
    }

    PyObject *left_py = (left != nullptr) ? (PyObject *)left : Py_NewRef(Py_None);
    PyObject *dupe_py = (dupe != nullptr) ? (PyObject *)dupe : Py_NewRef(Py_None);
    PyObject *right_py = (right != nullptr) ? (PyObject *)right : Py_NewRef(Py_None);

    PyObject *result = PyTuple_Pack(3, left_py, dupe_py, right_py);

    Py_DECREF(left_py);
    Py_DECREF(dupe_py);
    Py_DECREF(right_py);

    return result;
}

static PyObject *treap_union_func(PyObject *module, PyObject *args)
{
    PyObject *n_obj, *other_obj, *c_obj, *overwrite_obj;
    if (!PyArg_ParseTuple(args, "OOOO:union", &n_obj, &other_obj, &c_obj, &overwrite_obj)) {
        return nullptr;
    }

    treap_state *state = get_treap_state(module);

    TreapNode *n, *other;
    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }
    if (parse_node_arg(state, other_obj, &other) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;

    int overwrite = PyObject_IsTrue(overwrite_obj);
    if (overwrite < 0) {
        return nullptr;
    }

    return node_to_pyobject(treap_union_impl(state, n, other, cmp, overwrite));
}

static PyObject *treap_intersect_func(PyObject *module, PyObject *args)
{
    PyObject *n_obj, *other_obj, *c_obj;
    if (!PyArg_ParseTuple(args, "OOO:intersect", &n_obj, &other_obj, &c_obj)) {
        return nullptr;
    }

    treap_state *state = get_treap_state(module);

    TreapNode *n, *other;
    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }
    if (parse_node_arg(state, other_obj, &other) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;
    return node_to_pyobject(treap_intersect_impl(state, n, other, cmp));
}

static PyObject *treap_delete_func(PyObject *module, PyObject *args)
{
    PyObject *n_obj, *v, *c_obj;
    if (!PyArg_ParseTuple(args, "OOO:delete", &n_obj, &v, &c_obj)) {
        return nullptr;
    }

    treap_state *state = get_treap_state(module);

    TreapNode *n;
    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;
    return node_to_pyobject(treap_delete_impl(state, n, v, cmp));
}

static PyObject *treap_diff_func(PyObject *module, PyObject *args)
{
    PyObject *n_obj, *other_obj, *c_obj;
    if (!PyArg_ParseTuple(args, "OOO:diff", &n_obj, &other_obj, &c_obj)) {
        return nullptr;
    }

    treap_state *state = get_treap_state(module);

    TreapNode *n, *other;
    if (parse_node_arg(state, n_obj, &n) < 0) {
        return nullptr;
    }
    if (parse_node_arg(state, other_obj, &other) < 0) {
        return nullptr;
    }

    PyObject *cmp = (c_obj == Py_None) ? nullptr : c_obj;
    return node_to_pyobject(treap_diff_impl(state, n, other, cmp));
}

//
// Module definition
//

PyDoc_STRVAR(treap_doc, "Native C++ implementation of persistent treap operations.");

static PyMethodDef treap_methods[] = {
    {"new", (PyCFunction)treap_new_func, METH_VARARGS | METH_KEYWORDS, "new(value, *, priority=None)"},
    {"find", (PyCFunction)treap_find_func, METH_VARARGS, "find(n, v, c)"},
    {"place", (PyCFunction)treap_place_func, METH_VARARGS, "place(n, v, c, desc)"},
    {"split", (PyCFunction)treap_split_func, METH_VARARGS, "split(n, v, c)"},
    {"union", (PyCFunction)treap_union_func, METH_VARARGS, "union(n, other, c, overwrite)"},
    {"intersect", (PyCFunction)treap_intersect_func, METH_VARARGS, "intersect(n, other, c)"},
    {"delete", (PyCFunction)treap_delete_func, METH_VARARGS, "delete(n, v, c)"},
    {"diff", (PyCFunction)treap_diff_func, METH_VARARGS, "diff(n, other, c)"},
    {nullptr, nullptr, 0, nullptr}
};

static int treap_exec(PyObject *module)
{
    treap_state *state = get_treap_state(module);

    state->TreapNodeType = (PyTypeObject *) PyType_FromModuleAndSpec(
        module,
        &TreapNode_spec,
        nullptr
    );
    if (state->TreapNodeType == nullptr) {
        return -1;
    }

    if (PyModule_AddType(module, state->TreapNodeType) < 0) {
        return -1;
    }

    state->TreapIterType = (PyTypeObject *) PyType_FromModuleAndSpec(
        module,
        &TreapIter_spec,
        nullptr
    );
    if (state->TreapIterType == nullptr) {
        return -1;
    }

    return 0;
}

static int treap_traverse(PyObject *module, visitproc visit, void *arg)
{
    treap_state *state = get_treap_state(module);
    Py_VISIT(state->TreapNodeType);
    Py_VISIT(state->TreapIterType);
    return 0;
}

static int treap_clear(PyObject *module)
{
    treap_state *state = get_treap_state(module);
    Py_CLEAR(state->TreapNodeType);
    Py_CLEAR(state->TreapIterType);
    return 0;
}

static void treap_free(void *module)
{
    treap_clear((PyObject *)module);
}

static struct PyModuleDef_Slot treap_slots[] = {
    {Py_mod_exec, (void *)treap_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, nullptr}
};

static struct PyModuleDef treap_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = treap_doc,
    .m_size = sizeof(treap_state),
    .m_methods = treap_methods,
    .m_slots = treap_slots,
    .m_traverse = treap_traverse,
    .m_clear = treap_clear,
    .m_free = treap_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__treap(void)
{
    return PyModuleDef_Init(&treap_module);
}

}
