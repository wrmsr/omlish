import setuptools as st


st.setup(
    ext_modules=[
        st.Extension(
            name='omdev.cexts._cext._boilerplate',
            sources=['omdev/cexts/_cext.boilerplate.cc'],
            extra_compile_args=['-std=c++20'],
        ),
    ]
)
