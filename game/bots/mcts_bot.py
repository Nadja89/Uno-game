import math
import random

from game.card import Color
from game.game_state import GameState
from game.bots.heuristics import heuristic_pick

ALL_COLORS = [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]


def determinize(state: GameState, bot_index: int) -> GameState:
    clone = state.clone()
    bot = clone.players[bot_index]

    unseen: list = list(clone.deck.draw_pile)
    for i, player in enumerate(clone.players):
        if i != bot_index:
            unseen.extend(player.hand)

    random.shuffle(unseen)

    idx = 0
    for i, player in enumerate(clone.players):
        if i != bot_index:
            n = len(player.hand)
            player.hand = unseen[idx: idx + n]
            idx += n

    clone.deck.draw_pile = unseen[idx:]
    return clone


def get_actions(state: GameState) -> list[tuple]:
    if state.finished:
        return []

    legal = state.legal_moves()
    if not legal:
        return [("draw",)]

    actions = []
    for card in legal:
        if card.is_wild():
            for color in ALL_COLORS:
                actions.append(("play", card, color))
        else:
            actions.append(("play", card, None))
    return actions


def apply_action(state: GameState, action: tuple) -> None:
    if action[0] == "draw":
        state.draw_card()
    else:
        _, card, color = action
        state.play_card(card, color)


class MCTSNode:
    def __init__(self, state: GameState, parent: "MCTSNode | None" = None,
                 player_who_moved: int | None = None):
        self.state = state
        self.parent = parent
        self.player_who_moved = player_who_moved  
        self.children: list[tuple[tuple, "MCTSNode"]] = []
        self.visits = 0
        self.wins = 0.0
        self.untried_actions = get_actions(state)

    def is_fully_expanded(self) -> bool:
        return not self.untried_actions

    def is_terminal(self) -> bool:
        return self.state.finished


def ucb1_select(node: MCTSNode, c: float = 1.4) -> tuple[tuple, MCTSNode]:
    best_score = -1.0
    best_pair = None
    for action, child in node.children:
        exploit = child.wins / child.visits
        explore = c * math.sqrt(math.log(node.visits) / child.visits)
        score = exploit + explore
        if score > best_score:
            best_score = score
            best_pair = (action, child)
    return best_pair


def expand(node: MCTSNode) -> MCTSNode:
    action = node.untried_actions.pop()
    mover = node.state.current_player_index
    child_state = node.state.clone()
    apply_action(child_state, action)
    child = MCTSNode(child_state, parent=node, player_who_moved=mover)
    node.children.append((action, child))
    return child


def rollout(state: GameState, max_turns: int = 300) -> int | None:
    sim_state = state.clone()
    turns = 0
    while not sim_state.finished and turns < max_turns:
        actions = get_actions(sim_state)
        action = heuristic_pick(sim_state, actions)
        apply_action(sim_state, action)
        turns += 1

    if not sim_state.finished:
        return None

    for i, player in enumerate(sim_state.players):
        if player is sim_state.winner:
            return i
    return None


def backpropagate(node: MCTSNode, winner_index: int | None) -> None:
    while node is not None:
        node.visits += 1
        if node.player_who_moved is not None:
            if winner_index is None:
                node.wins += 0.5  
            elif node.player_who_moved == winner_index:
                node.wins += 1.0
        node = node.parent


def mcts_search(root_state: GameState, iterations: int = 100, c: float = 1.4) -> MCTSNode:
    root = MCTSNode(root_state.clone())

    for _ in range(iterations):
        node = root

        while node.is_fully_expanded() and node.children and not node.is_terminal():
            _, node = ucb1_select(node, c)

        if not node.is_terminal() and not node.is_fully_expanded():
            node = expand(node)

        winner_index = rollout(node.state)
        backpropagate(node, winner_index)

    return root


def choose_move(state: GameState, bot_index: int,
                 num_determinizations: int = 10, iterations: int = 100) -> tuple:
    action_visits: dict[tuple, int] = {}

    for _ in range(num_determinizations):
        det_state = determinize(state, bot_index)
        root = mcts_search(det_state, iterations=iterations)
        for action, child in root.children:
            action_visits[action] = action_visits.get(action, 0) + child.visits

    if not action_visits:
        return ("draw",)

    best_action = max(action_visits, key=action_visits.get)
    return best_action


def bot_take_turn(state: GameState, bot_index: int,
                   num_determinizations: int = 10, iterations: int = 100) -> tuple:
    action = choose_move(state, bot_index, num_determinizations, iterations)
    apply_action(state, action)
    return action