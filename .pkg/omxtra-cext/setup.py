import setuptools as st


st.setup(
    ext_modules=[
        st.Extension(
            name='omxtra.collections.stl._stl',
            sources=['omxtra/collections/stl/_stl.cc'],
            extra_compile_args=['-std=c++20'],
        ),
    ],
)
