// PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
// --------------------------------------------
//
// 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
//    ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
//    documentation.
//
// 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
//    royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
//    works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's
//    License Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2024 Python Software Foundation; All
//    Rights Reserved" are retained in Python alone or in any derivative version prepared by Licensee.
//
// 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
//    wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include
//    in any such work a brief summary of the changes made to Python.
//
// 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
//    EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR
//    WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY
//    THIRD PARTY RIGHTS.
//
// 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
//    DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN
//    IF ADVISED OF THE POSSIBILITY THEREOF.
//
// 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
//
// 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
//    venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
//    name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
//
// 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
//    License Agreement.

// https://github.com/python/cpython/blob/5b8a6c5186be299d96dd483146dc6ea737ffdfe7/Include/internal/pycore_hamt.h

#pragma once

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


extern PyTypeObject _PyHamt_Type;
extern PyTypeObject _PyHamt_ArrayNode_Type;
extern PyTypeObject _PyHamt_BitmapNode_Type;
extern PyTypeObject _PyHamt_CollisionNode_Type;
extern PyTypeObject _PyHamtKeys_Type;
extern PyTypeObject _PyHamtValues_Type;
extern PyTypeObject _PyHamtItems_Type;


/* other API */

#define PyHamt_Check(o) Py_IS_TYPE((o), &_PyHamt_Type)


/* Abstract tree node. */
typedef struct {
    PyObject_HEAD
} PyHamtNode;


/* An HAMT immutable mapping collection. */
typedef struct {
    PyObject_HEAD
    PyHamtNode *h_root;
    PyObject *h_weakreflist;
    Py_ssize_t h_count;
} PyHamtObject;


typedef struct {
    PyObject_VAR_HEAD
    uint32_t b_bitmap;
    PyObject *b_array[1];
} PyHamtNode_Bitmap;


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
    PyHamtNode *i_nodes[_Py_HAMT_MAX_TREE_DEPTH];
    Py_ssize_t i_pos[_Py_HAMT_MAX_TREE_DEPTH];
    int8_t i_level;
} PyHamtIteratorState;


/* Base iterator object.

   Contains the iteration state, a pointer to the HAMT tree,
   and a pointer to the 'yield function'.  The latter is a simple
   function that returns a key/value tuple for the 'Items' iterator,
   just a key for the 'Keys' iterator, and a value for the 'Values'
   iterator.
*/
typedef struct {
    PyObject_HEAD
    PyHamtObject *hi_obj;
    PyHamtIteratorState hi_iter;
    binaryfunc hi_yield;
} PyHamtIterator;


/* Create a new HAMT immutable mapping. */
PyHamtObject * _PyHamt_New(void);

/* Return a new collection based on "o", but with an additional
   key/val pair. */
PyHamtObject * _PyHamt_Assoc(PyHamtObject *o, PyObject *key, PyObject *val);

/* Return a new collection based on "o", but without "key". */
PyHamtObject * _PyHamt_Without(PyHamtObject *o, PyObject *key);

/* Find "key" in the "o" collection.

   Return:
   - -1: An error occurred.
   - 0: "key" wasn't found in "o".
   - 1: "key" is in "o"; "*val" is set to its value (a borrowed ref).
*/
int _PyHamt_Find(PyHamtObject *o, PyObject *key, PyObject **val);

/* Check if "v" is equal to "w".

   Return:
   - 0: v != w
   - 1: v == w
   - -1: An error occurred.
*/
int _PyHamt_Eq(PyHamtObject *v, PyHamtObject *w);

/* Return the size of "o"; equivalent of "len(o)". */
Py_ssize_t _PyHamt_Len(PyHamtObject *o);

/* Return a Keys iterator over "o". */
PyObject * _PyHamt_NewIterKeys(PyHamtObject *o);

/* Return a Values iterator over "o". */
PyObject * _PyHamt_NewIterValues(PyHamtObject *o);

/* Return a Items iterator over "o". */
PyObject * _PyHamt_NewIterItems(PyHamtObject *o);

