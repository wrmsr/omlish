def build_attr_tuple_str(obj_name: str, *attrs: str) -> str:
    # Return a string representing each field of obj_name as a tuple member.  So, if fields is ['x', 'y'] and obj_name
    # is "self", return "(self.x,self.y)".

    # Special case for the 0-tuple.
    if not attrs:
        return '()'

    # Note the trailing comma, needed if this turns out to be a 1-tuple.
    return f'({",".join([f"{obj_name}.{a}" for a in attrs])},)'
