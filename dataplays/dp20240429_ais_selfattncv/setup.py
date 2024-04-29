import codecs
import os
import pathlib
import platform
import re

from setuptools import setup, find_packages


def clean_html(raw_html):
    """
    Args:
        raw_html:
    Returns:
    """
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html).strip()
    return cleantext


# Single sourcing code from here:
# https://packaging.python.org/guides/single-sourcing-package-version/
def find_version(*file_paths):
    """
    Args:
        *file_paths:
    Returns:
    """
    here = os.path.abspath(os.path.dirname(__file__))

    def read(*parts):
        """
        Args:
            *parts:
        Returns:
        """
        with codecs.open(os.path.join(here, *parts), "r") as fp:
            return fp.read()

    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def fetch_long_description():
    """
    Returns:
    """
    with open("README.md", encoding="utf8") as f:
        readme = f.read()
        # https://stackoverflow.com/a/12982689
        readme = clean_html(readme)
    return readme


def fetch_requirements():
    """
    Returns:
    """
    requirements_file = "requirements.txt"

    if platform.system() == "Windows":
        DEPENDENCY_LINKS.append("https://download.pytorch.org/whl/torch_stable.html")

    with open(requirements_file) as f:
        reqs = f.read()

    reqs = reqs.strip().split("\n")
    return reqs


HERE = pathlib.Path(__file__).parent

DISTNAME = "self_attention_cv"
DESCRIPTION = "Self-attention building blocks for computer vision applications in PyTorch"

LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
URL = "https://github.com/The-AI-Summer/self_attention_cv"
AUTHOR = "Adaloglou Nikolas"
AUTHOR_EMAIL = "nikolas@theaiusummer.com"
LICENSE = "MIT"
DEPENDENCY_LINKS = []
REQUIREMENTS = (fetch_requirements())
EXCLUDES = ("examples")
EXT_MODULES = []

if __name__ == "__main__":
    setup(
        name=DISTNAME,
        install_requires=REQUIREMENTS,
        url=URL,
        license=LICENSE,
        include_package_data=True,
        version=find_version("self_attention_cv", "version.py"),
        packages=find_packages(exclude=EXCLUDES),
        python_requires=">=3.6",
        ext_modules=EXT_MODULES,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        dependency_links=DEPENDENCY_LINKS,
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
        ]
    )
