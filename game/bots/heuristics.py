import random

from game.card import CardType, Color
from game.game_state import GameState


def _color_counts(hand) -> dict:
    counts = {Color.RED: 0, Color.YELLOW: 0, Color.GREEN: 0, Color.BLUE: 0}
    for card in hand:
        if not card.is_wild():
            counts[card.color] += 1
    return counts


def best_wild_color(hand) -> Color:
    counts = _color_counts(hand)
    return max(counts, key=counts.get)


def score_action(state: GameState, action: tuple) -> float:
    if action[0] == "draw":
        return -100.0

    _, card, chosen_color = action
    player = state.current_player()
    opponent_min_cards = min(
        p.card_count() for i, p in enumerate(state.players) if p is not player
    )

    score = 0.0

    if player.card_count() == 1:
        score += 1000.0

    if card.card_type in (CardType.SKIP, CardType.DRAW_TWO):
        score += 5.0 + max(0, 6 - opponent_min_cards)
    elif card.card_type == CardType.WILD_DRAW_FOUR:
        score += 6.0 + max(0, 6 - opponent_min_cards)
    elif card.card_type == CardType.REVERSE:
        score += 3.0

    if card.is_wild():
        score -= 2.0
        remaining_hand = [c for c in player.hand if c != card]
        if remaining_hand and chosen_color == best_wild_color(remaining_hand):
            score += 1.5

    if not card.is_wild():
        counts = _color_counts(player.hand)
        score += 0.5 * counts.get(card.color, 0)

    return score


def heuristic_pick(state: GameState, actions: list[tuple], epsilon: float = 0.25) -> tuple:
    if len(actions) == 1:
        return actions[0]

    if random.random() < epsilon:
        return random.choice(actions)

    return max(actions, key=lambda a: score_action(state, a))