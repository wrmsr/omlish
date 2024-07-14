"""
https://github.com/dragansah/tpch-dbgen https://github.com/2ndQuadrant/pg-tpch
"""
import sqlalchemy as sa
import sqlalchemy.ext.declarative


Base = sa.ext.declarative.declarative_base()


class Nation(Base):
    __tablename__ = 'nation'
    __table_args__ = (
        sa.Index('nation_regionkey_index', 'regionkey'),
    )

    nationkey = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(25))
    regionkey = sa.Column(sa.Integer)
    comment = sa.Column(sa.String(152))


class Region(Base):
    __tablename__ = 'region'

    regionkey = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(25))
    comment = sa.Column(sa.String(152))


class Part(Base):
    __tablename__ = 'part'

    partkey = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(55))
    mfgr = sa.Column(sa.String(25))
    brand = sa.Column(sa.String(10))
    type = sa.Column(sa.String(25))
    size = sa.Column(sa.Integer)
    container = sa.Column(sa.String(10))
    retailprice = sa.Column(sa.DECIMAL)
    comment = sa.Column(sa.String(23))


class Supplier(Base):
    __tablename__ = 'supplier'
    __table_args__ = (
        sa.Index('supplier_nationkey_index', 'nationkey'),
    )

    suppkey = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(25))
    address = sa.Column(sa.String(40))
    nationkey = sa.Column(sa.Integer)
    phone = sa.Column(sa.String(15))
    acctbal = sa.Column(sa.DECIMAL)
    comment = sa.Column(sa.String(101))


class PartSupp(Base):
    __tablename__ = 'partsupp'
    __table_args__ = (
        sa.Index('partsupp_suppkey_partkey_index', 'suppkey', 'partkey'),
    )

    partkey = sa.Column(sa.Integer, primary_key=True)
    suppkey = sa.Column(sa.Integer, primary_key=True)
    availqty = sa.Column(sa.Integer)
    supplycost = sa.Column(sa.DECIMAL)
    comment = sa.Column(sa.String(199))


class Customer(Base):
    __tablename__ = 'customer'
    __table_args__ = (
        sa.Index('customer_nationkey_index', 'nationkey'),
    )

    custkey = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(25))
    address = sa.Column(sa.String(40))
    nationkey = sa.Column(sa.Integer)
    phone = sa.Column(sa.String(15))
    acctbal = sa.Column(sa.DECIMAL)
    mktsegment = sa.Column(sa.String(10))
    comment = sa.Column(sa.String(117))


class Order(Base):
    __tablename__ = 'order'
    __table_args__ = (
        sa.Index('order_custkey_index', 'custkey'),
    )

    orderkey = sa.Column(sa.Integer, primary_key=True)
    custkey = sa.Column(sa.Integer)
    orderstatus = sa.Column(sa.String(1))
    totalprice = sa.Column(sa.DECIMAL)
    orderdate = sa.Column(sa.Date)
    orderpriority = sa.Column(sa.String(15))
    clerk = sa.Column(sa.String(15))
    shippriority = sa.Column(sa.Integer)
    comment = sa.Column(sa.String(79))


class LineItem(Base):
    __tablename__ = 'lineitem'
    __table_args__ = (
        sa.Index('lineitem_partkey_index', 'partkey'),
        sa.Index('lineitem_suppkey_index', 'suppkey'),
    )

    orderkey = sa.Column(sa.Integer, primary_key=True)
    partkey = sa.Column(sa.Integer)
    suppkey = sa.Column(sa.Integer)
    linenumber = sa.Column(sa.Integer, primary_key=True)
    quantity = sa.Column(sa.DECIMAL)
    extendedprice = sa.Column(sa.DECIMAL)
    discount = sa.Column(sa.DECIMAL)
    tax = sa.Column(sa.DECIMAL)
    returnflag = sa.Column(sa.String(1))
    linestatus = sa.Column(sa.String(1))
    shipdate = sa.Column(sa.Date)
    commitdate = sa.Column(sa.Date)
    receiptdate = sa.Column(sa.Date)
    shipinstruct = sa.Column(sa.String(25))
    shipmode = sa.Column(sa.String(10))
    comment = sa.Column(sa.String(44))
