import importlib.resources


WIKI_FILES = {
    fn.name: fn.read_text()
    for fn in importlib.resources.files(__package__).iterdir()
    if fn.name.endswith('.wiki')
}
