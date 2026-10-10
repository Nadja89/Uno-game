

import os
from dataclasses import dataclass, field, replace

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default, cast=str):
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    if cast is bool:
        return raw.strip().lower() in ("1", "true", "yes", "da")
    return cast(raw)


@dataclass(frozen=True)
class HeuristicConfig:
    epsilon: float = 0.25
    draw_penalty: float = -100.0
    last_card_bonus: float = 1000.0
    action_card_bonus: float = 5.0
    wild_draw_four_bonus: float = 6.0
    pressure_threshold: int = 6
    wild_penalty: float = 2.0
    good_color_bonus: float = 1.5
    same_color_weight: float = 0.5


@dataclass(frozen=True)
class MCTSConfig:
    iterations: int = 100
    determinizations: int = 10
    exploration_c: float = 1.4
    rollout_max_turns: int = 300
    rollout_policy: str = "heuristic"
    use_belief: bool = True
    heuristic: HeuristicConfig = field(default_factory=HeuristicConfig)

    def with_(self, **changes) -> "MCTSConfig":
        return replace(self, **changes)


@dataclass(frozen=True)
class GameConfig:
    starting_hand_size: int = 7
    human_index: int = 0
    bot_index: int = 1
    human_name: str = "You"
    bot_name: str = "Bot"


@dataclass(frozen=True)
class SecurityConfig:
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 60 * 24


def load_mcts_config() -> MCTSConfig:
    base = MCTSConfig()
    return base.with_(
        iterations=_env("UNO_MCTS_ITERATIONS", base.iterations, int),
        determinizations=_env("UNO_MCTS_DETERMINIZATIONS", base.determinizations, int),
        exploration_c=_env("UNO_MCTS_C", base.exploration_c, float),
        rollout_max_turns=_env("UNO_MCTS_ROLLOUT_MAX_TURNS", base.rollout_max_turns, int),
        rollout_policy=_env("UNO_MCTS_ROLLOUT_POLICY", base.rollout_policy, str),
        use_belief=_env("UNO_MCTS_USE_BELIEF", base.use_belief, bool),
    )


def load_game_config() -> GameConfig:
    base = GameConfig()
    return replace(
        base,
        starting_hand_size=_env("UNO_HAND_SIZE", base.starting_hand_size, int),
    )


def load_security_config() -> SecurityConfig:
    base = SecurityConfig()
    return replace(
        base,
        token_expire_minutes=_env("JWT_EXPIRE_MINUTES", base.token_expire_minutes, int),
    )


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is not set. "
            f"See .env.example and create your own .env file."
        )
    return value


def get_cors_origins() -> list[str]:
    raw = _env("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    return [o.strip() for o in raw.split(",") if o.strip()]


DEFAULT_MCTS = MCTSConfig()
DEFAULT_GAME = GameConfig()
