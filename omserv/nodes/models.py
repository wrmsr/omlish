from omlish.sql import tabledefs as td


##


NODE = td.table_def(
    'nodes',

    td.Column('uuid', td.String(), not_null=True),
    td.Index(['uuid'], 'nodes_by_uuid'),

    td.CreatedAtUpdatedAt(),

    td.Column('hostname', td.String()),

    td.Column('heartbeat_at', td.Datetime()),

    td.Column('extra', td.String()),
)
