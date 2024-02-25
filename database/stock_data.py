import datetime
import json

import finance
from redislite import Redis


class StockData:
    def __init__(self):
        self.__conn__ = Redis('./data/symbols.db')

    def insert(self, s: finance.Stock):
        """
        Inserts a stock into the database with an expiry of 7 days
        Args:
            s: the stock that you want to insert
        """
        self.__conn__.set(s.name, s.toJSON(), ex=datetime.timedelta(days=7))

    def get_all(self) -> [finance.Stock]:
        """
        Fetches all the stocks in the database
        Returns:
            List of stock objects
        """
        keys = self.__conn__.keys()
        res: [finance.Stock] = []
        for key in keys:
            res.append(self.get_by_name(key))

        return res

    def get_by_name(self, name: str) -> finance.Stock | None:
        """
        Fetches the stock by its name
        Args:
            name: name of the stock you want to get

        Returns:
            Stock object if no stock with name exists else None
        """
        val = self.__conn__.get(name)
        if val is None:
            return None

        return finance.Stock.fromJSON(json.loads(self.__conn__.get(name)))

    def delete(self, key: str):
        """
        Deletes a stock object or deletes the key
        Args:
            key: the key to delete
            stk: the stock object you want to delete.
        """
        if key == "":
            raise Exception("key cannot be empty")

        self.__conn__.delete(key)


Singleton: StockData = StockData()


def get_singleton() -> StockData:
    return Singleton
