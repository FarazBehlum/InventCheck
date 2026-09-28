from .demo import DemoAdapter
from .unavailable import UnavailableAdapter


class WalmartDemoAdapter(DemoAdapter):
    def __init__(self):
        super().__init__("walmart")


class WalmartAdapter(UnavailableAdapter):
    def __init__(self):
        super().__init__("walmart")
