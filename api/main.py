

import uuid

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import get_cors_origins, load_game_config, load_mcts_config
from game.belief import BeliefState
from game.card import Card, CardType, Color
from game.game_state import GameState
from game.bots.mcts_bot import play_bot_turns
from game.player import Player
from game.serialization import game_data_from_dict, game_data_to_dict

from api.schemas import (
    CardOut,
    GameStateOut,
    LoginRequest,
    PlayCardRequest,
    RegisterRequest,
    TokenResponse,
)
from api.security import create_access_token, decode_access_token, hash_password, verify_password
from db.database import Base, engine, get_db
from db.models import GameModel, UserModel

Base.metadata.create_all(bind=engine)

app = FastAPI(title="UNO Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

GAME = load_game_config()
MCTS = load_mcts_config()
HUMAN_INDEX = GAME.human_index
BOT_INDEX = GAME.bot_index

bearer_scheme = HTTPBearer(auto_error=False)  


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authorization token.")

    token = credentials.credentials

    try:
        user_id = uuid.UUID(decode_access_token(token))
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User does not exist.")

    return user


def serialize_state(game_id: str, state: GameState, bot_actions: list[str] | None = None) -> GameStateOut:
    top = state.top_card()
    human = state.players[HUMAN_INDEX]
    bot = state.players[BOT_INDEX]
    playable = [] if state.finished or state.current_player_index != HUMAN_INDEX else state.legal_moves()

    return GameStateOut(
        game_id=game_id,
        current_player_index=state.current_player_index,
        direction=state.direction,
        active_color=state.active_color.value,
        top_card=CardOut(color=top.color.value, card_type=top.card_type.value, value=top.value),
        pending_draw=state.pending_draw,
        finished=state.finished,
        winner=state.winner.name if state.winner else None,
        you_won=state.winner is human,
        your_hand=[
            CardOut(color=c.color.value, card_type=c.card_type.value, value=c.value)
            for c in human.hand
        ],
        playable_cards=[
            CardOut(color=c.color.value, card_type=c.card_type.value, value=c.value)
            for c in playable
        ],
        opponent_card_count=bot.card_count(),
        bot_action=" ".join(bot_actions) if bot_actions else None,
        bot_actions=bot_actions or [],
    )


def load_owned_game(game_id: str, user: UserModel, db: Session) -> GameModel:
    try:
        game_uuid = uuid.UUID(game_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Game not found.")
    row = db.query(GameModel).filter(GameModel.id == game_uuid).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Game not found.")
    if row.user_id is not None and str(row.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="This game does not belong to you.")
    return row


CHOOSABLE_COLORS = {"red", "yellow", "green", "blue"}


def find_card_in_hand(hand: list[Card], color: str, card_type: str, value: int | None) -> Card:
    try:
        wanted_color, wanted_type = Color(color), CardType(card_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unknown card color or type.")
    for card in hand:
        if card.color == wanted_color and card.card_type == wanted_type and card.value == value:
            return card
    raise HTTPException(status_code=400, detail="Card not found in the player's hand.")


def _card_name(card: Card) -> str:
    if card.card_type == CardType.WILD_DRAW_FOUR:
        return "wild draw four"
    if card.card_type == CardType.WILD:
        return "wild"
    return str(card).replace("_", " ")


def _describe_action(action: tuple) -> str:
    if action[0] == "draw":
        return "Bot drew a card."
    _, card, color = action
    chosen = f" and chose {color.value}" if color else ""
    return f"Bot played {_card_name(card)}{chosen}."


def run_bot(state: GameState, belief: BeliefState) -> list[str]:
    actions = play_bot_turns(state, BOT_INDEX, excluded_colors=belief.excluded_colors, cfg=MCTS)
    return [_describe_action(a) for a in actions]


@app.get("/")
def health_check():
    return {"status": "ok", "message": "UNO Game API is running."}


@app.post("/auth/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.username == request.username).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Username is already taken.")

    user = UserModel(
        id=uuid.uuid4(),
        username=request.username,
        hashed_password=hash_password(request.password),
    )
    db.add(user)
    db.commit()

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == request.username).first()
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)

@app.post("/game/new", response_model=GameStateOut)
def new_game(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    human = Player(name=GAME.human_name)
    bot = Player(name=GAME.bot_name, is_bot=True)
    state = GameState([human, bot], starting_hand_size=GAME.starting_hand_size)
    belief = BeliefState()

    game_id = uuid.uuid4()
    row = GameModel(
        id=game_id,
        user_id=user.id,
        state=game_data_to_dict(state, belief),
        finished=state.finished,
    )
    db.add(row)
    db.commit()

    return serialize_state(str(game_id), state)


@app.get("/game/active", response_model=GameStateOut)
def get_active_game(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    row = (
        db.query(GameModel)
        .filter(GameModel.user_id == user.id, GameModel.finished == False)
        .order_by(GameModel.updated_at.desc())
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="You have no active game.")

    state, _ = game_data_from_dict(row.state)
    return serialize_state(str(row.id), state)


@app.get("/game/{game_id}", response_model=GameStateOut)
def get_game(game_id: str, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    row = load_owned_game(game_id, user, db)
    state, _ = game_data_from_dict(row.state)
    return serialize_state(game_id, state)


@app.post("/game/{game_id}/play", response_model=GameStateOut)
def play_card(
    game_id: str,
    request: PlayCardRequest,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    row = load_owned_game(game_id, user, db)
    state, belief = game_data_from_dict(row.state)

    if state.finished:
        raise HTTPException(status_code=400, detail="The game is already finished.")

    if state.current_player_index != HUMAN_INDEX:
        raise HTTPException(status_code=400, detail="It is not your turn.")

    human = state.players[HUMAN_INDEX]
    card = find_card_in_hand(
        human.hand, request.card.color, request.card.card_type, request.card.value
    )
    if request.chosen_color is not None and request.chosen_color not in CHOOSABLE_COLORS:
        raise HTTPException(
            status_code=400, detail="Color must be red, yellow, green or blue."
        )
    chosen_color = Color(request.chosen_color) if request.chosen_color else None

    try:
        state.play_card(card, chosen_color)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    bot_lines = run_bot(state, belief)

    row.state = game_data_to_dict(state, belief)
    row.finished = state.finished
    db.commit()

    return serialize_state(game_id, state, bot_actions=bot_lines)


@app.post("/game/{game_id}/draw", response_model=GameStateOut)
def draw_card(
    game_id: str, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)
):
    row = load_owned_game(game_id, user, db)
    state, belief = game_data_from_dict(row.state)

    if state.finished:
        raise HTTPException(status_code=400, detail="The game is already finished.")

    if state.current_player_index != HUMAN_INDEX:
        raise HTTPException(status_code=400, detail="It is not your turn.")

    belief.observe_before_draw(state, HUMAN_INDEX)
    state.draw_card()
    belief.reset_player(HUMAN_INDEX)

    bot_lines = run_bot(state, belief)

    row.state = game_data_to_dict(state, belief)
    row.finished = state.finished
    db.commit()

    return serialize_state(game_id, state, bot_actions=bot_lines)
