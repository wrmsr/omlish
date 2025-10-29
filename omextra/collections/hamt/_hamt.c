// @omlish-cext
//
// PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
// --------------------------------------------
//
// 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
// ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
// documentation.
//
// 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
// royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
// works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
// Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
// 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in
// Python alone or in any derivative version prepared by Licensee.
//
// 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
// wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
// any such work a brief summary of the changes made to Python.
//
// 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
// EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
// OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
// RIGHTS.
//
// 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
// DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
// ADVISED OF THE POSSIBILITY THEREOF.
//
// 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
//
// 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
// venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
// name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
//
// 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
// License Agreement.
//
// https://github.com/python/cpython/commit/aa18fd55d575a04e3aa782fedcd08dced26676e0
//
#define PY_SSIZE_T_CLEAN

#include "Python.h"

#include <stddef.h>               // offsetof()

#if PY_VERSION_HEX < 0x030D0000
#  error "This extension requires CPython 3.13+"
#endif

////

/*
HAMT tree is shaped by hashes of keys. Every group of 5 bits of a hash denotes
the exact position of the key in one level of the tree. Since we're using
32 bit hashes, we can have at most 7 such levels. Although if there are
two distinct keys with equal hashes, they will have to occupy the same
cell in the 7th level of the tree -- so we'd put them in a "collision" node.
Which brings the total possible tree depth to 8. Read more about the actual
layout of the HAMT tree in `hamt.c`.

This constant is used to define a datastucture for storing iteration state.
*/
#define _Py_HAMT_MAX_TREE_DEPTH 8


/* Abstract tree node. */
typedef struct {
    PyObject_HEAD
} HamtNode;


/* An HAMT immutable mapping collection. */
typedef struct {
    PyObject_HEAD
    HamtNode *h_root;
    PyObject *h_weakreflist;
    Py_ssize_t h_count;
} HamtObject;


typedef struct {
    PyObject_VAR_HEAD
    uint32_t b_bitmap;
    PyObject *b_array[1];
} HamtNode_Bitmap;


/* A struct to hold the state of depth-first traverse of the tree.

   HAMT is an immutable collection.  Iterators will hold a strong reference
   to it, and every node in the HAMT has strong references to its children.

   So for iterators, we can implement zero allocations and zero reference
   inc/dec depth-first iteration.

   - i_nodes: an array of seven pointers to tree nodes
   - i_level: the current node in i_nodes
   - i_pos: an array of positions within nodes in i_nodes.
*/
typedef struct {
    HamtNode *i_nodes[_Py_HAMT_MAX_TREE_DEPTH];
    Py_ssize_t i_pos[_Py_HAMT_MAX_TREE_DEPTH];
    int8_t i_level;
} HamtIteratorState;


/* Base iterator object.

   Contains the iteration state, a pointer to the HAMT tree,
   and a pointer to the 'yield function'.  The latter is a simple
   function that returns a key/value tuple for the 'Items' iterator,
   just a key for the 'Keys' iterator, and a value for the 'Values'
   iterator.
*/
typedef struct {
    PyObject_HEAD
    HamtObject *hi_obj;
    HamtIteratorState hi_iter;
    binaryfunc hi_yield;
} HamtIterator;


////

#define _MODULE_NAME "_hamt"
#define _PACKAGE_NAME "omextra.collections.hamt"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//

typedef struct hamt_module_state {
    /* Type objects */
    PyTypeObject *Hamt_Type;
    PyTypeObject *HamtItems_Type;
    PyTypeObject *HamtKeys_Type;
    PyTypeObject *HamtValues_Type;
    PyTypeObject *Hamt_ArrayNode_Type;
    PyTypeObject *Hamt_BitmapNode_Type;
    PyTypeObject *Hamt_CollisionNode_Type;

    /* Singleton objects */
    HamtObject *empty_hamt;
    HamtNode_Bitmap *empty_bitmap_node;
} hamt_module_state;

static inline hamt_module_state * get_hamt_module_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (hamt_module_state *)state;
}

static inline hamt_module_state * get_hamt_state_from_type(PyTypeObject *type)
{
    PyObject *module = PyType_GetModule(type);
    assert(module != NULL);
    return get_hamt_module_state(module);
}

static inline hamt_module_state * get_hamt_state_from_obj(PyObject *obj)
{
    PyTypeObject *type = Py_TYPE(obj);
    return get_hamt_state_from_type(type);
}

////

// Population count: count the number of 1's in 'x'
// (number of bits set to 1), also known as the hamming weight.
//
// Implementation note. CPUID is not used, to test if x86 POPCNT instruction
// can be used, to keep the implementation simple. For example, Visual Studio
// __popcnt() is not used this reason. The clang and GCC builtin function can
// use the x86 POPCNT instruction if the target architecture has SSE4a or
// newer.
static inline int
_popcount32(uint32_t x)
{
#if (defined(__clang__) || defined(__GNUC__))

#if SIZEOF_INT >= 4
    Py_BUILD_ASSERT(sizeof(x) <= sizeof(unsigned int));
    return __builtin_popcount(x);
#else
    // The C standard guarantees that unsigned long will always be big enough
    // to hold a uint32_t value without losing information.
    Py_BUILD_ASSERT(sizeof(x) <= sizeof(unsigned long));
    return __builtin_popcountl(x);
#endif

#else
    // 32-bit SWAR (SIMD Within A Register) popcount

    // Binary: 0 1 0 1 ...
    const uint32_t M1 = 0x55555555;
    // Binary: 00 11 00 11. ..
    const uint32_t M2 = 0x33333333;
    // Binary: 0000 1111 0000 1111 ...
    const uint32_t M4 = 0x0F0F0F0F;

    // Put count of each 2 bits into those 2 bits
    x = x - ((x >> 1) & M1);
    // Put count of each 4 bits into those 4 bits
    x = (x & M2) + ((x >> 2) & M2);
    // Put count of each 8 bits into those 8 bits
    x = (x + (x >> 4)) & M4;
    // Sum of the 4 byte counts.
    // Take care when considering changes to the next line. Portability and
    // correctness are delicate here, thanks to C's "integer promotions" (C99
    // §6.3.1.1p2). On machines where the `int` type has width greater than 32
    // bits, `x` will be promoted to an `int`, and following C's "usual
    // arithmetic conversions" (C99 §6.3.1.8), the multiplication will be
    // performed as a multiplication of two `unsigned int` operands. In this
    // case it's critical that we cast back to `uint32_t` in order to keep only
    // the least significant 32 bits. On machines where the `int` type has
    // width no greater than 32, the multiplication is of two 32-bit unsigned
    // integer types, and the (uint32_t) cast is a no-op. In both cases, we
    // avoid the risk of undefined behaviour due to overflow of a
    // multiplication of signed integer types.
    return (uint32_t)(x * 0x01010101U) >> 24;
#endif
}

////

/* Create a new HAMT immutable mapping. */
HamtObject * _Hamt_New(hamt_module_state *state);

/* Return a new collection based on "o", but with an additional
   key/val pair. */
HamtObject * _Hamt_Assoc(HamtObject *o, PyObject *key, PyObject *val);

/* Return a new collection based on "o", but without "key". */
HamtObject * _Hamt_Without(HamtObject *o, PyObject *key);

/* Find "key" in the "o" collection.

   Return:
   - -1: An error occurred.
   - 0: "key" wasn't found in "o".
   - 1: "key" is in "o"; "*val" is set to its value (a borrowed ref).
*/
int _Hamt_Find(HamtObject *o, PyObject *key, PyObject **val);

/* Check if "v" is equal to "w".

   Return:
   - 0: v != w
   - 1: v == w
   - -1: An error occurred.
*/
int _Hamt_Eq(HamtObject *v, HamtObject *w);

/* Return the size of "o"; equivalent of "len(o)". */
Py_ssize_t _Hamt_Len(HamtObject *o);

/* Return a Keys iterator over "o". */
PyObject * _Hamt_NewIterKeys(HamtObject *o);

/* Return a Values iterator over "o". */
PyObject * _Hamt_NewIterValues(HamtObject *o);

/* Return a Items iterator over "o". */
PyObject * _Hamt_NewIterItems(HamtObject *o);

////

/* Type check helper - checks if object is a HAMT by comparing against module state type */
static inline int
Hamt_Check(PyObject *o)
{
    PyTypeObject *type = Py_TYPE(o);
    PyObject *mod = PyType_GetModule(type);
    if (mod == NULL) {
        // Not a heap type or not from a module, definitely not our HAMT
        PyErr_Clear();
        return 0;
    }
    hamt_module_state *state = get_hamt_module_state(mod);
    return Py_IS_TYPE(o, state->Hamt_Type);
}


/*
This file provides an implementation of an immutable mapping using the
Hash Array Mapped Trie (or HAMT) datastructure.

This design allows to have:

1. Efficient copy: immutable mappings can be copied by reference,
   making it an O(1) operation.

2. Efficient mutations: due to structural sharing, only a portion of
   the trie needs to be copied when the collection is mutated.  The
   cost of set/delete operations is O(log N).

3. Efficient lookups: O(log N).

(where N is number of key/value items in the immutable mapping.)


HAMT
====

The core idea of HAMT is that the shape of the trie is encoded into the
hashes of keys.

Say we want to store a K/V pair in our mapping.  First, we calculate the
hash of K, let's say it's 19830128, or in binary:

    0b1001011101001010101110000 = 19830128

Now let's partition this bit representation of the hash into blocks of
5 bits each:

    0b00_00000_10010_11101_00101_01011_10000 = 19830128
          (6)   (5)   (4)   (3)   (2)   (1)

Each block of 5 bits represents a number between 0 and 31.  So if we have
a tree that consists of nodes, each of which is an array of 32 pointers,
those 5-bit blocks will encode a position on a single tree level.

For example, storing the key K with hash 19830128, results in the following
tree structure:

                     (array of 32 pointers)
                     +---+ -- +----+----+----+ -- +----+
  root node          | 0 | .. | 15 | 16 | 17 | .. | 31 |   0b10000 = 16 (1)
  (level 1)          +---+ -- +----+----+----+ -- +----+
                                      |
                     +---+ -- +----+----+----+ -- +----+
  a 2nd level node   | 0 | .. | 10 | 11 | 12 | .. | 31 |   0b01011 = 11 (2)
                     +---+ -- +----+----+----+ -- +----+
                                      |
                     +---+ -- +----+----+----+ -- +----+
  a 3rd level node   | 0 | .. | 04 | 05 | 06 | .. | 31 |   0b00101 = 5  (3)
                     +---+ -- +----+----+----+ -- +----+
                                      |
                     +---+ -- +----+----+----+----+
  a 4th level node   | 0 | .. | 04 | 29 | 30 | 31 |        0b11101 = 29 (4)
                     +---+ -- +----+----+----+----+
                                      |
                     +---+ -- +----+----+----+ -- +----+
  a 5th level node   | 0 | .. | 17 | 18 | 19 | .. | 31 |   0b10010 = 18 (5)
                     +---+ -- +----+----+----+ -- +----+
                                      |
                       +--------------+
                       |
                     +---+ -- +----+----+----+ -- +----+
  a 6th level node   | 0 | .. | 15 | 16 | 17 | .. | 31 |   0b00000 = 0  (6)
                     +---+ -- +----+----+----+ -- +----+
                       |
                       V -- our value (or collision)

To rehash: for a K/V pair, the hash of K encodes where in the tree V will
be stored.

To optimize memory footprint and handle hash collisions, our implementation
uses three different types of nodes:

 * A Bitmap node;
 * An Array node;
 * A Collision node.

Because we implement an immutable dictionary, our nodes are also
immutable.  Therefore, when we need to modify a node, we copy it, and
do that modification to the copy.


Array Nodes
-----------

These nodes are very simple.  Essentially they are arrays of 32 pointers
we used to illustrate the high-level idea in the previous section.

We use Array nodes only when we need to store more than 16 pointers
in a single node.

Array nodes do not store key objects or value objects.  They are used
only as an indirection level - their pointers point to other nodes in
the tree.


Bitmap Node
-----------

Allocating a new 32-pointers array for every node of our tree would be
very expensive.  Unless we store millions of keys, most of tree nodes would
be very sparse.

When we have less than 16 elements in a node, we don't want to use the
Array node, that would mean that we waste a lot of memory.  Instead,
we can use bitmap compression and can have just as many pointers
as we need!

Bitmap nodes consist of two fields:

1. An array of pointers.  If a Bitmap node holds N elements, the
   array will be of N pointers.

2. A 32bit integer -- a bitmap field.  If an N-th bit is set in the
   bitmap, it means that the node has an N-th element.

For example, say we need to store a 3 elements sparse array:

   +---+  --  +---+  --  +----+  --  +----+
   | 0 |  ..  | 4 |  ..  | 11 |  ..  | 17 |
   +---+  --  +---+  --  +----+  --  +----+
                |          |           |
                o1         o2          o3

We allocate a three-pointer Bitmap node.  Its bitmap field will be
then set to:

   0b_00100_00010_00000_10000 == (1 << 17) | (1 << 11) | (1 << 4)

To check if our Bitmap node has an I-th element we can do:

   bitmap & (1 << I)


And here's a formula to calculate a position in our pointer array
which would correspond to an I-th element:

   popcount(bitmap & ((1 << I) - 1))


Let's break it down:

 * `popcount` is a function that returns a number of bits set to 1;

 * `((1 << I) - 1)` is a mask to filter the bitmask to contain bits
   set to the *right* of our bit.


So for our 17, 11, and 4 indexes:

 * bitmap & ((1 << 17) - 1) == 0b100000010000 => 2 bits are set => index is 2.

 * bitmap & ((1 << 11) - 1) == 0b10000 => 1 bit is set => index is 1.

 * bitmap & ((1 << 4) - 1) == 0b0 => 0 bits are set => index is 0.


To conclude: Bitmap nodes are just like Array nodes -- they can store
a number of pointers, but use bitmap compression to eliminate unused
pointers.


Bitmap nodes have two pointers for each item:

  +----+----+----+----+  --  +----+----+
  | k1 | v1 | k2 | v2 |  ..  | kN | vN |
  +----+----+----+----+  --  +----+----+

When kI == NULL, vI points to another tree level.

When kI != NULL, the actual key object is stored in kI, and its
value is stored in vI.


Collision Nodes
---------------

Collision nodes are simple arrays of pointers -- two pointers per
key/value.  When there's a hash collision, say for k1/v1 and k2/v2
we have `hash(k1)==hash(k2)`.  Then our collision node will be:

  +----+----+----+----+
  | k1 | v1 | k2 | v2 |
  +----+----+----+----+


Tree Structure
--------------

All nodes are PyObjects.

The `HamtObject` object has a pointer to the root node (h_root),
and has a length field (h_count).

High-level functions accept a HamtObject object and dispatch to
lower-level functions depending on what kind of node h_root points to.


Operations
==========

There are three fundamental operations on an immutable dictionary:

1. "o.assoc(k, v)" will return a new immutable dictionary, that will be
   a copy of "o", but with the "k/v" item set.

   Functions in this file:

        hamt_node_assoc, hamt_node_bitmap_assoc,
        hamt_node_array_assoc, hamt_node_collision_assoc

   `hamt_node_assoc` function accepts a node object, and calls
   other functions depending on its actual type.

2. "o.find(k)" will lookup key "k" in "o".

   Functions:

        hamt_node_find, hamt_node_bitmap_find,
        hamt_node_array_find, hamt_node_collision_find

3. "o.without(k)" will return a new immutable dictionary, that will be
   a copy of "o", buth without the "k" key.

   Functions:

        hamt_node_without, hamt_node_bitmap_without,
        hamt_node_array_without, hamt_node_collision_without


Further Reading
===============

1. http://blog.higher-order.net/2009/09/08/understanding-clojures-persistenthashmap-deftwice.html

2. http://blog.higher-order.net/2010/08/16/assoc-and-clojures-persistenthashmap-part-ii.html

3. Clojure's PersistentHashMap implementation:
   https://github.com/clojure/clojure/blob/master/src/jvm/clojure/lang/PersistentHashMap.java


Debug
=====

The HAMT datatype is accessible for testing purposes under the
`_testinternalcapi` module:

    >>> from _testinternalcapi import hamt
    >>> h = hamt()
    >>> h2 = h.set('a', 2)
    >>> h3 = h2.set('b', 3)
    >>> list(h3)
    ['a', 'b']

When CPython is built in debug mode, a '__dump__()' method is available
to introspect the tree:

    >>> print(h3.__dump__())
    HAMT(len=2):
        BitmapNode(size=4 count=2 bitmap=0b110 id=0x10eb9d9e8):
            'a': 2
            'b': 3
*/


