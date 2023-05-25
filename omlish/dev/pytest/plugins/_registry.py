import typing as ta


ALL: ta.List[type] = []


def register_plugin(obj):
    ALL.append(obj)
    return obj
