from typing import Optional, TypedDict, Union

class BaseCounter(TypedDict):
    _id: int
    name: str
    correct: int
    wrong: int
    streak: Union[int, str]
    high: Union[int, str]

class OGCounter(BaseCounter, total=False):
    current_saves: float
    total_saves: int
    daily: int
    counter: bool
    reminder: bool
    dm: bool

class ClassicCounter(BaseCounter, total=False):
    """Same as BaseCounter"""

class BetaCounter(BaseCounter, total=False):
    current_saves: int
    total_saves: int
    counter: bool

class YodaCounter(BaseCounter, total=False):
    tokens: float

class NumselliCounter(BaseCounter, total=False):
    current_saves: float
    total_saves: int
    counter: bool