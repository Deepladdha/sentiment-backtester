from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from enum import Enum

class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass(frozen=True)
class Transaction:
    ticker : str
    quantity : int
    price : Decimal
    timestamp : datetime
    action : Action

    def __post_init__(self):
        if not isinstance(self.action, Action):
            raise TypeError(f"action must be an Action enum member, got {type(self.action)}")
   