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
    chosen_color: str | None = None  


class GameStateOut(BaseModel):
    game_id: str
    current_player_index: int
    direction: int
    active_color: str
    top_card: CardOut
    pending_draw: int
    finished: bool
    winner: str | None = None
    you_won: bool = False
    your_hand: list[CardOut]
    playable_cards: list[CardOut] = []
    opponent_card_count: int
    bot_action: str | None = None
    bot_actions: list[str] = []

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"