import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from game.card import Card, CardType, Color
from game.game_state import GameState
from game.player import Player
from game.serialization import game_state_from_dict, game_state_to_dict

from api.schemas import GameStateOut, PlayCardRequest, CardOut
from db.database import Base, engine, get_db
from db.models import GameModel

Base.metadata.create_all(bind=engine)

app = FastAPI(title="UNO Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HUMAN_INDEX = 0
BOT_INDEX = 1

MCTS_NUM_DETERMINIZATIONS = 10
MCTS_ITERATIONS = 100


def serialize_state(game_id: str, state: GameState, bot_action: str | None = None) -> GameStateOut:
    top = state.top_card()
    human = state.players[HUMAN_INDEX]
    bot = state.players[BOT_INDEX]

    return GameStateOut(
        game_id=game_id,
        current_player_index=state.current_player_index,
        direction=state.direction,
        active_color=state.active_color.value,
        top_card=CardOut(color=top.color.value, card_type=top.card_type.value, value=top.value),
        pending_draw=state.pending_draw,
        finished=state.finished,
        winner=state.winner.name if state.winner else None,
        your_hand=[
            CardOut(color=c.color.value, card_type=c.card_type.value, value=c.value)
            for c in human.hand
        ],
        opponent_card_count=bot.card_count(),
        bot_action=bot_action,
    )


def load_game(game_id: str, db: Session) -> GameModel:
    row = db.query(GameModel).filter(GameModel.id == game_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Not found")
    return row


def find_card_in_hand(hand: list[Card], color: str, card_type: str, value: int | None) -> Card:
    for card in hand:
        if card.color == Color(color) and card.card_type == CardType(card_type) and card.value == value:
            return card
    raise HTTPException(status_code=400, detail="Card is not found in hand")


def _describe_action(action: tuple) -> str:
    if action[0] == "draw":
        return "Bot draws a card"
    _, card, color = action
    extra = f" (color: {color.value})" if color else ""
    return f"Bot: {card}{extra}"


@app.get("/")
def health_check():
    return {"status": "ok", "message": "UNO Game API starts"}


@app.post("/game/new", response_model=GameStateOut)
def new_game(db: Session = Depends(get_db)):
    human = Player(name="You")
    bot = Player(name="Bot", is_bot=True)
    state = GameState([human, bot])

    game_id = uuid.uuid4()
    row = GameModel(id=game_id, state=game_state_to_dict(state), finished=state.finished)
    db.add(row)
    db.commit()

    return serialize_state(str(game_id), state)


@app.get("/game/{game_id}", response_model=GameStateOut)
def get_game(game_id: str, db: Session = Depends(get_db)):
    row = load_game(game_id, db)
    state = game_state_from_dict(row.state)
    return serialize_state(game_id, state)


@app.post("/game/{game_id}/play", response_model=GameStateOut)
def play_card(game_id: str, request: PlayCardRequest, db: Session = Depends(get_db)):
    row = load_game(game_id, db)
    state = game_state_from_dict(row.state)

    if state.finished:
        raise HTTPException(status_code=400, detail="End")

    if state.current_player_index != HUMAN_INDEX:
        raise HTTPException(status_code=400, detail="Not your move")

    human = state.players[HUMAN_INDEX]
    card = find_card_in_hand(
        human.hand, request.card.color, request.card.card_type, request.card.value
    )
    chosen_color = Color(request.chosen_color) if request.chosen_color else None

    try:
        state.play_card(card, chosen_color)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    bot_action_text = None
    if not state.finished and state.current_player_index == BOT_INDEX:
        from game.bots.mcts_bot import bot_take_turn
        action = bot_take_turn(state, BOT_INDEX, MCTS_NUM_DETERMINIZATIONS, MCTS_ITERATIONS)
        bot_action_text = _describe_action(action)

    row.state = game_state_to_dict(state)
    row.finished = state.finished
    db.commit()

    return serialize_state(game_id, state, bot_action=bot_action_text)


@app.post("/game/{game_id}/draw", response_model=GameStateOut)
def draw_card(game_id: str, db: Session = Depends(get_db)):
    row = load_game(game_id, db)
    state = game_state_from_dict(row.state)

    if state.finished:
        raise HTTPException(status_code=400, detail="End")

    if state.current_player_index != HUMAN_INDEX:
        raise HTTPException(status_code=400, detail="Not your move")

    state.draw_card()

    bot_action_text = None
    if not state.finished and state.current_player_index == BOT_INDEX:
        from game.bots.mcts_bot import bot_take_turn
        action = bot_take_turn(state, BOT_INDEX, MCTS_NUM_DETERMINIZATIONS, MCTS_ITERATIONS)
        bot_action_text = _describe_action(action)

    row.state = game_state_to_dict(state)
    row.finished = state.finished
    db.commit()

    return serialize_state(game_id, state, bot_action=bot_action_text)