import setuptools as st


st.setup(
    ext_modules=[
        st.Extension(
            name='omlish._check',
            sources=['omlish/_check.cc'],
            extra_compile_args=['-std=c++20'],
        ),
        st.Extension(
            name='omlish.collections.hamt._hamt',
            sources=['omlish/collections/hamt/_hamt.c'],
            extra_compile_args=['-std=c11'],
        ),
        st.Extension(
            name='omlish.lang._asyncs',
            sources=['omlish/lang/_asyncs.cc'],
            extra_compile_args=['-std=c++20'],
        ),
        st.Extension(
            name='omlish.lang.imports._capture',
            sources=['omlish/lang/imports/_capture.cc'],
            extra_compile_args=['-std=c++20'],
        ),
        st.Extension(
            name='omlish.typedvalues._collection',
            sources=['omlish/typedvalues/_collection.cc'],
            extra_compile_args=['-std=c++20'],
        ),
    ],
)
