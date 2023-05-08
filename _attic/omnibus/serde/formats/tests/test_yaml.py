from .. import yaml as yaml_
from .yaml_examples import Examples


def test_yaml():
    for name in Examples:
        buf = Examples(name)

        print('#######################')
        print(name)
        print()
        print(buf)
        print()

        try:
            loader = yaml_.WrappedLoaders.base(buf)
            vals = []
            try:
                while loader.check_data():
                    vals.append(loader.get_data())
            finally:
                loader.dispose()
        except Exception as e:
            print('ERROR:')
            print(e)
        else:
            print(vals)
            print([yaml_.unwrap(v) for v in vals])

        print()
        print()
