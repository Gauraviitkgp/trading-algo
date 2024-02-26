from pydantic import BaseModel, Field
from typing import List, Annotated

import finance
from finance import Stock, Transaction, Holdings


class AlgorithmResult(BaseModel):
    ID: Annotated[str, Field(description="ID corresponding to the algorithm result")]
    Transactions: Annotated[List[Transaction], Field(description="The transactions corresponding to the algorithm")]
    Value: Annotated[float, Field(description="Final Value after the algorithm has been run")]
    Holdings: Annotated[List[Holdings], Field(description="Current Holdings")]


class StockInfo(BaseModel):
    Openings: List[float] = Field()
    Closings: List[float] = Field()


def conv_stock(s: Stock) -> StockInfo:
    return StockInfo(Openings=s.values(finance.ValueKind.Open), Closings=s.values())
