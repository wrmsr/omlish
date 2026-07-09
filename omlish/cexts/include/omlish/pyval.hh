/*
FIXME:
 - unify interface with pyref
*/
#pragma once

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <utility>

#include <Python.h>

//

static_assert(sizeof(void*) == 8);
static_assert(sizeof(std::uintptr_t) == 8);
static_assert(sizeof(std::int64_t) == 8);
static_assert(alignof(PyObject) >= 2);

namespace pyval_detail {
    inline constexpr std::uintptr_t kTagBit = std::uintptr_t{1};

    constexpr std::uintptr_t encode(std::int64_t v) noexcept {
        return static_cast<std::uintptr_t>(v << 1) | kTagBit;
    }

    constexpr std::int64_t decode(std::uintptr_t w) noexcept {
        return static_cast<std::int64_t>(w) >> 1;
    }
}

class PyVal {
    static constexpr std::uintptr_t kTag = pyval_detail::kTagBit;

    static constexpr std::int64_t kMin = -(INT64_C(1) << 62);
    static constexpr std::int64_t kMax =  (INT64_C(1) << 62) - 1;

public:
    static constexpr std::int64_t kImmMin = kMin;
    static constexpr std::int64_t kImmMax = kMax;

private:
    static bool      is_ptr_(std::uintptr_t w) noexcept { return (w & kTag) == 0; }
    static PyObject* as_ptr_(std::uintptr_t w) noexcept { return reinterpret_cast<PyObject*>(w); }
    bool             holds_pointer_() const noexcept { return is_ptr_(w_); }
    PyObject*        ptr_()           const noexcept { return as_ptr_(w_); }

    // Install a new word, THEN drop the old contents. This is Py_XSETREF order: the slot is already consistent before a
    // freed object's __del__/tp_dealloc can re-enter and observe it.
    void set_word_(std::uintptr_t nw) noexcept {
        std::uintptr_t ow = w_;
        w_ = nw;
        if (is_ptr_(ow)) {
            Py_XDECREF(as_ptr_(ow));
        }
    }

    // Take ownership of one reference to `o` (NULL ok) and drop the old contents.
    void adopt_(PyObject* o) noexcept {
        assert((reinterpret_cast<std::uintptr_t>(o) & kTag) == 0 && "PyObject* is not 2-byte aligned; tag scheme is broken");
        set_word_(reinterpret_cast<std::uintptr_t>(o));
    }

    // compile-time guards

    static_assert(sizeof(void*) == 8, "PyVal assumes 64-bit pointers (the immediate path needs 63 bits).");

    // The round-trip asserts below are the real guard on the integer codec: they fail to compile on any target where
    // encode/decode don't invert.
    static_assert(pyval_detail::decode(pyval_detail::encode(0))       == 0,       "roundtrip");
    static_assert(pyval_detail::decode(pyval_detail::encode(-1))      == -1,      "roundtrip");
    static_assert(pyval_detail::decode(pyval_detail::encode(kImmMin)) == kImmMin, "roundtrip");
    static_assert(pyval_detail::decode(pyval_detail::encode(kImmMax)) == kImmMax, "roundtrip");

    std::uintptr_t w_ = 0;  // 0 == empty (NULL PyObject*)

public:
    // lifetime (RAII; see NOTES for the embedded-in-PyObject case

    PyVal() noexcept = default;  // empty (all-zero word)

    ~PyVal() noexcept {
        clear();
    }

    PyVal(const PyVal& o) noexcept : w_(o.w_) {
        if (holds_pointer_()) {
            Py_XINCREF(ptr_());
        }
    }

    PyVal(PyVal&& o) noexcept : w_(std::exchange(o.w_, 0)) {}

    PyVal& operator=(const PyVal& o) noexcept {
        if (this == &o) {
            return *this;
        }
        std::uintptr_t nw = o.w_;
        if (is_ptr_(nw)) {
            Py_XINCREF(as_ptr_(nw));  // incref new ...
        }
        std::uintptr_t ow = w_;
        w_ = nw;  // ... install (Py_XSETREF order) ...
        if (is_ptr_(ow)) {
            Py_XDECREF(as_ptr_(ow));  // ... then drop old
        }
        return *this;
    }

    PyVal& operator=(PyVal&& o) noexcept {
        if (this == &o) {
            return *this;
        }
        auto ow = w_;
        w_ = std::exchange(o.w_, 0);
        if (is_ptr_(ow)) {
            Py_XDECREF(as_ptr_(ow));
        }
        return *this;
    }

    void swap(PyVal& o) noexcept {
        std::swap(w_, o.w_);
    }

