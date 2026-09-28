from .demo import DemoAdapter
from .unavailable import UnavailableAdapter


class BestBuyDemoAdapter(DemoAdapter):
    def __init__(self):
        super().__init__("bestbuy")


class BestBuyAdapter(UnavailableAdapter):
    def __init__(self):
        super().__init__("bestbuy")
