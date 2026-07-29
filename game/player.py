from dataclasses import dataclass, field
from game.card import Card, Color

@dataclass
class Player:
    name: str
    is_bot: bool = False
    hand: list[Card] = field(default_factory=list)
    called_uno: bool = False

    def has_won(self) -> bool:
        return len(self.hand) == 0

    def add_cards(self, cards: list[Card]) -> None:
        self.hand.extend(cards)

    def remove_card(self, card: Card) -> None:
        self.hand.remove(card)
        if len(self.hand) != 1:
            self.called_uno = False

    def legal_moves(self, top_card: Card, active_color: Color | None = None) -> list[Card]:
        return [card for card in self.hand if card.matches(top_card, active_color)]

    def card_count(self) -> int:
        return len(self.hand)

    def __str__(self) -> str:
        role = "bot" if self.is_bot else "player"
        return f"{self.name} ({role}, {self.card_count()} cards)"