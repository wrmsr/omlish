from .... import marshal as msh
from ....formats import json
from ..dtypes import String
from ..elements import Column
from ..elements import CreatedAtUpdatedAt
from ..elements import Elements
from ..elements import IdIntegerPrimaryKey
from ..lower import lower_table_elements
from ..tabledefs import TableDef


def test_table_defs():
    users = TableDef(
        'users',
        Elements([
            IdIntegerPrimaryKey(),
            CreatedAtUpdatedAt(),
            Column('name', String()),
        ]),
    )
    print(users_json := json.dumps_pretty(msh.marshal(users)))

    users2 = msh.unmarshal(json.loads(users_json), TableDef)
    assert users2 == users

    users_lowered = lower_table_elements(users)
    print(json.dumps_pretty(msh.marshal(users_lowered)))

    print(users_lowered.elements.by_type[Column])
