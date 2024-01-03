import logging
from typing import List, Dict

from finance import Portfolio, Stock
from utils import get_ticker


class Algorithms:

    @staticmethod
    def A(cash: float, stocks: List[Stock]) -> Portfolio:
        p = Portfolio(initial_cash=cash)
        t = get_ticker()
        t.reset()

        total = len(stocks[0].openings)
        q = 0
        for i in range(total):
            if t.value in [int(0.05 * total), int(0.35 * total), int(0.65 * total), int(0.75 * total),
                           int(0.95 * total)]:
                q = p.buy_amount(stocks[0], cash / 5)

            if t.value in [int(0.25 * total), int(0.41 * total), int(0.70 * total), int(0.90 * total),
                           int(0.99 * total)]:
                p.sell(stocks[0], q)

            t.tick()
        return p

    @staticmethod
    def TenPercent(cash: float, stocks: List[Stock], percent: float) -> Portfolio:
        p = Portfolio(initial_cash=cash)
        t = get_ticker()
        t.reset()

        locked_price: Dict[Stock, float] = {}
        for s in stocks:
            locked_price[s] = s.value
            print(s.value)

        for i in range(len(stocks[0].openings)):
            for s in stocks:
                cp = s.value
                lp = locked_price[s]
                if (lp - cp) / lp > percent:
                    try:
                        p.buy_amount(s, int(p.Cash * percent))
                        lp = 0.5 * lp + 0.5 * cp
                        locked_price[s] = lp
                    except:
                        pass

                if (cp - lp) / lp > percent:
                    try:
                        p.sell(s, int(p.get_holding(s).quantity * percent))
                        lp = 0.5 * lp + 0.5 * cp
                        locked_price[s] = lp
                    except:
                        pass

            t.tick()
        logging.info("Trying to sell remaining stocks")
        for s in stocks:
            try:
                p.sell(s, p.get_holding(s).quantity)
            except:
                pass
        return p
