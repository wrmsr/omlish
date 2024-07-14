# flake8: noqa
from .. import ents as ents_  # noqa


EXPECTED_REGIONS = [
    ents_.Region(
        row_number=0,
        region_key=0,
        name="AFRICA",
        comment="lar deposits. blithely final packages cajole. regular waters are final requests. regular accounts are according to ",
    ),
    ents_.Region(
        row_number=1,
        region_key=1,
        name="AMERICA",
        comment="hs use ironic, even requests. s",
    ),
]


EXPECTED_CUSTOMERS = [
    ents_.Customer(
        row_number=1,
        customer_key=1,
        name="Customer#000000001",
        address="IVhzIApeRb ot,c,E",
        nation_key=15,
        phone="25-989-741-2988",
        account_balance=71156,
        market_segment="BUILDING",
        comment="to the even, regular platelets. regular, ironic epitaphs nag e",
    ),
    ents_.Customer(
        row_number=2,
        customer_key=2,
        name="Customer#000000002",
        address="XSTf4,NCwDVaWNe6tEgvwfmRchLXak",
        nation_key=13,
        phone="23-768-687-3665",
        account_balance=12165,
        market_segment="AUTOMOBILE",
        comment="l accounts. blithely ironic theodolites integrate boldly: caref",
    ),
]
