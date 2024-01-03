import json
import logging
import statistics
from typing import List, Dict

import pandas
import yfinance as yf

from utils import get_ticker

DATETIME_COLNAME = "Datetime"
OPEN_COLNAME = "Open"
CLOSE_COLNAME = "Close"
NAME_KEY = "name"


def __create_dataframe__(opens: List[float], closes: List[float]) -> pandas.DataFrame:
    df = pandas.DataFrame()
    df[OPEN_COLNAME] = opens
    df[CLOSE_COLNAME] = closes
    df[DATETIME_COLNAME] = list(range(len(df[OPEN_COLNAME])))
    return df


class Stock:
    def __init__(self, name: str, skip_loading=False, period="7d", interval="1m"):
        self.name = name
        self.df: pandas.DataFrame = pandas.DataFrame()

        if not skip_loading:
            ticker = yf.Ticker(self.name)
            history_df = ticker.history(period=period, interval=interval)
            self.df = __create_dataframe__(history_df[OPEN_COLNAME], history_df[CLOSE_COLNAME])

    def get_history(self) -> pandas.DataFrame:
        return self.df

    @staticmethod
    def fromJSON(json_dict: Dict):
        s = Stock(json_dict[NAME_KEY], skip_loading=True)
        s.df = __create_dataframe__(json_dict[OPEN_COLNAME], json_dict[CLOSE_COLNAME])
        return s

    def toJSON(self) -> str:
        d = {
            NAME_KEY: self.name,
            OPEN_COLNAME: list(self.openings),
            CLOSE_COLNAME: list(self.closings)
        }

        return json.dumps(d, sort_keys=True, indent=4)

    @property
    def openings(self) -> List[float]:
        return list(self.df[OPEN_COLNAME])

    @property
    def closings(self) -> List[float]:
        return list(self.df[CLOSE_COLNAME])

    @property
    def value(self) -> float:
        return self.openings[min(len(self.openings) - 1, get_ticker().value)]
