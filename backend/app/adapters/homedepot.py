from .demo import DemoAdapter
from .unavailable import UnavailableAdapter


class HomeDepotDemoAdapter(DemoAdapter):
    def __init__(self):
        super().__init__("homedepot")


class HomeDepotAdapter(UnavailableAdapter):
    def __init__(self):
        super().__init__("homedepot")
