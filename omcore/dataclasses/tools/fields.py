import dataclasses as dc


##


def install_class_field_attrs():
    def inner(cls):
        for f in dc.fields(cls):
            setattr(cls, f.name, f)
        return cls

    return inner
