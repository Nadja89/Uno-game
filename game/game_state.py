import random
from game.card import Card, Color, CardType
from game.deck import Deck
from game.player import Player

class GameState:
    def __init__(self, players: list[Player], starting_hand_size: int = 7):
        if len(players) < 2:
            raise ValueError("Two players needed!")

        self.players: list[Player] = players
        self.deck: Deck = Deck()
        self.direction: int = 1  
        self.current_player_index: int = 0
        self.active_color: Color | None = None
        self.pending_draw: int = 0 
        self.finished: bool = False
        self.winner: Player | None = None

        self._deal_starting_hands(starting_hand_size)
        self._flip_starting_card()


    def _deal_starting_hands(self, hand_size: int) -> None:
        for player in self.players:
            player.add_cards(self.deck.draw(hand_size))

    def _flip_starting_card(self) -> None:
        first_card = self.deck.draw(1)[0]
        while first_card.is_wild():
            self.deck.draw_pile.insert(0, first_card)
            first_card = self.deck.draw(1)[0]

        self.deck.play(first_card)
        self.active_color = first_card.color


    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def top_card(self) -> Card:
        return self.deck.top_card()

    def legal_moves(self) -> list[Card]:
        if self.pending_draw > 0:
            return []
        return self.current_player().legal_moves(self.top_card(), self.active_color)

    def play_card(self, card: Card, chosen_color: Color | None = None) -> None:
        if self.pending_draw > 0:
            raise ValueError("Must draw pending cards before playing!")

        player = self.current_player()
        if card not in player.legal_moves(self.top_card(), self.active_color):
            raise ValueError(f"The move {card} is not legal!")
        if card.is_wild() and chosen_color is None:
            raise ValueError("Must choose color!")

        player.remove_card(card)
        self.deck.play(card)

        if card.is_wild():
            self.active_color = chosen_color
        else:
            self.active_color = card.color

        if player.has_won():
            self.finished = True
            self.winner = player
            return

        self._apply_card_effect(card)
        self._advance_turn()

    def draw_card(self) -> list[Card]:
        player = self.current_player()

        if self.pending_draw > 0:
            drawn = self.deck.draw(self.pending_draw)
            player.add_cards(drawn)
            self.pending_draw = 0
            self._advance_turn()
            return drawn

        drawn = self.deck.draw(1)
        player.add_cards(drawn)
        self._advance_turn()
        return drawn

    def _apply_card_effect(self, card: Card) -> None:
        if card.card_type == CardType.REVERSE:
            self.direction *= -1
            if len(self.players) == 2:
                self._move_index_forward()
        elif card.card_type == CardType.SKIP:
            self._move_index_forward()
        elif card.card_type == CardType.DRAW_TWO:
            self.pending_draw += 2
        elif card.card_type == CardType.WILD_DRAW_FOUR:
            self.pending_draw += 4


    def _move_index_forward(self) -> None:
        self.current_player_index = (
            self.current_player_index + self.direction
        ) % len(self.players)

    def _advance_turn(self) -> None:
        self._move_index_forward()

    def __str__(self) -> str:
        return (
            f"On the move: {self.current_player()} | "
            f"Color: {self.active_color.value} | "
            f"Card on desk: {self.top_card()} | "
            f"Direction: {'forward' if self.direction == 1 else 'back'}"
        )
    
    def clone(self) -> "GameState":
        new_state = GameState.__new__(GameState)
        new_state.players = [p.clone() for p in self.players]
        new_state.deck = self.deck.clone()
        new_state.direction = self.direction
        new_state.current_player_index = self.current_player_index
        new_state.active_color = self.active_color
        new_state.pending_draw = self.pending_draw
        new_state.finished = self.finished
        new_state.winner = None
        if self.winner is not None:
            for i, p in enumerate(self.players):
                if p is self.winner:
                    new_state.winner = new_state.players[i]
                    break
        return new_state