static inline int
IS_ARRAY_NODE(HamtNode *node)
{
    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)node);
    return Py_IS_TYPE(node, state->Hamt_ArrayNode_Type);
}

static inline int
IS_BITMAP_NODE(HamtNode *node)
{
    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)node);
    return Py_IS_TYPE(node, state->Hamt_BitmapNode_Type);
}

static inline int
IS_COLLISION_NODE(HamtNode *node)
{
    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)node);
    return Py_IS_TYPE(node, state->Hamt_CollisionNode_Type);
}


/* Return type for 'find' (lookup a key) functions.

   * F_ERROR - an error occurred;
   * F_NOT_FOUND - the key was not found;
   * F_FOUND - the key was found.
*/
typedef enum {F_ERROR, F_NOT_FOUND, F_FOUND} hamt_find_t;


/* Return type for 'without' (delete a key) functions.

   * W_ERROR - an error occurred;
   * W_NOT_FOUND - the key was not found: there's nothing to delete;
   * W_EMPTY - the key was found: the node/tree would be empty
     if the key is deleted;
   * W_NEWNODE - the key was found: a new node/tree is returned
     without that key.
*/
typedef enum {W_ERROR, W_NOT_FOUND, W_EMPTY, W_NEWNODE} hamt_without_t;


/* Low-level iterator protocol type.

   * I_ITEM - a new item has been yielded;
   * I_END - the whole tree was visited (similar to StopIteration).
*/
typedef enum {I_ITEM, I_END} hamt_iter_t;


#define HAMT_ARRAY_NODE_SIZE 32


typedef struct {
    PyObject_HEAD
    HamtNode *a_array[HAMT_ARRAY_NODE_SIZE];
    Py_ssize_t a_count;
} HamtNode_Array;


typedef struct {
    PyObject_VAR_HEAD
    int32_t c_hash;
    PyObject *c_array[1];
} HamtNode_Collision;


static HamtObject *
hamt_alloc(hamt_module_state *state);

static HamtNode *
hamt_node_assoc(HamtNode *node,
                uint32_t shift, int32_t hash,
                PyObject *key, PyObject *val, int* added_leaf);

static hamt_without_t
hamt_node_without(HamtNode *node,
                  uint32_t shift, int32_t hash,
                  PyObject *key,
                  HamtNode **new_node);

static hamt_find_t
hamt_node_find(HamtNode *node,
               uint32_t shift, int32_t hash,
               PyObject *key, PyObject **val);

#ifdef Py_DEBUG
static int
hamt_node_dump(HamtNode *node,
               _PyUnicodeWriter *writer, int level);
#endif

static HamtNode *
hamt_node_array_new(hamt_module_state *state, Py_ssize_t);

static HamtNode *
hamt_node_collision_new(hamt_module_state *state, int32_t hash, Py_ssize_t size);

static inline Py_ssize_t
hamt_node_collision_count(HamtNode_Collision *node);


#ifdef Py_DEBUG
static void
_hamt_node_array_validate(void *obj_raw)
{
    PyObject *obj = _PyObject_CAST(obj_raw);
    assert(IS_ARRAY_NODE(obj));
    HamtNode_Array *node = (HamtNode_Array*)obj;
    Py_ssize_t i = 0, count = 0;
    for (; i < HAMT_ARRAY_NODE_SIZE; i++) {
        if (node->a_array[i] != NULL) {
            count++;
        }
    }
    assert(count == node->a_count);
}

#define VALIDATE_ARRAY_NODE(NODE) \
    do { _hamt_node_array_validate(NODE); } while (0);
#else
#define VALIDATE_ARRAY_NODE(NODE)
#endif


/* Returns -1 on error */
static inline int32_t
hamt_hash(PyObject *o)
{
    Py_hash_t hash = PyObject_Hash(o);

#if SIZEOF_PY_HASH_T <= 4
    return hash;
#else
    if (hash == -1) {
        /* exception */
        return -1;
    }

    /* While it's somewhat suboptimal to reduce Python's 64 bit hash to
       32 bits via XOR, it seems that the resulting hash function
       is good enough (this is also how Long type is hashed in Java.)
       Storing 10, 100, 1000 Python strings results in a relatively
       shallow and uniform tree structure.

       Also it's worth noting that it would be possible to adapt the tree
       structure to 64 bit hashes, but that would increase memory pressure
       and provide little to no performance benefits for collections with
       fewer than billions of key/value pairs.

       Important: do not change this hash reducing function. There are many
       tests that need an exact tree shape to cover all code paths and
       we do that by specifying concrete values for test data's `__hash__`.
       If this function is changed most of the regression tests would
       become useless.
    */
    int32_t xored = (int32_t)(hash & 0xffffffffl) ^ (int32_t)(hash >> 32);
    return xored == -1 ? -2 : xored;
#endif
}

static inline uint32_t
hamt_mask(int32_t hash, uint32_t shift)
{
    return (((uint32_t)hash >> shift) & 0x01f);
}

static inline uint32_t
hamt_bitpos(int32_t hash, uint32_t shift)
{
    return (uint32_t)1 << hamt_mask(hash, shift);
}

static inline uint32_t
hamt_bitindex(uint32_t bitmap, uint32_t bit)
{
    return (uint32_t)_popcount32(bitmap & (bit - 1));
}


/////////////////////////////////// Dump Helpers
#ifdef Py_DEBUG

static int
_hamt_dump_ident(_PyUnicodeWriter *writer, int level)
{
    /* Write `'    ' * level` to the `writer` */
    PyObject *str = NULL;
    PyObject *num = NULL;
    PyObject *res = NULL;
    int ret = -1;

    str = PyUnicode_FromString("    ");
    if (str == NULL) {
        goto error;
    }

    num = PyLong_FromLong((long)level);
    if (num == NULL) {
        goto error;
    }

    res = PyNumber_Multiply(str, num);
    if (res == NULL) {
        goto error;
    }

    ret = _PyUnicodeWriter_WriteStr(writer, res);

error:
    Py_XDECREF(res);
    Py_XDECREF(str);
    Py_XDECREF(num);
    return ret;
}

static int
_hamt_dump_format(_PyUnicodeWriter *writer, const char *format, ...)
{
    /* A convenient helper combining _PyUnicodeWriter_WriteStr and
       PyUnicode_FromFormatV.
    */
    PyObject* msg;
    int ret;

    va_list vargs;
    va_start(vargs, format);
    msg = PyUnicode_FromFormatV(format, vargs);
    va_end(vargs);

    if (msg == NULL) {
        return -1;
    }

    ret = _PyUnicodeWriter_WriteStr(writer, msg);
    Py_DECREF(msg);
    return ret;
}

#endif  /* Py_DEBUG */
/////////////////////////////////// Bitmap Node


static HamtNode *
hamt_node_bitmap_new(hamt_module_state *state, Py_ssize_t size)
{
    /* Create a new bitmap node of size 'size' */

    HamtNode_Bitmap *node;
    Py_ssize_t i;

    if (size == 0) {
        /* Since bitmap nodes are immutable, we can cache the instance
           for size=0 and reuse it whenever we need an empty bitmap node.
        */
        return (HamtNode *)Py_NewRef(state->empty_bitmap_node);
    }

    assert(size >= 0);
    assert(size % 2 == 0);

    /* No freelist; allocate a new bitmap node */
    node = PyObject_GC_NewVar(
        HamtNode_Bitmap, state->Hamt_BitmapNode_Type, size);
    if (node == NULL) {
        return NULL;
    }

    Py_SET_SIZE(node, size);

    for (i = 0; i < size; i++) {
        node->b_array[i] = NULL;
    }

    node->b_bitmap = 0;

    PyObject_GC_Track(node);

    return (HamtNode *)node;
}

static inline Py_ssize_t
hamt_node_bitmap_count(HamtNode_Bitmap *node)
{
    return Py_SIZE(node) / 2;
}

static HamtNode_Bitmap *
hamt_node_bitmap_clone(HamtNode_Bitmap *node)
{
    /* Clone a bitmap node; return a new one with the same child notes. */

    HamtNode_Bitmap *clone;
    Py_ssize_t i;

    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)node);
    clone = (HamtNode_Bitmap *)hamt_node_bitmap_new(state, Py_SIZE(node));
    if (clone == NULL) {
        return NULL;
    }

    for (i = 0; i < Py_SIZE(node); i++) {
        clone->b_array[i] = Py_XNewRef(node->b_array[i]);
    }

    clone->b_bitmap = node->b_bitmap;
    return clone;
}

