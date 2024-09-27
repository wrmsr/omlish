import setuptools as st


st.setup(
    ext_modules=[
        st.Extension(
            name='omdev.cexts._boilerplate',
            sources=['omdev/cexts/_boilerplate.cc'],
            extra_compile_args=['-std=c++20'],
        ),
    ]
)
