import json
from enum import Enum
from typing import List, Dict

import pandas
import yfinance as yf

from utils import get_ticker

DATETIME_COLNAME = "Date"
OPEN_COLNAME = "Open"
HIGH_COLNAME = "High"
LOW_COLNAME = "Low"
CLOSE_COLNAME = "Close"
VOLUME_COLNAME = "Volume"

NAME_KEY = "Name"
DATAFRAME_KEY = "df"


class ValueKind(Enum):
    """
    ValueKind is the kind of value to return for calculation
    """
    Open = OPEN_COLNAME
    Close = CLOSE_COLNAME
    High = HIGH_COLNAME
    Low = LOW_COLNAME

    @staticmethod
    def to_colname(kind) -> str:
        """
        Returns the colname corresponding to the colname
        Args:
            kind: Kind whose colname is needed

        Returns: the colname
        """
        match kind:
            case ValueKind.Open:
                return OPEN_COLNAME
            case ValueKind.Close:
                return CLOSE_COLNAME
            case ValueKind.High:
                return HIGH_COLNAME
            case ValueKind.Low:
                return LOW_COLNAME

        return CLOSE_COLNAME


class Stock:
    def __init__(self, name: str, skip_loading=False, period="7d", interval="1m"):
        self.name = name
        self.df: pandas.DataFrame = pandas.DataFrame()

        if not skip_loading:
            self.df = self.load_from_yahoo(period, interval)

    def load_from_yahoo(self, period, interval) -> pandas.DataFrame:
        ticker = yf.Ticker(self.name)
        return ticker.history(period=period, interval=interval)

    def get_history(self) -> pandas.DataFrame:
        return self.df

    @classmethod
    def fromJSON(cls, json_str: str):
        """
        Returns a stock object reading from json
        Args:
            json_str: expects "Name" as name of the stock, "df" as the dataframe json dump

        Returns:
            an object of type stock
        """
        json_dict: Dict = json.loads(json_str)

        s = Stock(json_dict[NAME_KEY], skip_loading=True)
        s.df = pandas.read_json(json_dict[DATAFRAME_KEY])
        return s

    def toJSON(self) -> str:
        d = {
            NAME_KEY: self.name,
            DATAFRAME_KEY: self.df.to_json()
        }

        return json.dumps(d, sort_keys=True, indent=4)

    def values(self, kind: ValueKind = ValueKind.Close) -> List[float]:
        """
        Returns the list of values
        Args:
            kind: the kind of values you want

        Returns:

        """
        return list(self.df[ValueKind.to_colname(kind)])

    def __get_value__(self, kind: ValueKind):
        """
        Returns the value of the stock at current time
        Args:
            kind: Kind of value to be returned

        Returns:
            float value to be returned
        """
        column = self.df[ValueKind.to_colname(kind)]
        return column.iloc[min(len(column) - 1, get_ticker().value)]

    @property
    def close(self) -> float:
        return self.__get_value__(kind=ValueKind.Close)

    @property
    def open(self) -> float:
        return self.__get_value__(kind=ValueKind.Open)

    @property
    def low(self) -> float:
        return self.__get_value__(kind=ValueKind.Low)

    @property
    def high(self) -> float:
        return self.__get_value__(kind=ValueKind.High)
