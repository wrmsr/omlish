#pragma once

//

template<typename F>
struct ScopeGuard {
    F cleanup;
    ~ScopeGuard() { cleanup(); }
};

template<typename F> ScopeGuard(F) -> ScopeGuard<F>;
