from game.card import Color
from game.game_state import GameState


class BeliefState:

    def __init__(self):
        self.excluded_colors: dict[int, set[Color]] = {}

    def observe_before_draw(self, state: GameState, player_index: int) -> None:
        if state.pending_draw > 0:
            return

        if state.legal_moves():
            return

        self.excluded_colors.setdefault(player_index, set()).add(state.active_color)

    def reset_player(self, player_index: int) -> None:
        self.excluded_colors.pop(player_index, None)

    def to_dict(self) -> dict:
        return {
            str(i): [c.value for c in colors]
            for i, colors in self.excluded_colors.items()
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BeliefState":
        belief = cls()
        for i_str, color_values in d.items():
            belief.excluded_colors[int(i_str)] = {Color(v) for v in color_values}
        return belief
