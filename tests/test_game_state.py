import pytest

from game.card import Card, Color, CardType
from game.deck import Deck
from game.game_state import GameState
from game.player import Player


def make_bare_state(p0_hand, p1_hand, top_card, active_color=None, direction=1,
                     current_player_index=0, pending_draw=0):
    p0 = Player(name="P0")
    p1 = Player(name="P1")
    p0.hand = list(p0_hand)
    p1.hand = list(p1_hand)

    state = GameState.__new__(GameState)
    state.players = [p0, p1]
    state.deck = Deck()
    used = set(p0_hand) | set(p1_hand) | {top_card}
    state.deck.draw_pile = [c for c in state.deck.draw_pile if c not in used]
    state.deck.discard_pile = [top_card]
    state.direction = direction
    state.current_player_index = current_player_index
    state.active_color = active_color if active_color is not None else top_card.color
    state.pending_draw = pending_draw
    state.finished = False
    state.winner = None
    return state


def test_game_starts_with_correct_hand_size():
    p0 = Player(name="A")
    p1 = Player(name="B")
    gs = GameState([p0, p1])
    assert p0.card_count() == 7
    assert p1.card_count() == 7
    assert gs.deck.cards_remaining() == 108 - 14 - 1


def test_illegal_move_raises_error():
    top = Card(Color.RED, CardType.NUMBER, 5)
    wrong_card = Card(Color.BLUE, CardType.NUMBER, 2)
    gs = make_bare_state(p0_hand=[wrong_card], p1_hand=[], top_card=top)
    with pytest.raises(ValueError):
        gs.play_card(wrong_card)


def test_wild_requires_chosen_color():
    top = Card(Color.RED, CardType.NUMBER, 5)
    wild = Card(Color.WILD, CardType.WILD)
    gs = make_bare_state(p0_hand=[wild], p1_hand=[Card(Color.BLUE, CardType.NUMBER, 1)], top_card=top)
    with pytest.raises(ValueError):
        gs.play_card(wild)


def test_playing_last_card_wins_game():
    top = Card(Color.RED, CardType.NUMBER, 5)
    last_card = Card(Color.RED, CardType.NUMBER, 9)
    gs = make_bare_state(
        p0_hand=[last_card],
        p1_hand=[Card(Color.BLUE, CardType.NUMBER, 1)],
        top_card=top,
    )
    gs.play_card(last_card)
    assert gs.finished is True
    assert gs.winner.name == "P0"


def test_draw_two_forces_next_player_to_draw():
    top = Card(Color.RED, CardType.NUMBER, 5)
    draw_two = Card(Color.RED, CardType.DRAW_TWO)
    gs = make_bare_state(
        p0_hand=[draw_two, Card(Color.GREEN, CardType.NUMBER, 7)],
        p1_hand=[Card(Color.BLUE, CardType.NUMBER, 1)],
        top_card=top,
    )
    gs.play_card(draw_two)
    assert gs.pending_draw == 2

    hand_before = gs.players[1].card_count()
    gs.draw_card()
    assert gs.players[1].card_count() == hand_before + 2
    assert gs.pending_draw == 0


def test_reverse_changes_direction():
    top = Card(Color.RED, CardType.NUMBER, 5)
    reverse = Card(Color.RED, CardType.REVERSE)
    gs = make_bare_state(
        p0_hand=[reverse, Card(Color.GREEN, CardType.NUMBER, 7)],
        p1_hand=[Card(Color.BLUE, CardType.NUMBER, 1)],
        top_card=top,
        direction=1,
    )
    gs.play_card(reverse)
    assert gs.direction == -1


def test_skip_gives_effectively_extra_turn_in_two_player_game():
    top = Card(Color.RED, CardType.NUMBER, 5)
    skip = Card(Color.RED, CardType.SKIP)
    gs = make_bare_state(
        p0_hand=[skip, Card(Color.GREEN, CardType.NUMBER, 7)],
        p1_hand=[Card(Color.BLUE, CardType.NUMBER, 1)],
        top_card=top,
        current_player_index=0,
    )
    gs.play_card(skip)
    assert gs.current_player_index == 0


def test_active_color_updates_after_wild():
    top = Card(Color.RED, CardType.NUMBER, 5)
    wild = Card(Color.WILD, CardType.WILD)
    gs = make_bare_state(
        p0_hand=[wild],
        p1_hand=[Card(Color.BLUE, CardType.NUMBER, 1)],
        top_card=top,
    )
    gs.play_card(wild, chosen_color=Color.GREEN)
    assert gs.active_color == Color.GREEN


def test_clone_does_not_affect_original_state():
    top = Card(Color.RED, CardType.NUMBER, 5)
    card = Card(Color.RED, CardType.NUMBER, 9)
    gs = make_bare_state(
        p0_hand=[card, Card(Color.RED, CardType.NUMBER, 3)],
        p1_hand=[Card(Color.BLUE, CardType.NUMBER, 1)],
        top_card=top,
    )
    clone = gs.clone()
    clone.play_card(card)

    assert gs.players[0].card_count() == 2
    assert clone.players[0].card_count() == 1