static HamtNode_Bitmap *
hamt_node_bitmap_clone_without(HamtNode_Bitmap *o, uint32_t bit)
{
    assert(bit & o->b_bitmap);
    assert(hamt_node_bitmap_count(o) > 1);

    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)o);
    HamtNode_Bitmap *new = (HamtNode_Bitmap *)hamt_node_bitmap_new(
        state, Py_SIZE(o) - 2);
    if (new == NULL) {
        return NULL;
    }

    uint32_t idx = hamt_bitindex(o->b_bitmap, bit);
    uint32_t key_idx = 2 * idx;
    uint32_t val_idx = key_idx + 1;
    uint32_t i;

    for (i = 0; i < key_idx; i++) {
        new->b_array[i] = Py_XNewRef(o->b_array[i]);
    }

    assert(Py_SIZE(o) >= 0 && Py_SIZE(o) <= 32);
    for (i = val_idx + 1; i < (uint32_t)Py_SIZE(o); i++) {
        new->b_array[i - 2] = Py_XNewRef(o->b_array[i]);
    }

    new->b_bitmap = o->b_bitmap & ~bit;
    return new;
}

static HamtNode *
hamt_node_new_bitmap_or_collision(
    hamt_module_state *state,
    uint32_t shift,
    PyObject *key1, PyObject *val1,
    int32_t key2_hash,
    PyObject *key2, PyObject *val2)
{
    /* Helper method.  Creates a new node for key1/val and key2/val2
       pairs.

       If key1 hash is equal to the hash of key2, a Collision node
       will be created.  If they are not equal, a Bitmap node is
       created.
    */

    int32_t key1_hash = hamt_hash(key1);
    if (key1_hash == -1) {
        return NULL;
    }

    if (key1_hash == key2_hash) {
        HamtNode_Collision *n;
        n = (HamtNode_Collision *)hamt_node_collision_new(state, key1_hash, 4);
        if (n == NULL) {
            return NULL;
        }

        n->c_array[0] = Py_NewRef(key1);
        n->c_array[1] = Py_NewRef(val1);

        n->c_array[2] = Py_NewRef(key2);
        n->c_array[3] = Py_NewRef(val2);

        return (HamtNode *)n;
    }
    else {
        int added_leaf = 0;
        HamtNode *n = hamt_node_bitmap_new(state, 0);
        if (n == NULL) {
            return NULL;
        }

        HamtNode *n2 = hamt_node_assoc(
            n, shift, key1_hash, key1, val1, &added_leaf);
        Py_DECREF(n);
        if (n2 == NULL) {
            return NULL;
        }

        n = hamt_node_assoc(n2, shift, key2_hash, key2, val2, &added_leaf);
        Py_DECREF(n2);
        if (n == NULL) {
            return NULL;
        }

        return n;
    }
}

static HamtNode *
hamt_node_bitmap_assoc(HamtNode_Bitmap *self,
                       uint32_t shift, int32_t hash,
                       PyObject *key, PyObject *val, int* added_leaf)
{
    /* assoc operation for bitmap nodes.

       Return: a new node, or self if key/val already is in the
       collection.

       'added_leaf' is later used in '_Hamt_Assoc' to determine if
       `hamt.set(key, val)` increased the size of the collection.
    */

    uint32_t bit = hamt_bitpos(hash, shift);
    uint32_t idx = hamt_bitindex(self->b_bitmap, bit);

    /* Bitmap node layout:

    +------+------+------+------+  ---  +------+------+
    | key1 | val1 | key2 | val2 |  ...  | keyN | valN |
    +------+------+------+------+  ---  +------+------+
    where `N < Py_SIZE(node)`.

    The `node->b_bitmap` field is a bitmap.  For a given
    `(shift, hash)` pair we can determine:

     - If this node has the corresponding key/val slots.
     - The index of key/val slots.
    */

    if (self->b_bitmap & bit) {
        /* The key is set in this node */

        uint32_t key_idx = 2 * idx;
        uint32_t val_idx = key_idx + 1;

        assert(val_idx < (size_t)Py_SIZE(self));

        PyObject *key_or_null = self->b_array[key_idx];
        PyObject *val_or_node = self->b_array[val_idx];

        if (key_or_null == NULL) {
            /* key is NULL.  This means that we have a few keys
               that have the same (hash, shift) pair. */

            assert(val_or_node != NULL);

            HamtNode *sub_node = hamt_node_assoc(
                (HamtNode *)val_or_node,
                shift + 5, hash, key, val, added_leaf);
            if (sub_node == NULL) {
                return NULL;
            }

            if (val_or_node == (PyObject *)sub_node) {
                Py_DECREF(sub_node);
                return (HamtNode *)Py_NewRef(self);
            }

            HamtNode_Bitmap *ret = hamt_node_bitmap_clone(self);
            if (ret == NULL) {
                return NULL;
            }
            Py_SETREF(ret->b_array[val_idx], (PyObject*)sub_node);
            return (HamtNode *)ret;
        }

        assert(key != NULL);
        /* key is not NULL.  This means that we have only one other
           key in this collection that matches our hash for this shift. */

        int comp_err = PyObject_RichCompareBool(key, key_or_null, Py_EQ);
        if (comp_err < 0) {  /* exception in __eq__ */
            return NULL;
        }
        if (comp_err == 1) {  /* key == key_or_null */
            if (val == val_or_node) {
                /* we already have the same key/val pair; return self. */
                return (HamtNode *)Py_NewRef(self);
            }

            /* We're setting a new value for the key we had before.
               Make a new bitmap node with a replaced value, and return it. */
            HamtNode_Bitmap *ret = hamt_node_bitmap_clone(self);
            if (ret == NULL) {
                return NULL;
            }
            Py_SETREF(ret->b_array[val_idx], Py_NewRef(val));
            return (HamtNode *)ret;
        }

        /* It's a new key, and it has the same index as *one* another key.
           We have a collision.  We need to create a new node which will
           combine the existing key and the key we're adding.

           `hamt_node_new_bitmap_or_collision` will either create a new
           Collision node if the keys have identical hashes, or
           a new Bitmap node.
        */
        HamtNode *sub_node = hamt_node_new_bitmap_or_collision(
            get_hamt_state_from_obj((PyObject*)self),
            shift + 5,
            key_or_null, val_or_node,  /* existing key/val */
            hash,
            key, val  /* new key/val */
        );
        if (sub_node == NULL) {
            return NULL;
        }

        HamtNode_Bitmap *ret = hamt_node_bitmap_clone(self);
        if (ret == NULL) {
            Py_DECREF(sub_node);
            return NULL;
        }
        Py_SETREF(ret->b_array[key_idx], NULL);
        Py_SETREF(ret->b_array[val_idx], (PyObject *)sub_node);

        *added_leaf = 1;
        return (HamtNode *)ret;
    }
    else {
        /* There was no key before with the same (shift,hash). */

        uint32_t n = (uint32_t)_popcount32(self->b_bitmap);

        if (n >= 16) {
            /* When we have a situation where we want to store more
               than 16 nodes at one level of the tree, we no longer
               want to use the Bitmap node with bitmap encoding.

               Instead we start using an Array node, which has
               simpler (faster) implementation at the expense of
               having preallocated 32 pointers for its keys/values
               pairs.

               Small hamt objects (<30 keys) usually don't have any
               Array nodes at all.  Between ~30 and ~400 keys hamt
               objects usually have one Array node, and usually it's
               a root node.
            */

            uint32_t jdx = hamt_mask(hash, shift);
            /* 'jdx' is the index of where the new key should be added
               in the new Array node we're about to create. */

            HamtNode *empty = NULL;
            HamtNode_Array *new_node = NULL;
            HamtNode *res = NULL;

            hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);

            /* Create a new Array node. */
            new_node = (HamtNode_Array *)hamt_node_array_new(state, n + 1);
            if (new_node == NULL) {
                goto fin;
            }

            /* Create an empty bitmap node for the next
               hamt_node_assoc call. */
            empty = hamt_node_bitmap_new(state, 0);
            if (empty == NULL) {
                goto fin;
            }

            /* Make a new bitmap node for the key/val we're adding.
               Set that bitmap node to new-array-node[jdx]. */
            new_node->a_array[jdx] = hamt_node_assoc(
                empty, shift + 5, hash, key, val, added_leaf);
            if (new_node->a_array[jdx] == NULL) {
                goto fin;
            }

            /* Copy existing key/value pairs from the current Bitmap
               node to the new Array node we've just created. */
            Py_ssize_t i, j;
            for (i = 0, j = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
                if (((self->b_bitmap >> i) & 1) != 0) {
                    /* Ensure we don't accidentally override `jdx` element
                       we set few lines above.
                    */
                    assert(new_node->a_array[i] == NULL);

                    if (self->b_array[j] == NULL) {
                        new_node->a_array[i] =
                            (HamtNode *)Py_NewRef(self->b_array[j + 1]);
                    }
                    else {
                        int32_t rehash = hamt_hash(self->b_array[j]);
                        if (rehash == -1) {
                            goto fin;
                        }

                        new_node->a_array[i] = hamt_node_assoc(
                            empty, shift + 5,
                            rehash,
                            self->b_array[j],
                            self->b_array[j + 1],
                            added_leaf);

                        if (new_node->a_array[i] == NULL) {
                            goto fin;
                        }
                    }
                    j += 2;
                }
            }

            VALIDATE_ARRAY_NODE(new_node)

            /* That's it! */
            res = (HamtNode *)new_node;

        fin:
            Py_XDECREF(empty);
            if (res == NULL) {
                Py_XDECREF(new_node);
            }
            return res;
        }
        else {
            /* We have less than 16 keys at this level; let's just
               create a new bitmap node out of this node with the
               new key/val pair added. */

            uint32_t key_idx = 2 * idx;
            uint32_t val_idx = key_idx + 1;
            uint32_t i;

            *added_leaf = 1;

            /* Allocate new Bitmap node which can have one more key/val
               pair in addition to what we have already. */
            hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);
            HamtNode_Bitmap *new_node =
                (HamtNode_Bitmap *)hamt_node_bitmap_new(state, 2 * (n + 1));
            if (new_node == NULL) {
                return NULL;
            }

            /* Copy all keys/values that will be before the new key/value
               we are adding. */
            for (i = 0; i < key_idx; i++) {
                new_node->b_array[i] = Py_XNewRef(self->b_array[i]);
            }

            /* Set the new key/value to the new Bitmap node. */
            new_node->b_array[key_idx] = Py_NewRef(key);
            new_node->b_array[val_idx] = Py_NewRef(val);

            /* Copy all keys/values that will be after the new key/value
               we are adding. */
            assert(Py_SIZE(self) >= 0 && Py_SIZE(self) <= 32);
            for (i = key_idx; i < (uint32_t)Py_SIZE(self); i++) {
                new_node->b_array[i + 2] = Py_XNewRef(self->b_array[i]);
            }

            new_node->b_bitmap = self->b_bitmap | bit;
            return (HamtNode *)new_node;
        }
    }
}

static hamt_without_t
hamt_node_bitmap_without(HamtNode_Bitmap *self,
                         uint32_t shift, int32_t hash,
                         PyObject *key,
                         HamtNode **new_node)
{
    uint32_t bit = hamt_bitpos(hash, shift);
    if ((self->b_bitmap & bit) == 0) {
        return W_NOT_FOUND;
    }

    uint32_t idx = hamt_bitindex(self->b_bitmap, bit);

    uint32_t key_idx = 2 * idx;
    uint32_t val_idx = key_idx + 1;

    PyObject *key_or_null = self->b_array[key_idx];
    PyObject *val_or_node = self->b_array[val_idx];

    if (key_or_null == NULL) {
        /* key == NULL means that 'value' is another tree node. */

        HamtNode *sub_node = NULL;

        hamt_without_t res = hamt_node_without(
            (HamtNode *)val_or_node,
            shift + 5, hash, key, &sub_node);

        switch (res) {
            case W_EMPTY:
                /* It's impossible for us to receive a W_EMPTY here:

                    - Array nodes are converted to Bitmap nodes when
                      we delete 16th item from them;

                    - Collision nodes are converted to Bitmap when
                      there is one item in them;

                    - Bitmap node's without() inlines single-item
                      sub-nodes.

                   So in no situation we can have a single-item
                   Bitmap child of another Bitmap node.
                */
                Py_UNREACHABLE();

            case W_NEWNODE: {
                assert(sub_node != NULL);

                if (IS_BITMAP_NODE(sub_node)) {
                    HamtNode_Bitmap *sub_tree = (HamtNode_Bitmap *)sub_node;
                    if (hamt_node_bitmap_count(sub_tree) == 1 &&
                            sub_tree->b_array[0] != NULL)
                    {
                        /* A bitmap node with one key/value pair.  Just
                           merge it into this node.

                           Note that we don't inline Bitmap nodes that
                           have a NULL key -- those nodes point to another
                           tree level, and we cannot simply move tree levels
                           up or down.
                        */

                        HamtNode_Bitmap *clone = hamt_node_bitmap_clone(self);
                        if (clone == NULL) {
                            Py_DECREF(sub_node);
                            return W_ERROR;
                        }

                        PyObject *key = sub_tree->b_array[0];
                        PyObject *val = sub_tree->b_array[1];

                        Py_XSETREF(clone->b_array[key_idx], Py_NewRef(key));
                        Py_SETREF(clone->b_array[val_idx], Py_NewRef(val));

                        Py_DECREF(sub_tree);

                        *new_node = (HamtNode *)clone;
                        return W_NEWNODE;
                    }
                }

#ifdef Py_DEBUG
                /* Ensure that Collision.without implementation
                   converts to Bitmap nodes itself.
                */
                if (IS_COLLISION_NODE(sub_node)) {
                    assert(hamt_node_collision_count(
                            (HamtNode_Collision*)sub_node) > 1);
                }
#endif

                HamtNode_Bitmap *clone = hamt_node_bitmap_clone(self);
                if (clone == NULL) {
                    return W_ERROR;
                }

                Py_SETREF(clone->b_array[val_idx],
                          (PyObject *)sub_node);  /* borrow */

                *new_node = (HamtNode *)clone;
                return W_NEWNODE;
            }

            case W_ERROR:
            case W_NOT_FOUND:
                assert(sub_node == NULL);
                return res;

            default:
                Py_UNREACHABLE();
        }
    }
    else {
        /* We have a regular key/value pair */

        int cmp = PyObject_RichCompareBool(key_or_null, key, Py_EQ);
        if (cmp < 0) {
            return W_ERROR;
        }
        if (cmp == 0) {
            return W_NOT_FOUND;
        }

        if (hamt_node_bitmap_count(self) == 1) {
            return W_EMPTY;
        }

        *new_node = (HamtNode *)
            hamt_node_bitmap_clone_without(self, bit);
        if (*new_node == NULL) {
            return W_ERROR;
        }

        return W_NEWNODE;
    }
}