    friend void swap(PyVal& a, PyVal& b) noexcept {
        a.swap(b);
    }

    // queries

    bool is_empty()  const noexcept { return w_ == 0; }
    bool is_object() const noexcept { return holds_pointer_() && w_ != 0; }

    // True only for an inline integer. NOTE: a large int stored as a heap PyLong reports is_object(), not
    // is_inline_int(). Likewise Py_None/Py_True/Py_False are just objects here - an empty val (NULL) is NOT a ref to
    // None.
    bool is_inline_int() const noexcept { return (w_ & kTag) != 0; }

    // accessors

    // Borrowed pointer, or NULL if this isn't a real object (no refcount change).
    PyObject* object() const noexcept { return is_object() ? ptr_() : nullptr; }

    // Precondition: is_inline_int(). The decoded C value.
    std::int64_t inline_int() const noexcept {
        assert(is_inline_int());
        return pyval_detail::decode(w_);
    }

    // Materialize a NEW strong reference equivalent to the contents:
    //   object     -> incref & return
    //   inline int -> a fresh PyLong (may be NULL + MemoryError on failure)
    // Calling this on an empty val is a logic error: returns NULL + SystemError
    [[nodiscard]] PyObject* to_object() const {
        if (is_empty()) {
            PyErr_SetString(PyExc_SystemError, "PyVal::to_object() on empty val");
            return nullptr;
        }
        if (auto* p = object()) {
            return Py_NewRef(p);
        }
        return PyLong_FromLongLong(static_cast<long long>(pyval_detail::decode(w_)));
    }

    // setters (each drops the previous contents, Py_XSETREF ordering)

    void clear() noexcept { set_word_(0); }  // also the tp_clear helper

    // Store a C integer. In-range values go inline; anything outside [kImmMin, kImmMax] gracefully falls back to a
    // heap PyLong. Returns false ONLY if that allocation fails (MemoryError is set); the inline path cannot fail.
    [[nodiscard]] bool set_int(std::int64_t v) {
        if (v >= kImmMin && v <= kImmMax) {
            set_word_(pyval_detail::encode(v));
            return true;
        }
        PyObject* o = PyLong_FromLongLong(static_cast<long long>(v));
        if (!o) {
            return false;
        }
        adopt_(o);  // steals the new ref
        return true;
    }

    // Store a strong reference to an arbitrary object (INCREFs `o`; NULL ok, in which case this is equivalent to
    // clear()). Note that a stored Py_None is a real reference, distinct from empty/NULL.
    void set_object(PyObject* o) noexcept {
        adopt_(Py_XNewRef(o));
    }

    // Same, but steals the caller's reference (no INCREF). Use for fresh refs.
    void set_object_steal(PyObject* o) noexcept { adopt_(o); }

    // Convenience setter. If absorb_ints is set, collapses exact, in-range PyLongs into immediates - this does NOT
    // preserve object identity (`x is y` will differ later), hence opt-in. Everything else (including None and bools)
    // is stored as a plain strong reference.
    void assign(PyObject* o, bool absorb_ints = false) noexcept {
        if (absorb_ints && o && PyLong_CheckExact(o)) {
            int ovf = 0;
            long long v = PyLong_AsLongLongAndOverflow(o, &ovf);
            if (!ovf && v >= kImmMin && v <= kImmMax) {
                set_word_(pyval_detail::encode(static_cast<std::int64_t>(v)));
                return;
            }
        }
        set_object(o);
    }

    // cyclic-GC protocol helpers

    // Use inside tp_traverse. Only real objects are visited; immediates are not tracked and need no visiting. (clear()
    // above is the tp_clear helper.)
    int traverse(visitproc visit, void* arg) const {
        if (is_object()) {
            int r = visit(ptr_(), arg);
            if (r) {
                return r;
            }
        }
        return 0;
    }

    // manual relocation (the type is NOT trivially copyable)

    // Move the owned bits out, leaving this empty. Use when you relocate a val yourself (e.g. growing your own array):
    // copy the word to the new slot and treat the old slot as released - do NOT also run a destructor on it.
    [[nodiscard]] std::uintptr_t release() noexcept {
        std::uintptr_t w = w_;
        w_ = 0;
        return w;
    }

    std::uintptr_t raw() const noexcept { return w_; }

    static PyVal from_raw(std::uintptr_t w) noexcept {
        PyVal b;
        b.w_ = w;
        return b;
    }
};

static_assert(sizeof(PyVal) == sizeof(void*), "PyVal must be exactly pointer-sized.");
