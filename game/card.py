from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Color(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    WILD = "wild"  

class CardType(Enum):
    NUMBER = "number"
    SKIP = "skip"
    REVERSE = "reverse"
    DRAW_TWO = "draw_two"
    WILD = "wild"
    WILD_DRAW_FOUR = "wild_draw_four"

@dataclass(frozen=True)
class Card:
    color: Color
    card_type: CardType
    value: Optional[int] = None

    def is_wild(self) -> bool:
        return self.card_type in (CardType.WILD, CardType.WILD_DRAW_FOUR)

    def matches(self, top_card: "Card", active_color: Optional[Color] = None) -> bool:
        if self.is_wild():
            return True

        compare_color = active_color if active_color is not None else top_card.color

        if self.color == compare_color:
            return True

        if self.card_type == CardType.NUMBER and top_card.card_type == CardType.NUMBER:
            return self.value == top_card.value

        if self.card_type == top_card.card_type and self.card_type in (
            CardType.SKIP,
            CardType.REVERSE,
            CardType.DRAW_TWO,
        ):
            return True

        return False

    def __str__(self) -> str:
        if self.card_type == CardType.NUMBER:
            label = str(self.value)
        else:
            label = self.card_type.value
        return f"{self.color.value}_{label}"

    def __repr__(self) -> str:
        return f"Card({self.color.name}, {self.card_type.name}, value={self.value})"