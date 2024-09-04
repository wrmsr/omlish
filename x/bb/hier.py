import hashlib
import numbers


def hier_write(output, obj):
    if isinstance(obj, dict):
        conv_keys = {}

        for key in obj.keys():
            if isinstance(key, str):
                conv_key = key
            elif isinstance(key, bool):
                conv_key = 'true' if key else 'false'
            elif isinstance(key, numbers.Integral) or isinstance(key, numbers.Real):
                conv_key = str(key)
            elif key is None:
                conv_key = 'null'
            else:
                raise KeyError(key)

            if conv_key in conv_keys:
                raise KeyError(conv_key)

            conv_keys[conv_key] = key

        output('{')

        need_comma = False
        for conv_key in sorted(conv_keys.keys()):
            if need_comma:
                output(',')
            else:
                need_comma = True

            output('"')
            output(conv_key)
            output('":')

            hier_write(output, obj[conv_keys[conv_key]])

        output('}')

    elif isinstance(obj, list):
        output('[')

        need_comma = False
        for item in obj:
            if need_comma:
                output(',')
            else:
                need_comma = True

            hier_write(output, item)

        output(']')

    elif isinstance(obj, str):
        output('"')
        output(obj)
        output('"')

    elif isinstance(obj, bool):
        output('true' if obj else 'false')

    elif isinstance(obj, numbers.Integral) or isinstance(obj, numbers.Real):
        output(str(obj))

    elif obj is None:
        output('null')

    else:
        raise TypeError(obj)


def hier_hash(obj, hash_alg=hashlib.sha1, use_hexdigest=False):
    hash_obj = hash_alg()

    hier_write(hash_obj.update, obj)

    if use_hexdigest:
        return hash_obj.hexdigest()
    else:
        return hash_obj.digest()
