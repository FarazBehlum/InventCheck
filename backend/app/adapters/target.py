from .demo import DemoAdapter
from .unavailable import UnavailableAdapter


class TargetDemoAdapter(DemoAdapter):
    def __init__(self):
        super().__init__("target")


class TargetAdapter(UnavailableAdapter):
    def __init__(self):
        super().__init__("target")
