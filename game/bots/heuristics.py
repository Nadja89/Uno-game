import random

from config import HeuristicConfig
from game.card import CardType, Color
from game.game_state import GameState

DEFAULT_HEURISTIC = HeuristicConfig()


def _color_counts(hand) -> dict:
    counts = {Color.RED: 0, Color.YELLOW: 0, Color.GREEN: 0, Color.BLUE: 0}
    for card in hand:
        if not card.is_wild():
            counts[card.color] += 1
    return counts


def best_wild_color(hand) -> Color:
    counts = _color_counts(hand)
    return max(counts, key=counts.get)


def score_action(state: GameState, action: tuple,
                 cfg: HeuristicConfig = DEFAULT_HEURISTIC) -> float:
    if action[0] == "draw":
        return cfg.draw_penalty

    _, card, chosen_color = action
    player = state.current_player()
    opponent_min_cards = min(
        p.card_count() for p in state.players if p is not player
    )
    pressure = max(0, cfg.pressure_threshold - opponent_min_cards)

    score = 0.0

    if player.card_count() == 1:
        score += cfg.last_card_bonus

    if card.card_type in (CardType.SKIP, CardType.DRAW_TWO, CardType.REVERSE):
        score += cfg.action_card_bonus + pressure
    elif card.card_type == CardType.WILD_DRAW_FOUR:
        score += cfg.wild_draw_four_bonus + pressure

    if card.is_wild():
        score -= cfg.wild_penalty
        remaining_hand = [c for c in player.hand if c != card]
        if remaining_hand and chosen_color == best_wild_color(remaining_hand):
            score += cfg.good_color_bonus

    if not card.is_wild():
        counts = _color_counts(player.hand)
        score += cfg.same_color_weight * counts.get(card.color, 0)

    return score


def heuristic_pick(state: GameState, actions: list[tuple],
                   cfg: HeuristicConfig = DEFAULT_HEURISTIC) -> tuple:
    if len(actions) == 1:
        return actions[0]

    if random.random() < cfg.epsilon:
        return random.choice(actions)

    return max(actions, key=lambda a: score_action(state, a, cfg))


def random_pick(state: GameState, actions: list[tuple]) -> tuple:
    return random.choice(actions)
