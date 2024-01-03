import logging
from http import HTTPStatus
from typing import List, Annotated

from fastapi import FastAPI, HTTPException, Depends, Query

import database
import finance
from .stock_info import StockInfo, conv_stock, AlgorithmResult

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/{symbol}")
async def post_symbol(symbol: finance.Symbols, data: database.StockData = Depends(database.get_singleton)) -> StockInfo:
    """

    Args:
        symbol: the symbol you want to add in the trading computation
        data: database singleton object

    Returns:

    """
    # if already in database skip adding
    stk = data.get_by_name(symbol)
    if stk is not None:
        return conv_stock(stk)

    stk = finance.Stock(symbol)
    data.insert(stk)
    return conv_stock(stk)


@app.delete("/{symbol}")
async def delete_symbol(symbol: finance.Symbols, data: database.StockData = Depends(database.get_singleton)):
    """

    Args:
        symbol: the symbol you want to delete in the trading computation
        data: database singleton object

    Returns:

    """
    stk = data.get_by_name(symbol)
    if stk is None:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="Stock not found")

    data.delete(stk.name)


@app.get("/{symbol}/history")
async def get_history(symbol: finance.Symbols, data: database.StockData = Depends(database.get_singleton)) -> StockInfo:
    """

    Args:
        data: database singleton object
        symbol: Symbol is the symbol you are looking for

    Returns:
        the symbol's history

    """
    stk = data.get_by_name(symbol)
    if stk is None:
        raise HTTPException(status_code=404, detail="Symbol not found, kindly register it first using /add_symbol")

    return conv_stock(stk)


@app.post("/algorithm/{algo}")
async def post_algorithm(algo: finance.Algos, cash: int, stocks: List[str],
                         threshold: Annotated[float, Query(title="threshold",
                                                           description="accepted percentage change before buying")] = 0.5,
                         volatility: Annotated[
                             float, Query(title="volatility", description="accepted volatility when buying")] = 0.5,
                         data: database.StockData = Depends(database.get_singleton)) -> AlgorithmResult:
    if volatility < 0 or volatility > 1:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Volatility should be between 0 and 1")

    if threshold < 0 or threshold > 1:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Threshold should be between 0 and 1")
    # portfolio is the which will be produced by the algorithm
    p: finance.Portfolio

    stock = []
    for s in stocks:
        val = data.get_by_name(s)
        if val is None:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"stock {s} not found")
        else:
            stock.append(val)

    match algo:
        case finance.Algos.A:
            p = finance.Algorithms.A(cash=cash, stocks=stock)
        case finance.Algos.percent:
            p = finance.Algorithms.Threshold(cash=cash, stocks=stock, threshold=threshold, volatility=volatility)
        case _:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Algorithm not found")

    return AlgorithmResult(Transactions=p.get_all_transactions(), Value=p.Cash,
                           Holdings=p.holdings)
