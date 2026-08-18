from game.card import Card, Color, CardType
from game.deck import Deck
from game.game_state import GameState
from game.player import Player


def card_to_dict(card: Card) -> dict:
    return {
        "color": card.color.value,
        "card_type": card.card_type.value,
        "value": card.value,
    }


def card_from_dict(d: dict) -> Card:
    return Card(Color(d["color"]), CardType(d["card_type"]), d["value"])


def player_to_dict(player: Player) -> dict:
    return {
        "name": player.name,
        "is_bot": player.is_bot,
        "hand": [card_to_dict(c) for c in player.hand],
        "called_uno": player.called_uno,
    }


def player_from_dict(d: dict) -> Player:
    player = Player(name=d["name"], is_bot=d["is_bot"], called_uno=d.get("called_uno", False))
    player.hand = [card_from_dict(c) for c in d["hand"]]
    return player


def game_state_to_dict(state: GameState) -> dict:
    winner_index = None
    if state.winner is not None:
        for i, p in enumerate(state.players):
            if p is state.winner:
                winner_index = i
                break

    return {
        "players": [player_to_dict(p) for p in state.players],
        "draw_pile": [card_to_dict(c) for c in state.deck.draw_pile],
        "discard_pile": [card_to_dict(c) for c in state.deck.discard_pile],
        "direction": state.direction,
        "current_player_index": state.current_player_index,
        "active_color": state.active_color.value if state.active_color else None,
        "pending_draw": state.pending_draw,
        "finished": state.finished,
        "winner_index": winner_index,
    }


def game_state_from_dict(d: dict) -> GameState:
    state = GameState.__new__(GameState)
    state.players = [player_from_dict(pd) for pd in d["players"]]

    deck = Deck.__new__(Deck)
    deck.draw_pile = [card_from_dict(c) for c in d["draw_pile"]]
    deck.discard_pile = [card_from_dict(c) for c in d["discard_pile"]]
    state.deck = deck

    state.direction = d["direction"]
    state.current_player_index = d["current_player_index"]
    state.active_color = Color(d["active_color"]) if d["active_color"] else None
    state.pending_draw = d["pending_draw"]
    state.finished = d["finished"]
    state.winner = (
        state.players[d["winner_index"]] if d["winner_index"] is not None else None
    )
    return state