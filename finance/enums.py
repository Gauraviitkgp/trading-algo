from enum import Enum


class Symbols(str, Enum):
    MICROSOFT = "msft"
    RAIL_VIKAS_NIGAM_LIMITED = "rvnl.ns"
    MAHABANK = "mahabank.ns"
    MSUMI = "msumi.ns"


class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class Algos(str, Enum):
    A = "A"
    percent = "percent"
