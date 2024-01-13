import logging
from http import HTTPStatus
from typing import List, Annotated

from fastapi import FastAPI, HTTPException, Depends, Query, Body

import database
import finance
from .stock_info import StockInfo, conv_stock, AlgorithmResult

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/{symbol}")
async def post_symbol(symbol: finance.Symbols,
                      period: Annotated[str, Query(title="period", description="time period of data")] = "7d",
                      interval: Annotated[str, Query(title="interval", description="interval between ticks")] = "1m",
                      no_cache: Annotated[
                          bool, Query(title="no_cache", description="Whether we want to skip cached data")] = False,
                      data: database.StockData = Depends(database.get_singleton)) -> StockInfo:
    """

    Args:
        no_cache: skip cache data
        interval: interval between ticks
        period: time period for what you want the stock data
        symbol: the symbol you want to add in the trading computation
        data: database singleton object

    Returns:

    """
    # if already in database skip adding
    stk = data.get_by_name(symbol)
    # if caching is allowed and cache data is there return cache
    if not no_cache and stk is not None:
        return conv_stock(stk)

    stk = finance.Stock(symbol, period=period, interval=interval)
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
async def post_algorithm(algo: finance.Algos,
                         cash: Annotated[int, Query(description="Amount of cash for the transaction")],
                         stocks: Annotated[
                             List[str], Body(description="stocks to be taken under consideration for computation",
                                             examples=[["rvnl.ns"]])],
                         threshold: Annotated[
                             float, Query(description="accepted percentage change before buying")] = 0.5,
                         volatility: Annotated[
                             float, Query(description="accepted volatility when buying")] = 0.5,
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
