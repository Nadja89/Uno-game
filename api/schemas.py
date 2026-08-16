from pydantic import BaseModel


class CardOut(BaseModel):
    color: str
    card_type: str
    value: int | None = None


class CardIn(BaseModel):
    color: str
    card_type: str
    value: int | None = None


class PlayCardRequest(BaseModel):
    card: CardIn
    chosen_color: str | None = None  # obavezno samo za wild karte


class GameStateOut(BaseModel):
    game_id: str
    current_player_index: int
    direction: int
    active_color: str
    top_card: CardOut
    pending_draw: int
    finished: bool
    winner: str | None = None
    your_hand: list[CardOut]
    opponent_card_count: int
    bot_action: str | None = None