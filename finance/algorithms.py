import logging
from typing import List, Dict

from finance import Portfolio, Stock, AmountIsZeroException, NotEnoughStocksToSellException
from utils import get_ticker


class Algorithms:

    @staticmethod
    def A(cash: float, stocks: List[Stock]) -> Portfolio:
        p = Portfolio(initial_cash=cash)
        t = get_ticker()
        t.reset()

        total = len(stocks[0].values())
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
    def Threshold(cash: float, stocks: List[Stock], threshold: float, volatility: float) -> Portfolio:
        # Declare a new portfolio and reset the ticker
        p = Portfolio(initial_cash=cash, allow_short=True)
        t = get_ticker()
        t.reset()

        # Store the initial price as the locked price
        locked_price: Dict[Stock, float] = {}
        for stk in stocks:
            locked_price[stk] = stk.close

        total_timeline: int = len(stocks[0].values())

        for i in range(total_timeline):
            for stk in stocks:
                # cp is current price, lp is the locked price
                cp = stk.close
                lp = locked_price[stk]
                diff = (lp - cp) / lp
                # if the relative difference between lp and cp is greater than threshold, buy it
                if diff > threshold:
                    try:
                        p.buy_amount(stk, cash * threshold)
                        # new lock price is the mixture of previous lock price and current price in terms of volatility
                        lp = (1 - volatility) * lp + volatility * cp
                        locked_price[stk] = lp
                    except Exception as e:
                        # if cannot buy just pass
                        pass

                if (-diff) > threshold:
                    try:
                        print(
                            f"trying to sell at {i} = {-diff}>{threshold}, cp = {cp}, lp = {lp}, amt = {cash * threshold} ")
                        p.sell_amount(stk, cash * threshold)
                        lp = (1 - volatility) * lp + volatility * cp
                        locked_price[stk] = lp
                    except NotEnoughStocksToSellException:
                        p.square_off([stk])
                    except AmountIsZeroException:
                        pass

            t.tick()
        logging.info("Trying to square off remaining stocks")
        p.square_off(stocks=stocks)
        return p