static hamt_find_t
hamt_node_bitmap_find(HamtNode_Bitmap *self,
                      uint32_t shift, int32_t hash,
                      PyObject *key, PyObject **val)
{
    /* Lookup a key in a Bitmap node. */

    uint32_t bit = hamt_bitpos(hash, shift);
    uint32_t idx;
    uint32_t key_idx;
    uint32_t val_idx;
    PyObject *key_or_null;
    PyObject *val_or_node;
    int comp_err;

    if ((self->b_bitmap & bit) == 0) {
        return F_NOT_FOUND;
    }

    idx = hamt_bitindex(self->b_bitmap, bit);
    key_idx = idx * 2;
    val_idx = key_idx + 1;

    assert(val_idx < (size_t)Py_SIZE(self));

    key_or_null = self->b_array[key_idx];
    val_or_node = self->b_array[val_idx];

    if (key_or_null == NULL) {
        /* There are a few keys that have the same hash at the current shift
           that match our key.  Dispatch the lookup further down the tree. */
        assert(val_or_node != NULL);
        return hamt_node_find((HamtNode *)val_or_node,
                              shift + 5, hash, key, val);
    }

    /* We have only one key -- a potential match.  Let's compare if the
       key we are looking at is equal to the key we are looking for. */
    assert(key != NULL);
    comp_err = PyObject_RichCompareBool(key, key_or_null, Py_EQ);
    if (comp_err < 0) {  /* exception in __eq__ */
        return F_ERROR;
    }
    if (comp_err == 1) {  /* key == key_or_null */
        *val = val_or_node;
        return F_FOUND;
    }

    return F_NOT_FOUND;
}

static int
hamt_node_bitmap_traverse(HamtNode_Bitmap *self, visitproc visit, void *arg)
{
    /* Bitmap's tp_traverse */

    Py_ssize_t i;

    for (i = Py_SIZE(self); --i >= 0; ) {
        Py_VISIT(self->b_array[i]);
    }

    return 0;
}

static void
hamt_node_bitmap_dealloc(HamtNode_Bitmap *self)
{
    /* Bitmap's tp_dealloc */

    Py_ssize_t len = Py_SIZE(self);
    Py_ssize_t i;

    if (Py_SIZE(self) == 0) {
        /* The empty node is managed by the module state. */
        hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);
        assert(self == state->empty_bitmap_node);
#ifdef Py_DEBUG
        _Py_FatalRefcountError("deallocating the empty hamt node bitmap singleton");
#else
        return;
#endif
    }

    PyObject_GC_UnTrack(self);
    Py_TRASHCAN_BEGIN(self, hamt_node_bitmap_dealloc)

    if (len > 0) {
        i = len;
        while (--i >= 0) {
            Py_XDECREF(self->b_array[i]);
        }
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
    Py_TRASHCAN_END
}

#ifdef Py_DEBUG
static int
hamt_node_bitmap_dump(HamtNode_Bitmap *node,
                      _PyUnicodeWriter *writer, int level)
{
    /* Debug build: __dump__() method implementation for Bitmap nodes. */

    Py_ssize_t i;
    PyObject *tmp1;
    PyObject *tmp2;

    if (_hamt_dump_ident(writer, level + 1)) {
        goto error;
    }

    if (_hamt_dump_format(writer, "BitmapNode(size=%zd count=%zd ",
                          Py_SIZE(node), Py_SIZE(node) / 2))
    {
        goto error;
    }

    tmp1 = PyLong_FromUnsignedLong(node->b_bitmap);
    if (tmp1 == NULL) {
        goto error;
    }
    // Format as binary using format spec 'b' (like f"{num:b}" in Python)
    PyObject *format_spec = PyUnicode_FromString("b");
    if (format_spec == NULL) {
        Py_DECREF(tmp1);
        goto error;
    }
    tmp2 = PyObject_Format(tmp1, format_spec);
    Py_DECREF(format_spec);
    Py_DECREF(tmp1);
    if (tmp2 == NULL) {
        goto error;
    }
    if (_hamt_dump_format(writer, "bitmap=%S id=%p):\n", tmp2, node)) {
        Py_DECREF(tmp2);
        goto error;
    }
    Py_DECREF(tmp2);

    for (i = 0; i < Py_SIZE(node); i += 2) {
        PyObject *key_or_null = node->b_array[i];
        PyObject *val_or_node = node->b_array[i + 1];

        if (_hamt_dump_ident(writer, level + 2)) {
            goto error;
        }

        if (key_or_null == NULL) {
            if (_hamt_dump_format(writer, "NULL:\n")) {
                goto error;
            }

            if (hamt_node_dump((HamtNode *)val_or_node,
                               writer, level + 2))
            {
                goto error;
            }
        }
        else {
            if (_hamt_dump_format(writer, "%R: %R", key_or_null,
                                  val_or_node))
            {
                goto error;
            }
        }

        if (_hamt_dump_format(writer, "\n")) {
            goto error;
        }
    }

    return 0;
error:
    return -1;
}
#endif  /* Py_DEBUG */


/////////////////////////////////// Collision Node


static HamtNode *
hamt_node_collision_new(hamt_module_state *state, int32_t hash, Py_ssize_t size)
{
    /* Create a new Collision node. */

    HamtNode_Collision *node;
    Py_ssize_t i;

    assert(size >= 4);
    assert(size % 2 == 0);

    node = PyObject_GC_NewVar(
        HamtNode_Collision, state->Hamt_CollisionNode_Type, size);
    if (node == NULL) {
        return NULL;
    }

    for (i = 0; i < size; i++) {
        node->c_array[i] = NULL;
    }

    Py_SET_SIZE(node, size);
    node->c_hash = hash;

    PyObject_GC_Track(node);

    return (HamtNode *)node;
}

static hamt_find_t
hamt_node_collision_find_index(HamtNode_Collision *self, PyObject *key,
                               Py_ssize_t *idx)
{
    /* Lookup `key` in the Collision node `self`.  Set the index of the
       found key to 'idx'. */

    Py_ssize_t i;
    PyObject *el;

    for (i = 0; i < Py_SIZE(self); i += 2) {
        el = self->c_array[i];

        assert(el != NULL);
        int cmp = PyObject_RichCompareBool(key, el, Py_EQ);
        if (cmp < 0) {
            return F_ERROR;
        }
        if (cmp == 1) {
            *idx = i;
            return F_FOUND;
        }
    }

    return F_NOT_FOUND;
}

static HamtNode *
hamt_node_collision_assoc(HamtNode_Collision *self,
                          uint32_t shift, int32_t hash,
                          PyObject *key, PyObject *val, int* added_leaf)
{
    /* Set a new key to this level (currently a Collision node)
       of the tree. */

    if (hash == self->c_hash) {
        /* The hash of the 'key' we are adding matches the hash of
           other keys in this Collision node. */

        Py_ssize_t key_idx = -1;
        hamt_find_t found;
        HamtNode_Collision *new_node;
        Py_ssize_t i;
        hamt_module_state *state;

        /* Let's try to lookup the new 'key', maybe we already have it. */
        found = hamt_node_collision_find_index(self, key, &key_idx);
        switch (found) {
            case F_ERROR:
                /* Exception. */
                return NULL;

            case F_NOT_FOUND:
                /* This is a totally new key.  Clone the current node,
                   add a new key/value to the cloned node. */

                state = get_hamt_state_from_obj((PyObject*)self);
                new_node = (HamtNode_Collision *)hamt_node_collision_new(
                    state, self->c_hash, Py_SIZE(self) + 2);
                if (new_node == NULL) {
                    return NULL;
                }

                for (i = 0; i < Py_SIZE(self); i++) {
                    new_node->c_array[i] = Py_NewRef(self->c_array[i]);
                }

                new_node->c_array[i] = Py_NewRef(key);
                new_node->c_array[i + 1] = Py_NewRef(val);

                *added_leaf = 1;
                return (HamtNode *)new_node;

            case F_FOUND:
                /* There's a key which is equal to the key we are adding. */

                assert(key_idx >= 0);
                assert(key_idx < Py_SIZE(self));
                Py_ssize_t val_idx = key_idx + 1;

                if (self->c_array[val_idx] == val) {
                    /* We're setting a key/value pair that's already set. */
                    return (HamtNode *)Py_NewRef(self);
                }

                /* We need to replace old value for the key
                   with a new value.  Create a new Collision node.*/
                hamt_module_state *state2 = get_hamt_state_from_obj((PyObject*)self);
                new_node = (HamtNode_Collision *)hamt_node_collision_new(
                    state2, self->c_hash, Py_SIZE(self));
                if (new_node == NULL) {
                    return NULL;
                }

                /* Copy all elements of the old node to the new one. */
                for (i = 0; i < Py_SIZE(self); i++) {
                    new_node->c_array[i] = Py_NewRef(self->c_array[i]);
                }

                /* Replace the old value with the new value for the our key. */
                Py_SETREF(new_node->c_array[val_idx], Py_NewRef(val));

                return (HamtNode *)new_node;

            default:
                Py_UNREACHABLE();
        }
    }
    else {
        /* The hash of the new key is different from the hash that
           all keys of this Collision node have.

           Create a Bitmap node inplace with two children:
           key/value pair that we're adding, and the Collision node
           we're replacing on this tree level.
        */

        HamtNode_Bitmap *new_node;
        HamtNode *assoc_res;

        hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);
        new_node = (HamtNode_Bitmap *)hamt_node_bitmap_new(state, 2);
        if (new_node == NULL) {
            return NULL;
        }
        new_node->b_bitmap = hamt_bitpos(self->c_hash, shift);
        new_node->b_array[1] = Py_NewRef(self);

        assoc_res = hamt_node_bitmap_assoc(
            new_node, shift, hash, key, val, added_leaf);
        Py_DECREF(new_node);
        return assoc_res;
    }
}

static inline Py_ssize_t
hamt_node_collision_count(HamtNode_Collision *node)
{
    return Py_SIZE(node) / 2;
}

