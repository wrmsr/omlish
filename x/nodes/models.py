from omlish.sql import tabledefs as td


##


NODES = td.table_def(
    'nodes',

    td.Column('uuid', td.String()),
    td.Index(['uuid'], 'nodes_by_uuid'),

    td.CreatedAtUpdatedAt(),

    td.Column('hostname', td.String(), nullable=True),

    td.Column('heartbeat_at', td.Datetime(), nullable=True),

    td.Column('extra', td.String(), nullable=True),
)
