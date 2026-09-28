from .demo import DemoAdapter
from .unavailable import UnavailableAdapter


class LowesDemoAdapter(DemoAdapter):
    def __init__(self):
        super().__init__("lowes")


class LowesAdapter(UnavailableAdapter):
    def __init__(self):
        super().__init__("lowes")