static hamt_without_t
hamt_node_collision_without(HamtNode_Collision *self,
                            uint32_t shift, int32_t hash,
                            PyObject *key,
                            HamtNode **new_node)
{
    if (hash != self->c_hash) {
        return W_NOT_FOUND;
    }

    Py_ssize_t key_idx = -1;
    hamt_find_t found = hamt_node_collision_find_index(self, key, &key_idx);

    switch (found) {
        case F_ERROR:
            return W_ERROR;

        case F_NOT_FOUND:
            return W_NOT_FOUND;

        case F_FOUND:
            assert(key_idx >= 0);
            assert(key_idx < Py_SIZE(self));

            Py_ssize_t new_count = hamt_node_collision_count(self) - 1;

            if (new_count == 0) {
                /* The node has only one key/value pair and it's for the
                   key we're trying to delete.  So a new node will be empty
                   after the removal.
                */
                return W_EMPTY;
            }

            if (new_count == 1) {
                /* The node has two keys, and after deletion the
                   new Collision node would have one.  Collision nodes
                   with one key shouldn't exist, so convert it to a
                   Bitmap node.
                */
                hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);
                HamtNode_Bitmap *node = (HamtNode_Bitmap *)
                    hamt_node_bitmap_new(state, 2);
                if (node == NULL) {
                    return W_ERROR;
                }

                if (key_idx == 0) {
                    node->b_array[0] = Py_NewRef(self->c_array[2]);
                    node->b_array[1] = Py_NewRef(self->c_array[3]);
                }
                else {
                    assert(key_idx == 2);
                    node->b_array[0] = Py_NewRef(self->c_array[0]);
                    node->b_array[1] = Py_NewRef(self->c_array[1]);
                }

                node->b_bitmap = hamt_bitpos(hash, shift);

                *new_node = (HamtNode *)node;
                return W_NEWNODE;
            }

            /* Allocate a new Collision node with capacity for one
               less key/value pair */
            hamt_module_state *state3 = get_hamt_state_from_obj((PyObject*)self);
            HamtNode_Collision *new = (HamtNode_Collision *)
                hamt_node_collision_new(
                    state3, self->c_hash, Py_SIZE(self) - 2);
            if (new == NULL) {
                return W_ERROR;
            }

            /* Copy all other keys from `self` to `new` */
            Py_ssize_t i;
            for (i = 0; i < key_idx; i++) {
                new->c_array[i] = Py_NewRef(self->c_array[i]);
            }
            for (i = key_idx + 2; i < Py_SIZE(self); i++) {
                new->c_array[i - 2] = Py_NewRef(self->c_array[i]);
            }

            *new_node = (HamtNode*)new;
            return W_NEWNODE;

        default:
            Py_UNREACHABLE();
    }
}

static hamt_find_t
hamt_node_collision_find(HamtNode_Collision *self,
                         uint32_t shift, int32_t hash,
                         PyObject *key, PyObject **val)
{
    /* Lookup `key` in the Collision node `self`.  Set the value
       for the found key to 'val'. */

    Py_ssize_t idx = -1;
    hamt_find_t res;

    res = hamt_node_collision_find_index(self, key, &idx);
    if (res == F_ERROR || res == F_NOT_FOUND) {
        return res;
    }

    assert(idx >= 0);
    assert(idx + 1 < Py_SIZE(self));

    *val = self->c_array[idx + 1];
    assert(*val != NULL);

    return F_FOUND;
}


static int
hamt_node_collision_traverse(HamtNode_Collision *self,
                             visitproc visit, void *arg)
{
    /* Collision's tp_traverse */

    Py_ssize_t i;

    for (i = Py_SIZE(self); --i >= 0; ) {
        Py_VISIT(self->c_array[i]);
    }

    return 0;
}

static void
hamt_node_collision_dealloc(HamtNode_Collision *self)
{
    /* Collision's tp_dealloc */

    Py_ssize_t len = Py_SIZE(self);

    PyObject_GC_UnTrack(self);
    Py_TRASHCAN_BEGIN(self, hamt_node_collision_dealloc)

    if (len > 0) {

        while (--len >= 0) {
            Py_XDECREF(self->c_array[len]);
        }
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
    Py_TRASHCAN_END
}

#ifdef Py_DEBUG
static int
hamt_node_collision_dump(HamtNode_Collision *node,
                         _PyUnicodeWriter *writer, int level)
{
    /* Debug build: __dump__() method implementation for Collision nodes. */

    Py_ssize_t i;

    if (_hamt_dump_ident(writer, level + 1)) {
        goto error;
    }

    if (_hamt_dump_format(writer, "CollisionNode(size=%zd id=%p):\n",
                          Py_SIZE(node), node))
    {
        goto error;
    }

    for (i = 0; i < Py_SIZE(node); i += 2) {
        PyObject *key = node->c_array[i];
        PyObject *val = node->c_array[i + 1];

        if (_hamt_dump_ident(writer, level + 2)) {
            goto error;
        }

        if (_hamt_dump_format(writer, "%R: %R\n", key, val)) {
            goto error;
        }
    }

    return 0;
error:
    return -1;
}
#endif  /* Py_DEBUG */


/////////////////////////////////// Array Node


static HamtNode *
hamt_node_array_new(hamt_module_state *state, Py_ssize_t count)
{
    Py_ssize_t i;

    HamtNode_Array *node = PyObject_GC_New(
        HamtNode_Array, state->Hamt_ArrayNode_Type);
    if (node == NULL) {
        return NULL;
    }

    for (i = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
        node->a_array[i] = NULL;
    }

    node->a_count = count;

    PyObject_GC_Track(node);
    return (HamtNode *)node;
}

static HamtNode_Array *
hamt_node_array_clone(HamtNode_Array *node)
{
    HamtNode_Array *clone;
    Py_ssize_t i;

    VALIDATE_ARRAY_NODE(node)

    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)node);

    /* Create a new Array node. */
    clone = (HamtNode_Array *)hamt_node_array_new(state, node->a_count);
    if (clone == NULL) {
        return NULL;
    }

    /* Copy all elements from the current Array node to the new one. */
    for (i = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
        clone->a_array[i] = (HamtNode*)Py_XNewRef(node->a_array[i]);
    }

    VALIDATE_ARRAY_NODE(clone)
    return clone;
}

static HamtNode *
hamt_node_array_assoc(HamtNode_Array *self,
                      uint32_t shift, int32_t hash,
                      PyObject *key, PyObject *val, int* added_leaf)
{
    /* Set a new key to this level (currently a Collision node)
       of the tree.

       Array nodes don't store values, they can only point to
       other nodes.  They are simple arrays of 32 BaseNode pointers/
     */

    uint32_t idx = hamt_mask(hash, shift);
    HamtNode *node = self->a_array[idx];
    HamtNode *child_node;
    HamtNode_Array *new_node;
    Py_ssize_t i;

    if (node == NULL) {
        /* There's no child node for the given hash.  Create a new
           Bitmap node for this key. */

        HamtNode_Bitmap *empty = NULL;

        /* Get an empty Bitmap node to work with. */
        hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);
        empty = (HamtNode_Bitmap *)hamt_node_bitmap_new(state, 0);
        if (empty == NULL) {
            return NULL;
        }

        /* Set key/val to the newly created empty Bitmap, thus
           creating a new Bitmap node with our key/value pair. */
        child_node = hamt_node_bitmap_assoc(
            empty,
            shift + 5, hash, key, val, added_leaf);
        Py_DECREF(empty);
        if (child_node == NULL) {
            return NULL;
        }

        /* Create a new Array node. */
        new_node = (HamtNode_Array *)hamt_node_array_new(state, self->a_count + 1);
        if (new_node == NULL) {
            Py_DECREF(child_node);
            return NULL;
        }

        /* Copy all elements from the current Array node to the
           new one. */
        for (i = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
            new_node->a_array[i] = (HamtNode*)Py_XNewRef(self->a_array[i]);
        }

        assert(new_node->a_array[idx] == NULL);
        new_node->a_array[idx] = child_node;  /* borrow */
        VALIDATE_ARRAY_NODE(new_node)
    }
    else {
        /* There's a child node for the given hash.
           Set the key to it./ */
        child_node = hamt_node_assoc(
            node, shift + 5, hash, key, val, added_leaf);
        if (child_node == NULL) {
            return NULL;
        }
        else if (child_node == (HamtNode *)self) {
            Py_DECREF(child_node);
            return (HamtNode *)self;
        }

        new_node = hamt_node_array_clone(self);
        if (new_node == NULL) {
            Py_DECREF(child_node);
            return NULL;
        }

        Py_SETREF(new_node->a_array[idx], child_node);  /* borrow */
        VALIDATE_ARRAY_NODE(new_node)
    }

    return (HamtNode *)new_node;
}

static hamt_without_t
hamt_node_array_without(HamtNode_Array *self,
                        uint32_t shift, int32_t hash,
                        PyObject *key,
                        HamtNode **new_node)
{
    uint32_t idx = hamt_mask(hash, shift);
    HamtNode *node = self->a_array[idx];

    if (node == NULL) {
        return W_NOT_FOUND;
    }

    HamtNode *sub_node = NULL;
    hamt_without_t res = hamt_node_without(
        (HamtNode *)node,
        shift + 5, hash, key, &sub_node);

    switch (res) {
        case W_NOT_FOUND:
        case W_ERROR:
            assert(sub_node == NULL);
            return res;

        case W_NEWNODE: {
            /* We need to replace a node at the `idx` index.
               Clone this node and replace.
            */
            assert(sub_node != NULL);

            HamtNode_Array *clone = hamt_node_array_clone(self);
            if (clone == NULL) {
                Py_DECREF(sub_node);
                return W_ERROR;
            }

            Py_SETREF(clone->a_array[idx], sub_node);  /* borrow */
            *new_node = (HamtNode*)clone;  /* borrow */
            return W_NEWNODE;
        }

        case W_EMPTY: {
            assert(sub_node == NULL);
            /* We need to remove a node at the `idx` index.
               Calculate the size of the replacement Array node.
            */
            Py_ssize_t new_count = self->a_count - 1;

            if (new_count == 0) {
                return W_EMPTY;
            }

            if (new_count >= 16) {
                /* We convert Bitmap nodes to Array nodes, when a
                   Bitmap node needs to store more than 15 key/value
                   pairs.  So we will create a new Array node if we
                   the number of key/values after deletion is still
                   greater than 15.
                */

                HamtNode_Array *new = hamt_node_array_clone(self);
                if (new == NULL) {
                    return W_ERROR;
                }
                new->a_count = new_count;
                Py_CLEAR(new->a_array[idx]);

                *new_node = (HamtNode*)new;  /* borrow */
                return W_NEWNODE;
            }

            /* New Array node would have less than 16 key/value
               pairs.  We need to create a replacement Bitmap node. */

            Py_ssize_t bitmap_size = new_count * 2;
            uint32_t bitmap = 0;

            hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);
            HamtNode_Bitmap *new = (HamtNode_Bitmap *)
                hamt_node_bitmap_new(state, bitmap_size);
            if (new == NULL) {
                return W_ERROR;
            }

            Py_ssize_t new_i = 0;
            for (uint32_t i = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
                if (i == idx) {
                    /* Skip the node we are deleting. */
                    continue;
                }

                HamtNode *node = self->a_array[i];
                if (node == NULL) {
                    /* Skip any missing nodes. */
                    continue;
                }

                bitmap |= 1U << i;

                if (IS_BITMAP_NODE(node)) {
                    HamtNode_Bitmap *child = (HamtNode_Bitmap *)node;

                    if (hamt_node_bitmap_count(child) == 1 &&
                            child->b_array[0] != NULL)
                    {
                        /* node is a Bitmap with one key/value pair, just
                           merge it into the new Bitmap node we're building.

                           Note that we don't inline Bitmap nodes that
                           have a NULL key -- those nodes point to another
                           tree level, and we cannot simply move tree levels
                           up or down.
                        */
                        PyObject *key = child->b_array[0];
                        PyObject *val = child->b_array[1];

                        new->b_array[new_i] = Py_NewRef(key);
                        new->b_array[new_i + 1] = Py_NewRef(val);
                    }
                    else {
                        new->b_array[new_i] = NULL;
                        new->b_array[new_i + 1] = Py_NewRef(node);
                    }
                }
                else {

#ifdef Py_DEBUG
                    if (IS_COLLISION_NODE(node)) {
                        Py_ssize_t child_count = hamt_node_collision_count(
                            (HamtNode_Collision*)node);
                        assert(child_count > 1);
                    }
                    else if (IS_ARRAY_NODE(node)) {
                        assert(((HamtNode_Array*)node)->a_count >= 16);
                    }
#endif

                    /* Just copy the node into our new Bitmap */
                    new->b_array[new_i] = NULL;
                    new->b_array[new_i + 1] = Py_NewRef(node);
                }

                new_i += 2;
            }

            new->b_bitmap = bitmap;
            *new_node = (HamtNode*)new;  /* borrow */
            return W_NEWNODE;
        }

        default:
            Py_UNREACHABLE();
    }
}

static hamt_find_t
hamt_node_array_find(HamtNode_Array *self,
                     uint32_t shift, int32_t hash,
                     PyObject *key, PyObject **val)
{
    /* Lookup `key` in the Array node `self`.  Set the value
       for the found key to 'val'. */

    uint32_t idx = hamt_mask(hash, shift);
    HamtNode *node;

    node = self->a_array[idx];
    if (node == NULL) {
        return F_NOT_FOUND;
    }

    /* Dispatch to the generic hamt_node_find */
    return hamt_node_find(node, shift + 5, hash, key, val);
}

