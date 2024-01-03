from dataclasses import dataclass

from .enums import TransactionType


@dataclass
class Transaction:
    Tick: int
    Type: TransactionType
    StockName: str
    Quantity: int
    Price: float
    Amount: float
