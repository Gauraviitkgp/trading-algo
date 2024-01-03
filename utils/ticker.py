class Ticker:

    def __init__(self, initial_tick: int = 0):
        self.__tick__: int = initial_tick

    def tick(self):
        self.__tick__ += 1

    @property
    def value(self):
        return self.__tick__

    def reset(self):
        self.__tick__ = 0


t: Ticker = Ticker()


def get_ticker() -> Ticker:
    return t