static int
hamt_node_array_traverse(HamtNode_Array *self,
                         visitproc visit, void *arg)
{
    /* Array's tp_traverse */

    Py_ssize_t i;

    for (i = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
        Py_VISIT(self->a_array[i]);
    }

    return 0;
}

static void
hamt_node_array_dealloc(HamtNode_Array *self)
{
    /* Array's tp_dealloc */

    Py_ssize_t i;

    PyObject_GC_UnTrack(self);
    Py_TRASHCAN_BEGIN(self, hamt_node_array_dealloc)

    for (i = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
        Py_XDECREF(self->a_array[i]);
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
    Py_TRASHCAN_END
}

#ifdef Py_DEBUG
static int
hamt_node_array_dump(HamtNode_Array *node,
                     _PyUnicodeWriter *writer, int level)
{
    /* Debug build: __dump__() method implementation for Array nodes. */

    Py_ssize_t i;

    if (_hamt_dump_ident(writer, level + 1)) {
        goto error;
    }

    if (_hamt_dump_format(writer, "ArrayNode(id=%p):\n", node)) {
        goto error;
    }

    for (i = 0; i < HAMT_ARRAY_NODE_SIZE; i++) {
        if (node->a_array[i] == NULL) {
            continue;
        }

        if (_hamt_dump_ident(writer, level + 2)) {
            goto error;
        }

        if (_hamt_dump_format(writer, "%zd::\n", i)) {
            goto error;
        }

        if (hamt_node_dump(node->a_array[i], writer, level + 1)) {
            goto error;
        }

        if (_hamt_dump_format(writer, "\n")) {
            goto error;
        }
    }

    return 0;
error:
    return -1;
}
#endif  /* Py_DEBUG */


/////////////////////////////////// Node Dispatch


static HamtNode *
hamt_node_assoc(HamtNode *node,
                uint32_t shift, int32_t hash,
                PyObject *key, PyObject *val, int* added_leaf)
{
    /* Set key/value to the 'node' starting with the given shift/hash.
       Return a new node, or the same node if key/value already
       set.

       added_leaf will be set to 1 if key/value wasn't in the
       tree before.

       This method automatically dispatches to the suitable
       hamt_node_{nodetype}_assoc method.
    */

    if (IS_BITMAP_NODE(node)) {
        return hamt_node_bitmap_assoc(
            (HamtNode_Bitmap *)node,
            shift, hash, key, val, added_leaf);
    }
    else if (IS_ARRAY_NODE(node)) {
        return hamt_node_array_assoc(
            (HamtNode_Array *)node,
            shift, hash, key, val, added_leaf);
    }
    else {
        assert(IS_COLLISION_NODE(node));
        return hamt_node_collision_assoc(
            (HamtNode_Collision *)node,
            shift, hash, key, val, added_leaf);
    }
}

static hamt_without_t
hamt_node_without(HamtNode *node,
                  uint32_t shift, int32_t hash,
                  PyObject *key,
                  HamtNode **new_node)
{
    if (IS_BITMAP_NODE(node)) {
        return hamt_node_bitmap_without(
            (HamtNode_Bitmap *)node,
            shift, hash, key,
            new_node);
    }
    else if (IS_ARRAY_NODE(node)) {
        return hamt_node_array_without(
            (HamtNode_Array *)node,
            shift, hash, key,
            new_node);
    }
    else {
        assert(IS_COLLISION_NODE(node));
        return hamt_node_collision_without(
            (HamtNode_Collision *)node,
            shift, hash, key,
            new_node);
    }
}

static hamt_find_t
hamt_node_find(HamtNode *node,
               uint32_t shift, int32_t hash,
               PyObject *key, PyObject **val)
{
    /* Find the key in the node starting with the given shift/hash.

       If a value is found, the result will be set to F_FOUND, and
       *val will point to the found value object.

       If a value wasn't found, the result will be set to F_NOT_FOUND.

       If an exception occurs during the call, the result will be F_ERROR.

       This method automatically dispatches to the suitable
       hamt_node_{nodetype}_find method.
    */

    if (IS_BITMAP_NODE(node)) {
        return hamt_node_bitmap_find(
            (HamtNode_Bitmap *)node,
            shift, hash, key, val);

    }
    else if (IS_ARRAY_NODE(node)) {
        return hamt_node_array_find(
            (HamtNode_Array *)node,
            shift, hash, key, val);
    }
    else {
        assert(IS_COLLISION_NODE(node));
        return hamt_node_collision_find(
            (HamtNode_Collision *)node,
            shift, hash, key, val);
    }
}

#ifdef Py_DEBUG
static int
hamt_node_dump(HamtNode *node,
               _PyUnicodeWriter *writer, int level)
{
    /* Debug build: __dump__() method implementation for a node.

       This method automatically dispatches to the suitable
       hamt_node_{nodetype})_dump method.
    */

    if (IS_BITMAP_NODE(node)) {
        return hamt_node_bitmap_dump(
            (HamtNode_Bitmap *)node, writer, level);
    }
    else if (IS_ARRAY_NODE(node)) {
        return hamt_node_array_dump(
            (HamtNode_Array *)node, writer, level);
    }
    else {
        assert(IS_COLLISION_NODE(node));
        return hamt_node_collision_dump(
            (HamtNode_Collision *)node, writer, level);
    }
}
#endif  /* Py_DEBUG */


/////////////////////////////////// Iterators: Machinery


static hamt_iter_t
hamt_iterator_next(HamtIteratorState *iter, PyObject **key, PyObject **val);


static void
hamt_iterator_init(HamtIteratorState *iter, HamtNode *root)
{
    for (uint32_t i = 0; i < _Py_HAMT_MAX_TREE_DEPTH; i++) {
        iter->i_nodes[i] = NULL;
        iter->i_pos[i] = 0;
    }

    iter->i_level = 0;

    /* Note: we don't incref/decref nodes in i_nodes. */
    iter->i_nodes[0] = root;
}

static hamt_iter_t
hamt_iterator_bitmap_next(HamtIteratorState *iter,
                          PyObject **key, PyObject **val)
{
    int8_t level = iter->i_level;

    HamtNode_Bitmap *node = (HamtNode_Bitmap *)(iter->i_nodes[level]);
    Py_ssize_t pos = iter->i_pos[level];

    if (pos + 1 >= Py_SIZE(node)) {
#ifdef Py_DEBUG
        assert(iter->i_level >= 0);
        iter->i_nodes[iter->i_level] = NULL;
#endif
        iter->i_level--;
        return hamt_iterator_next(iter, key, val);
    }

    if (node->b_array[pos] == NULL) {
        iter->i_pos[level] = pos + 2;

        int8_t next_level = level + 1;
        assert(next_level < _Py_HAMT_MAX_TREE_DEPTH);
        iter->i_level = next_level;
        iter->i_pos[next_level] = 0;
        iter->i_nodes[next_level] = (HamtNode *)
            node->b_array[pos + 1];

        return hamt_iterator_next(iter, key, val);
    }

    *key = node->b_array[pos];
    *val = node->b_array[pos + 1];
    iter->i_pos[level] = pos + 2;
    return I_ITEM;
}

static hamt_iter_t
hamt_iterator_collision_next(HamtIteratorState *iter,
                             PyObject **key, PyObject **val)
{
    int8_t level = iter->i_level;

    HamtNode_Collision *node = (HamtNode_Collision *)(iter->i_nodes[level]);
    Py_ssize_t pos = iter->i_pos[level];

    if (pos + 1 >= Py_SIZE(node)) {
#ifdef Py_DEBUG
        assert(iter->i_level >= 0);
        iter->i_nodes[iter->i_level] = NULL;
#endif
        iter->i_level--;
        return hamt_iterator_next(iter, key, val);
    }

    *key = node->c_array[pos];
    *val = node->c_array[pos + 1];
    iter->i_pos[level] = pos + 2;
    return I_ITEM;
}

static hamt_iter_t
hamt_iterator_array_next(HamtIteratorState *iter,
                         PyObject **key, PyObject **val)
{
    int8_t level = iter->i_level;

    HamtNode_Array *node = (HamtNode_Array *)(iter->i_nodes[level]);
    Py_ssize_t pos = iter->i_pos[level];

    if (pos >= HAMT_ARRAY_NODE_SIZE) {
#ifdef Py_DEBUG
        assert(iter->i_level >= 0);
        iter->i_nodes[iter->i_level] = NULL;
#endif
        iter->i_level--;
        return hamt_iterator_next(iter, key, val);
    }

    for (Py_ssize_t i = pos; i < HAMT_ARRAY_NODE_SIZE; i++) {
        if (node->a_array[i] != NULL) {
            iter->i_pos[level] = i + 1;

            int8_t next_level = level + 1;
            assert(next_level < _Py_HAMT_MAX_TREE_DEPTH);
            iter->i_pos[next_level] = 0;
            iter->i_nodes[next_level] = node->a_array[i];
            iter->i_level = next_level;

            return hamt_iterator_next(iter, key, val);
        }
    }

#ifdef Py_DEBUG
        assert(iter->i_level >= 0);
        iter->i_nodes[iter->i_level] = NULL;
#endif

    iter->i_level--;
    return hamt_iterator_next(iter, key, val);
}

static hamt_iter_t
hamt_iterator_next(HamtIteratorState *iter, PyObject **key, PyObject **val)
{
    if (iter->i_level < 0) {
        return I_END;
    }

    assert(iter->i_level < _Py_HAMT_MAX_TREE_DEPTH);

    HamtNode *current = iter->i_nodes[iter->i_level];

    if (IS_BITMAP_NODE(current)) {
        return hamt_iterator_bitmap_next(iter, key, val);
    }
    else if (IS_ARRAY_NODE(current)) {
        return hamt_iterator_array_next(iter, key, val);
    }
    else {
        assert(IS_COLLISION_NODE(current));
        return hamt_iterator_collision_next(iter, key, val);
    }
}


/////////////////////////////////// HAMT high-level functions


HamtObject *
_Hamt_Assoc(HamtObject *o, PyObject *key, PyObject *val)
{
    int32_t key_hash;
    int added_leaf = 0;
    HamtNode *new_root;
    HamtObject *new_o;

    key_hash = hamt_hash(key);
    if (key_hash == -1) {
        return NULL;
    }

    new_root = hamt_node_assoc(
        (HamtNode *)(o->h_root),
        0, key_hash, key, val, &added_leaf);
    if (new_root == NULL) {
        return NULL;
    }

    if (new_root == o->h_root) {
        Py_DECREF(new_root);
        return (HamtObject*)Py_NewRef(o);
    }

    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)o);
    new_o = hamt_alloc(state);
    if (new_o == NULL) {
        Py_DECREF(new_root);
        return NULL;
    }

    new_o->h_root = new_root;  /* borrow */
    new_o->h_count = added_leaf ? o->h_count + 1 : o->h_count;

    return new_o;
}

HamtObject *
_Hamt_Without(HamtObject *o, PyObject *key)
{
    int32_t key_hash = hamt_hash(key);
    if (key_hash == -1) {
        return NULL;
    }

    HamtNode *new_root = NULL;

    hamt_without_t res = hamt_node_without(
        (HamtNode *)(o->h_root),
        0, key_hash, key,
        &new_root);

    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)o);

    switch (res) {
        case W_ERROR:
            return NULL;
        case W_EMPTY: {
            return _Hamt_New(state);
        }
        case W_NOT_FOUND:
            return (HamtObject*)Py_NewRef(o);
        case W_NEWNODE: {
            assert(new_root != NULL);

            HamtObject *new_o = hamt_alloc(state);
            if (new_o == NULL) {
                Py_DECREF(new_root);
                return NULL;
            }

            new_o->h_root = new_root;  /* borrow */
            new_o->h_count = o->h_count - 1;
            assert(new_o->h_count >= 0);
            return new_o;
        }
        default:
            Py_UNREACHABLE();
    }
}

static hamt_find_t
hamt_find(HamtObject *o, PyObject *key, PyObject **val)
{
    if (o->h_count == 0) {
        return F_NOT_FOUND;
    }

    int32_t key_hash = hamt_hash(key);
    if (key_hash == -1) {
        return F_ERROR;
    }

    return hamt_node_find(o->h_root, 0, key_hash, key, val);
}


int
_Hamt_Find(HamtObject *o, PyObject *key, PyObject **val)
{
    hamt_find_t res = hamt_find(o, key, val);
    switch (res) {
        case F_ERROR:
            return -1;
        case F_NOT_FOUND:
            return 0;
        case F_FOUND:
            return 1;
        default:
            Py_UNREACHABLE();
    }
}


