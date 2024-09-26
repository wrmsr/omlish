It's like my previous python monorepo-ey thing `omnibus
<https://github.com/wrmsr/omnibus/tree/wrmsr_exp_split>`_... ish.

Core packages begin with ``om``, scratch app is in ``app``, temp / dump code is in ``x``.

Core packages installable from git via:

.. code-block::

  pip install 'git+https://github.com/wrmsr/omlish@master#subdirectory=.pkg/<pkg>'

Core packages have no required dependencies, but numerous optional ones - see their respective ``pyproject.toml`` files
for details.

The cli is installable through uvx or pipx via:

.. code-block::

  curl -LsSf https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/cli/install.py | python3 -

Additional deps to be injected may be appended to the command.
