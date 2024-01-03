from pydantic import BaseModel, Field
from typing import List

from finance import Stock, Transaction, Holdings


class AlgorithmResult(BaseModel):
    Transactions: List[Transaction] = Field()
    Value: float
    Holdings: List[Holdings]


class StockInfo(BaseModel):
    Openings: List[float] = Field()
    Closings: List[float] = Field()


def conv_stock(s: Stock) -> StockInfo:
    return StockInfo(Openings=s.openings, Closings=s.closings)
