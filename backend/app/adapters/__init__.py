from .bestbuy import BestBuyAdapter, BestBuyDemoAdapter
from .homedepot import HomeDepotAdapter, HomeDepotDemoAdapter
from .lowes import LowesAdapter, LowesDemoAdapter
from .target import TargetAdapter, TargetDemoAdapter
from .walmart import WalmartAdapter, WalmartDemoAdapter


def adapters(demo_mode):
    classes = (
        [
            WalmartDemoAdapter,
            TargetDemoAdapter,
            HomeDepotDemoAdapter,
            LowesDemoAdapter,
            BestBuyDemoAdapter,
        ]
        if demo_mode
        else [WalmartAdapter, TargetAdapter, HomeDepotAdapter, LowesAdapter, BestBuyAdapter]
    )
    return {adapter.id: adapter for cls in classes if (adapter := cls())}
