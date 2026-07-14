from omcore import inject as inj


##


def bind() -> inj.Elemental:
    return inj.as_elements()
