"""
TODO:
 - move to dev? currently only srcdist dev, no _ext :|
 - dc metaclass metadata
 - fk linkage

https://github.com/databricks/tpch-dbgen
"""
import typing as ta

from .. import dataclasses as dc
from .. import lang


class Meta(dc.Pure):
    primary_key: ta.Sequence[str]
    indices: ta.Sequence[ta.Sequence[str]] = ()


class Column(dc.Pure):
    class Type(lang.AutoEnum):
        INTEGER = ...
        IDENTIFIER = ...
        DATE = ...
        DOUBLE = ...
        VARCHAR = ...

    name: str
    type: Type
    precision: ta.Optional[int] = dc.field(0, kwonly=True)
    scale: ta.Optional[int] = dc.field(0, kwonly=True)


class Entity(dc.Enum):
    row_number: int


class Region(Entity):
    dc.metadata({Meta: Meta(['region_key'])})

    region_key: int = dc.field(metadata={Column: Column('r_regionkey', Column.Type.IDENTIFIER)})
    name: str = dc.field(metadata={Column: Column('r_name', Column.Type.VARCHAR, precision=25)})
    comment: str = dc.field(metadata={Column: Column('r_comment', Column.Type.VARCHAR, precision=152)})


class Nation(Entity):
    dc.metadata({Meta: Meta(['nation_key'], [['region_key']])})

    nation_key: int = dc.field(metadata={Column: Column('n_nationkey', Column.Type.IDENTIFIER)})
    name: str = dc.field(metadata={Column: Column('n_name', Column.Type.VARCHAR, precision=25)})
    region_key: int = dc.field(metadata={Column: Column('n_regionkey', Column.Type.IDENTIFIER)})
    comment: str = dc.field(metadata={Column: Column('n_comment', Column.Type.VARCHAR, precision=152)})


class Part(Entity):
    dc.metadata({Meta: Meta(['part_key'])})

    part_key: int = dc.field(metadata={Column: Column('p_partkey', Column.Type.IDENTIFIER)})
    name: str = dc.field(metadata={Column: Column('p_name', Column.Type.VARCHAR, precision=55)})
    manufacturer: str = dc.field(metadata={Column: Column('p_mfgr', Column.Type.VARCHAR, precision=25)})
    brand: str = dc.field(metadata={Column: Column('p_brand', Column.Type.VARCHAR, precision=10)})
    type: str = dc.field(metadata={Column: Column('p_type', Column.Type.VARCHAR, precision=25)})
    size: int = dc.field(metadata={Column: Column('p_size', Column.Type.INTEGER)})
    container: str = dc.field(metadata={Column: Column('p_container', Column.Type.VARCHAR, precision=10)})
    retail_price: int = dc.field(metadata={Column: Column('p_retailprice', Column.Type.DOUBLE)})
    comment: str = dc.field(metadata={Column: Column('p_comment', Column.Type.VARCHAR, precision=23)})


class Supplier(Entity):
    dc.metadata({Meta: Meta(['supplier_key'], [['nation_key']])})

    supplier_key: int = dc.field(metadata={Column: Column('s_suppkey', Column.Type.IDENTIFIER)})
    name: str = dc.field(metadata={Column: Column('s_name', Column.Type.VARCHAR, precision=25)})
    address: str = dc.field(metadata={Column: Column('s_address', Column.Type.VARCHAR, precision=40)})
    nation_key: int = dc.field(metadata={Column: Column('s_nationkey', Column.Type.IDENTIFIER)})
    phone: str = dc.field(metadata={Column: Column('s_phone', Column.Type.VARCHAR, precision=15)})
    account_balance: int = dc.field(metadata={Column: Column('s_acctbal', Column.Type.DOUBLE)})
    comment: str = dc.field(metadata={Column: Column('s_comment', Column.Type.VARCHAR, precision=101)})


class PartSupplier(Entity):
    dc.metadata({Meta: Meta(['part_key', 'supplier_key'], [['supplier_key', 'part_key']])})

    part_key: int = dc.field(metadata={Column: Column('ps_partkey', Column.Type.IDENTIFIER)})
    supplier_key: int = dc.field(metadata={Column: Column('ps_suppkey', Column.Type.IDENTIFIER)})
    available_quantity: int = dc.field(metadata={Column: Column('ps_availqty', Column.Type.INTEGER)})
    supply_cost: int = dc.field(metadata={Column: Column('ps_supplycost', Column.Type.DOUBLE)})
    comment: str = dc.field(metadata={Column: Column('ps_comment', Column.Type.VARCHAR, precision=199)})


