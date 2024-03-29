import dataclasses
import logging
import uuid

from .exceptions import AmountIsZeroException, NotEnoughStocksToSellException
from .stock import Stock
from .enums import TransactionType
from .transaction import Transaction
from typing import List, Dict
from utils import get_ticker

from collections import defaultdict


@dataclasses.dataclass
class Holdings:
    name: str
    quantity: int
    valuation: float


class Portfolio:

    def __init__(self, initial_cash=0.0, allow_short=False):
        self.ID = uuid.uuid4()
        self.Cash: float = initial_cash
        self.AllowShort: bool = allow_short

        self.__transactions__: List[Transaction] = []
        self.__holdings__: Dict[Stock, int] = defaultdict(lambda: 0)

    def buy(self, stock: Stock, quantity: int):
        if quantity == 0:
            raise Exception("Stock buy can't be 0")

        amount = stock.close * quantity

        if self.Cash < amount:
            raise Exception("Not enough money to buy")

        logging.debug(f"Buying {stock.name} q={quantity} p={stock.close} amount={amount}")

        self.__transactions__.append(
            Transaction(Tick=get_ticker().value, Type=TransactionType.BUY, StockName=stock.name,
                        Quantity=quantity, Price=stock.close, Amount=amount))
        self.Cash -= amount

        self.__holdings__[stock] += quantity

    def buy_amount(self, stock: Stock, amount: float) -> int:
        q = int(amount // stock.close)
        self.buy(stock, q)

        return q

    def sell(self, stock: Stock, quantity: int):
        if quantity == 0:
            raise AmountIsZeroException("Stock sell can't be 0")

        if not self.AllowShort and quantity > self.get_holding(stock).quantity:
            raise NotEnoughStocksToSellException("Not enough stocks to sell")

        amount = stock.close * quantity

        logging.debug(f"Selling {stock.name} q={quantity} p={stock.close} amount={amount}")

        self.__transactions__.append(
            Transaction(Tick=get_ticker().value, Type=TransactionType.SELL, StockName=stock.name,
                        Quantity=quantity, Price=stock.close, Amount=amount))

        self.Cash += amount
        self.__holdings__[stock] -= quantity

    def sell_amount(self, stock: Stock, amount: float) -> int:
        q = int(amount // stock.close)
        self.sell(stock, q)

        return q

    def get_stock_transactions(self, stock: Stock) -> List[Transaction]:
        return list(filter(lambda x: x.StockName == stock.name, self.__transactions__))

    def get_all_transactions(self) -> List[Transaction]:
        return list(self.__transactions__)

    def get_holding(self, stock: Stock) -> Holdings:
        q = self.__holdings__[stock]

        return Holdings(name=stock.name, quantity=q, valuation=q * stock.close)

    def square_off(self, stocks: List[Stock]):
        """
        Squares off all remaining stocks of the list of stocks provided
        Args:
            stocks: the stocks who are to be squared off
        Returns:
        """
        for holding, qty in self.__holdings__.items():
            if holding not in stocks:
                continue

            if qty > 0:
                self.sell(holding, qty)
            elif qty < 0:
                self.buy(holding, -qty)

    @property
    def holdings(self) -> List[Holdings]:
        res = []
        for k, v in self.__holdings__.items():
            res.append(Holdings(name=k.name, quantity=v, valuation=v * k.close))

        return res
