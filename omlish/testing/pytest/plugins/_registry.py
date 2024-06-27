ALL: list[type] = []


def register(obj):
    ALL.append(obj)
    return obj
