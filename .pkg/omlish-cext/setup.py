import setuptools as st


st.setup(
    ext_modules=[
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
    ],
)
