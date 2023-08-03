ALL: list[type] = []


def register_plugin(obj):
    ALL.append(obj)
    return obj