int
_Hamt_Eq(HamtObject *v, HamtObject *w)
{
    if (v == w) {
        return 1;
    }

    if (v->h_count != w->h_count) {
        return 0;
    }

    HamtIteratorState iter;
    hamt_iter_t iter_res;
    hamt_find_t find_res;
    PyObject *v_key;
    PyObject *v_val;
    PyObject *w_val;

    hamt_iterator_init(&iter, v->h_root);

    do {
        iter_res = hamt_iterator_next(&iter, &v_key, &v_val);
        if (iter_res == I_ITEM) {
            find_res = hamt_find(w, v_key, &w_val);
            switch (find_res) {
                case F_ERROR:
                    return -1;

                case F_NOT_FOUND:
                    return 0;

                case F_FOUND: {
                    int cmp = PyObject_RichCompareBool(v_val, w_val, Py_EQ);
                    if (cmp < 0) {
                        return -1;
                    }
                    if (cmp == 0) {
                        return 0;
                    }
                }
            }
        }
    } while (iter_res != I_END);

    return 1;
}

Py_ssize_t
_Hamt_Len(HamtObject *o)
{
    return o->h_count;
}

static HamtObject *
hamt_alloc(hamt_module_state *state)
{
    HamtObject *o;
    o = PyObject_GC_New(HamtObject, state->Hamt_Type);
    if (o == NULL) {
        return NULL;
    }
    o->h_count = 0;
    o->h_root = NULL;
    o->h_weakreflist = NULL;
    PyObject_GC_Track(o);
    return o;
}

HamtObject *
_Hamt_New(hamt_module_state *state)
{
    /* HAMT is an immutable object so we can easily cache an
       empty instance. */
    return (HamtObject*)Py_NewRef(state->empty_hamt);
}

#ifdef Py_DEBUG
static PyObject *
hamt_dump(HamtObject *self)
{
    _PyUnicodeWriter writer;

    _PyUnicodeWriter_Init(&writer);

    if (_hamt_dump_format(&writer, "HAMT(len=%zd):\n", self->h_count)) {
        goto error;
    }

    if (hamt_node_dump(self->h_root, &writer, 0)) {
        goto error;
    }

    return _PyUnicodeWriter_Finish(&writer);

error:
    _PyUnicodeWriter_Dealloc(&writer);
    return NULL;
}
#endif  /* Py_DEBUG */


/////////////////////////////////// Iterators: Shared Iterator Implementation


static int
hamt_baseiter_tp_clear(HamtIterator *it)
{
    Py_CLEAR(it->hi_obj);
    return 0;
}

static void
hamt_baseiter_tp_dealloc(HamtIterator *it)
{
    PyObject_GC_UnTrack(it);
    (void)hamt_baseiter_tp_clear(it);
    PyObject_GC_Del(it);
}

static int
hamt_baseiter_tp_traverse(HamtIterator *it, visitproc visit, void *arg)
{
    Py_VISIT(it->hi_obj);
    return 0;
}

static PyObject *
hamt_baseiter_tp_iternext(HamtIterator *it)
{
    PyObject *key;
    PyObject *val;
    hamt_iter_t res = hamt_iterator_next(&it->hi_iter, &key, &val);

    switch (res) {
        case I_END:
            PyErr_SetNone(PyExc_StopIteration);
            return NULL;

        case I_ITEM: {
            return (*(it->hi_yield))(key, val);
        }

        default: {
            Py_UNREACHABLE();
        }
    }
}

static Py_ssize_t
hamt_baseiter_tp_len(HamtIterator *it)
{
    return it->hi_obj->h_count;
}

static PyObject *
hamt_baseiter_new(PyTypeObject *type, binaryfunc yield, HamtObject *o)
{
    HamtIterator *it = PyObject_GC_New(HamtIterator, type);
    if (it == NULL) {
        return NULL;
    }

    it->hi_obj = (HamtObject*)Py_NewRef(o);
    it->hi_yield = yield;

    hamt_iterator_init(&it->hi_iter, o->h_root);

    return (PyObject*)it;
}

#define ITERATOR_TYPE_SHARED_SLOTS                              \
    .tp_basicsize = sizeof(HamtIterator),                     \
    .tp_itemsize = 0,                                           \
    .tp_as_mapping = &HamtIterator_as_mapping,                \
    .tp_dealloc = (destructor)hamt_baseiter_tp_dealloc,         \
    .tp_getattro = PyObject_GenericGetAttr,                     \
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,        \
    .tp_traverse = (traverseproc)hamt_baseiter_tp_traverse,     \
    .tp_clear = (inquiry)hamt_baseiter_tp_clear,                \
    .tp_iter = PyObject_SelfIter,                               \
    .tp_iternext = (iternextfunc)hamt_baseiter_tp_iternext,


/////////////////////////////////// _HamtItems_Type


static PyType_Slot HamtItems_Type_slots[] = {
    {Py_tp_dealloc, hamt_baseiter_tp_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_traverse, hamt_baseiter_tp_traverse},
    {Py_tp_clear, hamt_baseiter_tp_clear},
    {Py_tp_iter, PyObject_SelfIter},
    {Py_tp_iternext, hamt_baseiter_tp_iternext},
    {Py_mp_length, hamt_baseiter_tp_len},
    {0, NULL},
};

static PyType_Spec HamtItems_Type_spec = {
    .name = "hamt.items",
    .basicsize = sizeof(HamtIterator),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = HamtItems_Type_slots,
};

static PyObject *
hamt_iter_yield_items(PyObject *key, PyObject *val)
{
    return PyTuple_Pack(2, key, val);
}

PyObject *
_Hamt_NewIterItems(HamtObject *o)
{
    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)o);
    return hamt_baseiter_new(
        state->HamtItems_Type, hamt_iter_yield_items, o);
}


/////////////////////////////////// _HamtKeys_Type


static PyType_Slot HamtKeys_Type_slots[] = {
    {Py_tp_dealloc, hamt_baseiter_tp_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_traverse, hamt_baseiter_tp_traverse},
    {Py_tp_clear, hamt_baseiter_tp_clear},
    {Py_tp_iter, PyObject_SelfIter},
    {Py_tp_iternext, hamt_baseiter_tp_iternext},
    {Py_mp_length, hamt_baseiter_tp_len},
    {0, NULL},
};

static PyType_Spec HamtKeys_Type_spec = {
    .name = "hamt.keys",
    .basicsize = sizeof(HamtIterator),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = HamtKeys_Type_slots,
};

static PyObject *
hamt_iter_yield_keys(PyObject *key, PyObject *val)
{
    return Py_NewRef(key);
}

PyObject *
_Hamt_NewIterKeys(HamtObject *o)
{
    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)o);
    return hamt_baseiter_new(
        state->HamtKeys_Type, hamt_iter_yield_keys, o);
}


/////////////////////////////////// _HamtValues_Type


static PyType_Slot HamtValues_Type_slots[] = {
    {Py_tp_dealloc, hamt_baseiter_tp_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_traverse, hamt_baseiter_tp_traverse},
    {Py_tp_clear, hamt_baseiter_tp_clear},
    {Py_tp_iter, PyObject_SelfIter},
    {Py_tp_iternext, hamt_baseiter_tp_iternext},
    {Py_mp_length, hamt_baseiter_tp_len},
    {0, NULL},
};

static PyType_Spec HamtValues_Type_spec = {
    .name = "hamt.values",
    .basicsize = sizeof(HamtIterator),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = HamtValues_Type_slots,
};

static PyObject *
hamt_iter_yield_values(PyObject *key, PyObject *val)
{
    return Py_NewRef(val);
}

PyObject *
_Hamt_NewIterValues(HamtObject *o)
{
    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)o);
    return hamt_baseiter_new(
        state->HamtValues_Type, hamt_iter_yield_values, o);
}


/////////////////////////////////// _Hamt_Type


#ifdef Py_DEBUG
static PyObject *
hamt_dump(HamtObject *self);
#endif


static PyObject *
hamt_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    hamt_module_state *state = get_hamt_state_from_type(type);
    return (PyObject*)_Hamt_New(state);
}

static int
hamt_tp_clear(HamtObject *self)
{
    Py_CLEAR(self->h_root);
    return 0;
}


static int
hamt_tp_traverse(HamtObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->h_root);
    return 0;
}

static void
hamt_tp_dealloc(HamtObject *self)
{
    hamt_module_state *state = get_hamt_state_from_obj((PyObject*)self);
    if (self == state->empty_hamt) {
        /* The empty one is managed by the module state. */
#ifdef Py_DEBUG
        _Py_FatalRefcountError("deallocating the empty hamt singleton");
#else
        return;
#endif
    }

    PyObject_GC_UnTrack(self);
    if (self->h_weakreflist != NULL) {
        PyObject_ClearWeakRefs((PyObject*)self);
    }
    (void)hamt_tp_clear(self);
    Py_TYPE(self)->tp_free(self);
}


static PyObject *
hamt_tp_richcompare(PyObject *v, PyObject *w, int op)
{
    if (!Hamt_Check(v) || !Hamt_Check(w) || (op != Py_EQ && op != Py_NE)) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    int res = _Hamt_Eq((HamtObject *)v, (HamtObject *)w);
    if (res < 0) {
        return NULL;
    }

    if (op == Py_NE) {
        res = !res;
    }

    if (res) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}

static int
hamt_tp_contains(HamtObject *self, PyObject *key)
{
    PyObject *val;
    return _Hamt_Find(self, key, &val);
}

static PyObject *
hamt_tp_subscript(HamtObject *self, PyObject *key)
{
    PyObject *val;
    hamt_find_t res = hamt_find(self, key, &val);
    switch (res) {
        case F_ERROR:
            return NULL;
        case F_FOUND:
            return Py_NewRef(val);
        case F_NOT_FOUND:
            PyErr_SetObject(PyExc_KeyError, key);
            return NULL;
        default:
            Py_UNREACHABLE();
    }
}

static Py_ssize_t
hamt_tp_len(HamtObject *self)
{
    return _Hamt_Len(self);
}

static PyObject *
hamt_tp_iter(HamtObject *self)
{
    return _Hamt_NewIterKeys(self);
}

static PyObject *
hamt_py_set(HamtObject *self, PyObject *args)
{
    PyObject *key;
    PyObject *val;

    if (!PyArg_UnpackTuple(args, "set", 2, 2, &key, &val)) {
        return NULL;
    }

    return (PyObject *)_Hamt_Assoc(self, key, val);
}

static PyObject *
hamt_py_get(HamtObject *self, PyObject *args)
{
    PyObject *key;
    PyObject *def = NULL;

    if (!PyArg_UnpackTuple(args, "get", 1, 2, &key, &def)) {
        return NULL;
    }

    PyObject *val = NULL;
    hamt_find_t res = hamt_find(self, key, &val);
    switch (res) {
        case F_ERROR:
            return NULL;
        case F_FOUND:
            return Py_NewRef(val);
        case F_NOT_FOUND:
            if (def == NULL) {
                Py_RETURN_NONE;
            }
            return Py_NewRef(def);
        default:
            Py_UNREACHABLE();
    }
}

static PyObject *
hamt_py_delete(HamtObject *self, PyObject *key)
{
    return (PyObject *)_Hamt_Without(self, key);
}

static PyObject *
hamt_py_items(HamtObject *self, PyObject *args)
{
    return _Hamt_NewIterItems(self);
}

static PyObject *
hamt_py_values(HamtObject *self, PyObject *args)
{
    return _Hamt_NewIterValues(self);
}

static PyObject *
hamt_py_keys(HamtObject *self, PyObject *Py_UNUSED(args))
{
    return _Hamt_NewIterKeys(self);
}

#ifdef Py_DEBUG
static PyObject *
hamt_py_dump(HamtObject *self, PyObject *Py_UNUSED(args))
{
    return hamt_dump(self);
}
#endif


static PyMethodDef Hamt_methods[] = {
    {"set", _PyCFunction_CAST(hamt_py_set), METH_VARARGS, NULL},
    {"get", _PyCFunction_CAST(hamt_py_get), METH_VARARGS, NULL},
    {"delete", _PyCFunction_CAST(hamt_py_delete), METH_O, NULL},
    {"items", _PyCFunction_CAST(hamt_py_items), METH_NOARGS, NULL},
    {"keys", _PyCFunction_CAST(hamt_py_keys), METH_NOARGS, NULL},
    {"values", _PyCFunction_CAST(hamt_py_values), METH_NOARGS, NULL},
#ifdef Py_DEBUG
    {"__dump__", _PyCFunction_CAST(hamt_py_dump), METH_NOARGS, NULL},
#endif
    {NULL, NULL}
};