class Customer(Entity):
    dc.metadata({Meta: Meta(['customer_key'], [['nation_key']])})

    customer_key: int = dc.field(metadata={Column: Column('c_custkey', Column.Type.IDENTIFIER)})
    name: str = dc.field(metadata={Column: Column('c_name', Column.Type.VARCHAR, precision=25)})
    address: str = dc.field(metadata={Column: Column('c_address', Column.Type.VARCHAR, precision=40)})
    nation_key: int = dc.field(metadata={Column: Column('c_nationkey', Column.Type.IDENTIFIER)})
    phone: str = dc.field(metadata={Column: Column('c_phone', Column.Type.VARCHAR, precision=25)})
    account_balance: int = dc.field(metadata={Column: Column('c_acctbal', Column.Type.DOUBLE)})
    market_segment: str = dc.field(metadata={Column: Column('c_mktsegment', Column.Type.VARCHAR, precision=10)})
    comment: str = dc.field(metadata={Column: Column('c_comment', Column.Type.VARCHAR, precision=117)})


class Order(Entity):
    dc.metadata({Meta: Meta(['order_key'], [['customer_key']])})

    order_key: int = dc.field(metadata={Column: Column('o_orderkey', Column.Type.IDENTIFIER)})
    customer_key: int = dc.field(metadata={Column: Column('o_custkey', Column.Type.IDENTIFIER)})
    order_status: str = dc.field(metadata={Column: Column('o_orderstatus', Column.Type.VARCHAR, precision=1)})
    total_price: int = dc.field(metadata={Column: Column('o_totalprice', Column.Type.DOUBLE)})
    order_date: int = dc.field(metadata={Column: Column('o_orderdate', Column.Type.DATE)})
    order_priority: str = dc.field(metadata={Column: Column('o_orderpriority', Column.Type.VARCHAR, precision=15)})
    clerk: str = dc.field(metadata={Column: Column('o_clerk', Column.Type.VARCHAR, precision=15)})
    ship_priority: int = dc.field(metadata={Column: Column('o_shippriority', Column.Type.INTEGER)})
    comment: str = dc.field(metadata={Column: Column('o_comment', Column.Type.VARCHAR, precision=79)})


class LineItem(Entity):
    dc.metadata({Meta: Meta(['order_key', 'line_number'], [['part_key'], ['supp_key']])})

    order_key: int = dc.field(metadata={Column: Column('l_orderkey', Column.Type.IDENTIFIER)})
    part_key: int = dc.field(metadata={Column: Column('l_partkey', Column.Type.IDENTIFIER)})
    supplier_key: int = dc.field(metadata={Column: Column('l_suppkey', Column.Type.IDENTIFIER)})
    line_number: int = dc.field(metadata={Column: Column('l_linenumber', Column.Type.INTEGER)})
    quantity: int = dc.field(metadata={Column: Column('l_quantity', Column.Type.DOUBLE)})
    extended_price: int = dc.field(metadata={Column: Column('l_extendedprice', Column.Type.DOUBLE)})
    discount: int = dc.field(metadata={Column: Column('l_discount', Column.Type.DOUBLE)})
    tax: int = dc.field(metadata={Column: Column('l_tax', Column.Type.DOUBLE)})
    return_flag: str = dc.field(metadata={Column: Column('l_returnflag', Column.Type.VARCHAR, precision=1)})
    status: str = dc.field(metadata={Column: Column('l_linestatus', Column.Type.VARCHAR, precision=1)})
    ship_date: int = dc.field(metadata={Column: Column('l_shipdate', Column.Type.DATE)})
    commit_date: int = dc.field(metadata={Column: Column('l_commitdate', Column.Type.DATE)})
    receipt_date: int = dc.field(metadata={Column: Column('l_receiptdate', Column.Type.DATE)})
    ship_instructions: str = dc.field(metadata={Column: Column('l_shipinstruct', Column.Type.VARCHAR, precision=25)})
    ship_mode: str = dc.field(metadata={Column: Column('l_shipmode', Column.Type.VARCHAR, precision=10)})
    comment: str = dc.field(metadata={Column: Column('l_comment', Column.Type.VARCHAR, precision=44)})


ENTITIES: ta.Sequence[ta.Type[Entity]] = (
    Customer,
    LineItem,
    Nation,
    Order,
    Part,
    PartSupplier,
    Region,
    Supplier,
)
