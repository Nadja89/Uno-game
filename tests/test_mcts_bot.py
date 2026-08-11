import random

from game.card import Card, Color, CardType
from game.deck import Deck
from game.game_state import GameState
from game.player import Player
from game.bots.mcts_bot import determinize, choose_move, get_actions


def make_bare_state(p0_hand, p1_hand, top_card):
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
    state.direction = 1
    state.current_player_index = 1
    state.active_color = top_card.color
    state.pending_draw = 0
    state.finished = False
    state.winner = None
    return state


def test_determinize_preserves_bot_own_hand():
    top = Card(Color.RED, CardType.NUMBER, 5)
    bot_hand = [Card(Color.RED, CardType.NUMBER, 9), Card(Color.BLUE, CardType.NUMBER, 2)]
    opponent_hand = [Card(Color.GREEN, CardType.NUMBER, i) for i in range(3)]

    gs = make_bare_state(p0_hand=opponent_hand, p1_hand=bot_hand, top_card=top)

    det = determinize(gs, bot_index=1)

    assert det.players[1].hand == bot_hand


def test_determinize_preserves_opponent_card_count():
    top = Card(Color.RED, CardType.NUMBER, 5)
    bot_hand = [Card(Color.RED, CardType.NUMBER, 9)]
    opponent_hand = [Card(Color.GREEN, CardType.NUMBER, i) for i in range(4)]

    gs = make_bare_state(p0_hand=opponent_hand, p1_hand=bot_hand, top_card=top)

    det = determinize(gs, bot_index=1)

    assert det.players[0].card_count() == len(opponent_hand)


def test_choose_move_returns_action_from_legal_moves():
    top = Card(Color.RED, CardType.NUMBER, 5)
    bot_hand = [Card(Color.RED, CardType.NUMBER, 9), Card(Color.BLUE, CardType.NUMBER, 2)]
    opponent_hand = [Card(Color.GREEN, CardType.NUMBER, 1)] * 3

    gs = make_bare_state(p0_hand=opponent_hand, p1_hand=bot_hand, top_card=top)

    random.seed(42)
    action = choose_move(gs, bot_index=1, num_determinizations=3, iterations=30)

    legal_actions = get_actions(gs)
    assert action in legal_actions


def test_mcts_plays_only_legal_card_when_hand_has_one_card():
    top = Card(Color.RED, CardType.NUMBER, 5)
    only_card = Card(Color.RED, CardType.NUMBER, 9)
    bot_hand = [only_card]
    opponent_hand = [Card(Color.GREEN, CardType.NUMBER, i) for i in range(5)]

    gs = make_bare_state(p0_hand=opponent_hand, p1_hand=bot_hand, top_card=top)

    random.seed(1)
    action = choose_move(gs, bot_index=1, num_determinizations=3, iterations=30)

    assert action == ("play", only_card, None)


def test_mcts_statistically_prefers_attacking_card_when_opponent_is_close_to_winning():
    top = Card(Color.RED, CardType.NUMBER, 5)
    draw_two = Card(Color.RED, CardType.DRAW_TWO)
    neutral_card = Card(Color.RED, CardType.NUMBER, 3)
    bot_hand = [draw_two, neutral_card]
    opponent_hand = [Card(Color.RED, CardType.NUMBER, 3)]

    gs = make_bare_state(p0_hand=opponent_hand, p1_hand=bot_hand, top_card=top)

    correct_choices = 0
    trials = 10
    for seed in range(trials):
        random.seed(seed)
        action = choose_move(gs, bot_index=1, num_determinizations=5, iterations=100)
        if action == ("play", draw_two, None):
            correct_choices += 1

    assert correct_choices >= trials * 0.6