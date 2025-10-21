import setuptools as st
import setuptools_rust as st_rs


st.setup(
    rust_extensions=[
        st_rs.RustExtension(
            '_boilerplate',
            path='omdev/rs/_boilerplate/Cargo.toml',
        ),
    ],
)
