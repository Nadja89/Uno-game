import random
from game.card import Card, Color, CardType

class Deck:

    def __init__(self):
        self.draw_pile: list[Card] = self._build_full_deck()
        self.discard_pile: list[Card] = []
        random.shuffle(self.draw_pile)

    def _build_full_deck(self) -> list[Card]:
        cards: list[Card] = []
        colors = [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]

        for color in colors:
            cards.append(Card(color, CardType.NUMBER, 0))
            for value in range(1, 10):
                cards.append(Card(color, CardType.NUMBER, value))
                cards.append(Card(color, CardType.NUMBER, value))
            for card_type in (CardType.SKIP, CardType.REVERSE, CardType.DRAW_TWO):
                cards.append(Card(color, card_type))
                cards.append(Card(color, card_type))

        for _ in range(4):
            cards.append(Card(Color.WILD, CardType.WILD))
            cards.append(Card(Color.WILD, CardType.WILD_DRAW_FOUR))

        return cards

    def draw(self, n: int = 1) -> list[Card]:
        drawn: list[Card] = []
        for _ in range(n):
            if not self.draw_pile:
                self._reshuffle_discard_into_draw()
            drawn.append(self.draw_pile.pop())
        return drawn

    def _reshuffle_discard_into_draw(self) -> None:
        if len(self.discard_pile) <= 1:
            raise RuntimeError("Error!")

        top_card = self.discard_pile.pop()
        self.draw_pile = self.discard_pile
        random.shuffle(self.draw_pile)
        self.discard_pile = [top_card]

    def play(self, card: Card) -> None:
        self.discard_pile.append(card)

    def top_card(self) -> Card:
        if not self.discard_pile:
            raise RuntimeError("Error!")
        return self.discard_pile[-1]

    def cards_remaining(self) -> int:
        return len(self.draw_pile)
    
def clone(self) -> "Deck":
    new_deck = Deck.__new__(Deck)
    new_deck.draw_pile = list(self.draw_pile)
    new_deck.discard_pile = list(self.discard_pile)
    return new_deck