static PyType_Slot Hamt_Type_slots[] = {
    {Py_tp_dealloc, hamt_tp_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_traverse, hamt_tp_traverse},
    {Py_tp_clear, hamt_tp_clear},
    {Py_tp_new, hamt_tp_new},
    {Py_tp_iter, hamt_tp_iter},
    {Py_tp_richcompare, hamt_tp_richcompare},
    {Py_tp_hash, PyObject_HashNotImplemented},
    {Py_tp_methods, Hamt_methods},
    {Py_mp_length, hamt_tp_len},
    {Py_mp_subscript, hamt_tp_subscript},
    {Py_sq_contains, hamt_tp_contains},
    {0, NULL},
};

static PyType_Spec Hamt_Type_spec = {
    .name = "hamt.hamt",
    .basicsize = sizeof(HamtObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = Hamt_Type_slots,
};


/////////////////////////////////// Tree Node Types


static PyType_Slot Hamt_ArrayNode_Type_slots[] = {
    {Py_tp_dealloc, hamt_node_array_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_traverse, hamt_node_array_traverse},
    {Py_tp_free, PyObject_GC_Del},
    {Py_tp_hash, PyObject_HashNotImplemented},
    {0, NULL},
};

static PyType_Spec Hamt_ArrayNode_Type_spec = {
    .name = "hamt.hamt_array_node",
    .basicsize = sizeof(HamtNode_Array),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = Hamt_ArrayNode_Type_slots,
};

static PyType_Slot Hamt_BitmapNode_Type_slots[] = {
    {Py_tp_dealloc, hamt_node_bitmap_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_traverse, hamt_node_bitmap_traverse},
    {Py_tp_free, PyObject_GC_Del},
    {Py_tp_hash, PyObject_HashNotImplemented},
    {0, NULL},
};

static PyType_Spec Hamt_BitmapNode_Type_spec = {
    .name = "hamt.hamt_bitmap_node",
    .basicsize = sizeof(HamtNode_Bitmap) - sizeof(PyObject *),
    .itemsize = sizeof(PyObject *),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = Hamt_BitmapNode_Type_slots,
};

static PyType_Slot Hamt_CollisionNode_Type_slots[] = {
    {Py_tp_dealloc, hamt_node_collision_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_traverse, hamt_node_collision_traverse},
    {Py_tp_free, PyObject_GC_Del},
    {Py_tp_hash, PyObject_HashNotImplemented},
    {0, NULL},
};

static PyType_Spec Hamt_CollisionNode_Type_spec = {
    .name = "hamt.hamt_collision_node",
    .basicsize = sizeof(HamtNode_Collision) - sizeof(PyObject *),
    .itemsize = sizeof(PyObject *),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = Hamt_CollisionNode_Type_slots,
};

////

static PyObject *
py_hamt_new(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }

    hamt_module_state *state = get_hamt_module_state(self);
    HamtObject *hamt = _Hamt_New(state);
    if (!hamt) {
        return NULL;
    }

    return (PyObject *)hamt;
}

static PyObject *
py_hamt_assoc(PyObject *self, PyObject *args)
{
    PyObject *hamt_obj;
    PyObject *key;
    PyObject *val;

    if (!PyArg_ParseTuple(args, "OOO", &hamt_obj, &key, &val)) {
        return NULL;
    }

    if (!Hamt_Check(hamt_obj)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a HAMT object");
        return NULL;
    }

    HamtObject *result = _Hamt_Assoc((HamtObject *)hamt_obj, key, val);
    if (!result) {
        return NULL;
    }

    return (PyObject *)result;
}

static PyObject *
py_hamt_without(PyObject *self, PyObject *args)
{
    PyObject *hamt_obj;
    PyObject *key;

    if (!PyArg_ParseTuple(args, "OO", &hamt_obj, &key)) {
        return NULL;
    }

    if (!Hamt_Check(hamt_obj)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a HAMT object");
        return NULL;
    }

    HamtObject *result = _Hamt_Without((HamtObject *)hamt_obj, key);
    if (!result) {
        return NULL;
    }

    return (PyObject *)result;
}

static PyObject *
py_hamt_find(PyObject *self, PyObject *args)
{
    PyObject *hamt_obj;
    PyObject *key;

    if (!PyArg_ParseTuple(args, "OO", &hamt_obj, &key)) {
        return NULL;
    }

    if (!Hamt_Check(hamt_obj)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a HAMT object");
        return NULL;
    }

    PyObject *val = NULL;
    int result = _Hamt_Find((HamtObject *)hamt_obj, key, &val);

    if (result == -1) {
        return NULL;
    }

    if (result == 0) {
        Py_RETURN_NONE;
    }

    // result == 1, key found, val is a borrowed reference
    Py_INCREF(val);
    return val;
}

static PyObject *
py_hamt_eq(PyObject *self, PyObject *args)
{
    PyObject *v_obj;
    PyObject *w_obj;

    if (!PyArg_ParseTuple(args, "OO", &v_obj, &w_obj)) {
        return NULL;
    }

    if (!Hamt_Check(v_obj)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a HAMT object");
        return NULL;
    }

    if (!Hamt_Check(w_obj)) {
        PyErr_SetString(PyExc_TypeError, "second argument must be a HAMT object");
        return NULL;
    }

    int result = _Hamt_Eq((HamtObject *)v_obj, (HamtObject *)w_obj);

    if (result == -1) {
        return NULL;
    }

    if (result == 0) {
        Py_RETURN_FALSE;
    }

    Py_RETURN_TRUE;
}

static PyObject *
py_hamt_len(PyObject *self, PyObject *args)
{
    PyObject *hamt_obj;

    if (!PyArg_ParseTuple(args, "O", &hamt_obj)) {
        return NULL;
    }

    if (!Hamt_Check(hamt_obj)) {
        PyErr_SetString(PyExc_TypeError, "argument must be a HAMT object");
        return NULL;
    }

    Py_ssize_t len = _Hamt_Len((HamtObject *)hamt_obj);
    return PyLong_FromSsize_t(len);
}

static PyObject *
py_hamt_iter_keys(PyObject *self, PyObject *args)
{
    PyObject *hamt_obj;

    if (!PyArg_ParseTuple(args, "O", &hamt_obj)) {
        return NULL;
    }

    if (!Hamt_Check(hamt_obj)) {
        PyErr_SetString(PyExc_TypeError, "argument must be a HAMT object");
        return NULL;
    }

    PyObject *iter = _Hamt_NewIterKeys((HamtObject *)hamt_obj);
    if (!iter) {
        return NULL;
    }

    return iter;
}

static PyObject *
py_hamt_iter_values(PyObject *self, PyObject *args)
{
    PyObject *hamt_obj;

    if (!PyArg_ParseTuple(args, "O", &hamt_obj)) {
        return NULL;
    }

    if (!Hamt_Check(hamt_obj)) {
        PyErr_SetString(PyExc_TypeError, "argument must be a HAMT object");
        return NULL;
    }

    PyObject *iter = _Hamt_NewIterValues((HamtObject *)hamt_obj);
    if (!iter) {
        return NULL;
    }

    return iter;
}

static PyObject *
py_hamt_iter_items(PyObject *self, PyObject *args)
{
    PyObject *hamt_obj;

    if (!PyArg_ParseTuple(args, "O", &hamt_obj)) {
        return NULL;
    }

    if (!Hamt_Check(hamt_obj)) {
        PyErr_SetString(PyExc_TypeError, "argument must be a HAMT object");
        return NULL;
    }

    PyObject *iter = _Hamt_NewIterItems((HamtObject *)hamt_obj);
    if (!iter) {
        return NULL;
    }

    return iter;
}

//

static int _hamt_module_exec(PyObject *module)
{
    hamt_module_state *state = get_hamt_module_state(module);

    /* Initialize type objects */
    state->Hamt_Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &Hamt_Type_spec, NULL);
    if (state->Hamt_Type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->Hamt_Type) < 0) {
        return -1;
    }

    state->HamtItems_Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &HamtItems_Type_spec, NULL);
    if (state->HamtItems_Type == NULL) {
        return -1;
    }

    state->HamtKeys_Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &HamtKeys_Type_spec, NULL);
    if (state->HamtKeys_Type == NULL) {
        return -1;
    }

    state->HamtValues_Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &HamtValues_Type_spec, NULL);
    if (state->HamtValues_Type == NULL) {
        return -1;
    }

    state->Hamt_ArrayNode_Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &Hamt_ArrayNode_Type_spec, NULL);
    if (state->Hamt_ArrayNode_Type == NULL) {
        return -1;
    }

    state->Hamt_BitmapNode_Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &Hamt_BitmapNode_Type_spec, NULL);
    if (state->Hamt_BitmapNode_Type == NULL) {
        return -1;
    }

    state->Hamt_CollisionNode_Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &Hamt_CollisionNode_Type_spec, NULL);
    if (state->Hamt_CollisionNode_Type == NULL) {
        return -1;
    }

    /* Initialize singleton objects */

    /* Create empty bitmap node */
    state->empty_bitmap_node = PyObject_GC_New(HamtNode_Bitmap, state->Hamt_BitmapNode_Type);
    if (state->empty_bitmap_node == NULL) {
        return -1;
    }
    Py_SET_SIZE(state->empty_bitmap_node, 0);
    state->empty_bitmap_node->b_bitmap = 0;
    PyObject_GC_Track(state->empty_bitmap_node);

    /* Create empty HAMT object */
    state->empty_hamt = PyObject_GC_New(HamtObject, state->Hamt_Type);
    if (state->empty_hamt == NULL) {
        return -1;
    }
    state->empty_hamt->h_root = (HamtNode *)Py_NewRef(state->empty_bitmap_node);
    state->empty_hamt->h_weakreflist = NULL;
    state->empty_hamt->h_count = 0;
    PyObject_GC_Track(state->empty_hamt);

    return 0;
}

static int _hamt_module_traverse(PyObject *module, visitproc visit, void *arg)
{
    hamt_module_state *state = get_hamt_module_state(module);

    /* Visit type objects */
    Py_VISIT(state->Hamt_Type);
    Py_VISIT(state->HamtItems_Type);
    Py_VISIT(state->HamtKeys_Type);
    Py_VISIT(state->HamtValues_Type);
    Py_VISIT(state->Hamt_ArrayNode_Type);
    Py_VISIT(state->Hamt_BitmapNode_Type);
    Py_VISIT(state->Hamt_CollisionNode_Type);

    /* Visit singleton objects */
    Py_VISIT(state->empty_hamt);
    Py_VISIT(state->empty_bitmap_node);

    return 0;
}

static int _hamt_module_clear(PyObject *module)
{
    hamt_module_state *state = get_hamt_module_state(module);

    /* Clear type objects */
    Py_CLEAR(state->Hamt_Type);
    Py_CLEAR(state->HamtItems_Type);
    Py_CLEAR(state->HamtKeys_Type);
    Py_CLEAR(state->HamtValues_Type);
    Py_CLEAR(state->Hamt_ArrayNode_Type);
    Py_CLEAR(state->Hamt_BitmapNode_Type);
    Py_CLEAR(state->Hamt_CollisionNode_Type);

    /* Clear singleton objects */
    Py_CLEAR(state->empty_hamt);
    Py_CLEAR(state->empty_bitmap_node);

    return 0;
}

static void _hamt_module_free(void *module)
{
    _hamt_module_clear((PyObject *)module);
}

//

PyDoc_STRVAR(hamt_doc, _MODULE_NAME);

static PyMethodDef hamt_methods[] = {
    {"new", py_hamt_new, METH_VARARGS, "Create a new HAMT immutable mapping"},
    {"assoc", py_hamt_assoc, METH_VARARGS, "Return a new HAMT with an additional key/value pair"},
    {"without", py_hamt_without, METH_VARARGS, "Return a new HAMT without the specified key"},
    {"find", py_hamt_find, METH_VARARGS, "Find a key in the HAMT, return value or None"},
    {"eq", py_hamt_eq, METH_VARARGS, "Check if two HAMTs are equal"},
    {"len", py_hamt_len, METH_VARARGS, "Return the number of items in the HAMT"},
    {"iter_keys", py_hamt_iter_keys, METH_VARARGS, "Return a keys iterator over the HAMT"},
    {"iter_values", py_hamt_iter_values, METH_VARARGS, "Return a values iterator over the HAMT"},
    {"iter_items", py_hamt_iter_items, METH_VARARGS, "Return an items iterator over the HAMT"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot hamt_slots[] = {
    {Py_mod_exec, (void *) _hamt_module_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef hamt_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = hamt_doc,
    .m_size = sizeof(hamt_module_state),
    .m_methods = hamt_methods,
    .m_slots = hamt_slots,
    .m_traverse = _hamt_module_traverse,
    .m_clear = _hamt_module_clear,
    .m_free = _hamt_module_free,
};

PyMODINIT_FUNC PyInit__hamt(void)
{
    return PyModuleDef_Init(&hamt_module);
}
