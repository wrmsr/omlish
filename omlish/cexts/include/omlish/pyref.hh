#pragma once

//

template<typename T = PyObject>
class PyRef {
    T* ptr_;
public:
    explicit PyRef(T* ptr = nullptr) : ptr_(ptr) {}
    ~PyRef() {
        Py_XDECREF(reinterpret_cast<PyObject*>(ptr_));
    }

    // No copy
    PyRef(const PyRef&) = delete;
    PyRef& operator=(const PyRef&) = delete;

    // Move is OK
    PyRef(PyRef&& other) noexcept : ptr_(other.release()) {}
    PyRef& operator=(PyRef&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    void reset(T* ptr = nullptr) {
        PyObject* old = reinterpret_cast<PyObject*>(ptr_);
        ptr_ = ptr;
        Py_XDECREF(old);
    }

    T* get() const { return ptr_; }

    // Explicitly give up ownership
    [[nodiscard]] T* release() {
        T* p = ptr_;
        ptr_ = nullptr;
        return p;
    }

    explicit operator bool() const {
        return ptr_ != nullptr;
    }

    operator T*() const = delete;
};
