from typing import List, Dict

import pandas as pd
import numpy as py
# from lightweight_charts import Chart
import plotly.graph_objects as go
import time

from lightweight_charts import Chart

import database
import finance


# transactions: List[finance.Transaction] = [
#     finance.Transaction(
#         Tick=211,
#         Type=finance.TransactionType.BUY,
#         StockName="msumi.ns",
#         Quantity=4,
#         Price=165,
#         Amount=4 * 165,
#     ),
#     finance.Transaction(
#         Tick=290,
#         Type=finance.TransactionType.SELL,
#         StockName="msumi.ns",
#         Quantity=4,
#         Price=166,
#         Amount=4 * 166,
#     )
# ]


def plot(s: finance.Stock, transactions: List[finance.Transaction] = None):
    if transactions is None:
        transactions = []
    # https://github.com/louisnw01/lightweight-charts-python
    dataframe = s.df.rename(
        columns={finance.OPEN_COLNAME: "open", finance.CLOSE_COLNAME: "close", finance.HIGH_COLNAME: "high",
                 finance.LOW_COLNAME: "low"},
        inplace=False)

    chart = Chart()
    chart.grid(vert_enabled=True, horz_enabled=True)
    chart.legend(visible=True, font_family='Trebuchet MS', ohlc=True, percent=True)
    chart.layout(background_color='#131722', font_family='Trebuchet MS', font_size=16)
    chart.set(dataframe.iloc[:1])
    chart.show()

    ticks: Dict[int, finance.Transaction] = {t.Tick: t for t in transactions}
    tick = 1
    for i, series in dataframe.iterrows():
        chart.update(series)
        if tick in ticks:
            trans = ticks[tick]
            if trans.Type == finance.TransactionType.BUY:
                chart.marker(text="BUY", color="Green")
            if trans.Type == finance.TransactionType.SELL:
                chart.marker(text="SELL", color="Red")

        time.sleep(0.1)
        tick += 1


def plot_plotly(s: finance.Stock):
    """
    Plots a plotly graph of the stock
    Args:
        s: finance stock
    """
    # https://plotly.com/python/candlestick-charts/#simple-example-with-datetime-objects
    fig = go.Figure(
        data=[go.Candlestick(x=s.df.index,
                             open=s.df[finance.OPEN_COLNAME],
                             close=s.values(kind=finance.ValueKind.Close),
                             low=s.values(kind=finance.ValueKind.Low),
                             high=s.values(kind=finance.ValueKind.High))]
    )

    fig.show()
