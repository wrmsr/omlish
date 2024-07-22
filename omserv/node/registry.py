# import asyncio
# import contextlib
#
# import sqlalchemy as sa
# import sqlalchemy.ext.asyncio
#
# from omlish import check
#
#
# meta = sa.MetaData()
#
#
# _nodes_table = sa.Table(
#     '_nodes',
#     meta,
#     sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
#     sa.Column('name', sa.String(50), nullable=False, unique=True),
# )
#
#
# class NodeRegistry:
#     pass
