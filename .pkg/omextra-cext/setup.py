import setuptools as st


st.setup(
    ext_modules=[
        st.Extension(
            name='omextra.collections.hamt._hamt',
            sources=['omextra/collections/hamt/_hamt.c'],
            extra_compile_args=['-std=c11'],
        ),
    ],
)
