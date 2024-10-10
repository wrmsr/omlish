import json
import os.path


def _main() -> None:
    nb_file = os.path.join(os.path.dirname(__file__), 'dp', 'dp20240312_llamafs', 'llama.ipynb')
    with open(nb_file) as f:
        dct = json.load(f)

    code_cells = [c for c in dct['cells'] if c['cell_type'] == 'code']
    for i, c in enumerate(code_cells):
        if i:
            print('\n##\n')
        print(''.join(c['source']))


if __name__ == '__main__':
    _main()
