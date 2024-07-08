"""
lookit:
 - https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html
  - https://docs.ansible.com/ansible/latest/collections/all_plugins.html
  - https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html#comparing-loops
  - https://github.com/ansible/ansible/blob/83a0975611a3948d055c1f670f00799895b63847/lib/ansible/modules/file.py
  - https://github.com/piku/piku-bootstrap/blob/964e02357ef76ac66ac88dcf9e73ea7c00b38180/playbooks/piku.yml
"""  # noqa
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


class Play(dc.Frozen, lang.Abstract):
    pass


class File(Play, lang.Final):
    pass


class Stat(Play, lang.Final):
    pass


def _main():
    import omlish.marshal.factories  # noqa
    mf: msh.MarshalerFactory = msh.factories.TypeCacheFactory(
        msh.base.RecursiveMarshalerFactory(
            msh.factories.CompositeFactory(
                msh.polymorphism.PolymorphismMarshalerFactory(msh.polymorphism_from_subclasses(Play)),
                *msh.STANDARD_MARSHALER_FACTORIES,
            )
        )
    )


if __name__ == '__main__':
    _main()
