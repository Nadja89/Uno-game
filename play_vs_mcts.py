from game.card import Color
from game.game_state import GameState
from game.player import Player
from game.bots.mcts_bot import bot_take_turn


NUM_DETERMINIZATIONS = 20
ITERATIONS = 200


def print_hand(player: Player) -> None:
    print(f"\nYour hand ({player.card_count()} cards):")
    for i, card in enumerate(player.hand):
        print(f"  [{i}] {card}")


def choose_color() -> Color:
    colors = [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]
    print("Choose color:")
    for i, c in enumerate(colors):
        print(f"  [{i}] {c.value}")
    while True:
        choice = input("Input number of color: ").strip()
        if choice.isdigit() and 0 <= int(choice) < len(colors):
            return colors[int(choice)]
        print("Try again!")


def human_turn(gs: GameState, player: Player) -> None:
    print_hand(player)
    legal = gs.legal_moves()

    if not legal:
        if gs.pending_draw > 0:
            print(f"You have to pull {gs.pending_draw} cards")
        else:
            print("Not legal move")
        drawn = gs.draw_card()
        print(f"You pulled off: {[str(c) for c in drawn]}")
        return

    print("\nYou can play:")
    legal_indices = [i for i, c in enumerate(player.hand) if c in legal]
    for i in legal_indices:
        print(f"  [{i}] {player.hand[i]}")

    while True:
        choice = input("Your move: ").strip().lower()
        if choice.isdigit() and int(choice) in legal_indices:
            card = player.hand[int(choice)]
            chosen_color = choose_color() if card.is_wild() else None
            gs.play_card(card, chosen_color)
            print(f"You played: {card}")
            return
        print("Try again!")


def bot_turn(gs: GameState, player: Player, bot_index: int) -> None:
    print(f"\n{player.name} MCTS bot is thinking...")
    action = bot_take_turn(gs, bot_index, NUM_DETERMINIZATIONS, ITERATIONS)

    if action[0] == "draw":
        print(f"{player.name} draws a card.")
    else:
        _, card, color = action
        extra = f" (color: {color.value})" if color else ""
        print(f"{player.name} plays: {card}{extra}")


def main() -> None:
    human = Player(name="You")
    bot = Player(name="Bot", is_bot=True)
    gs = GameState([human, bot])
    bot_index = 1

    print(gs)

    while not gs.finished:
        print("\n" + "-" * 50)
        print(f"Cards on desk: {gs.top_card()} | Active color: {gs.active_color.value} | "
              f"Smer: {'forward' if gs.direction == 1 else 'back'}")
        if gs.pending_draw > 0:
            print(f"PENDING DRAW: {gs.pending_draw} cards!")
        print(f"Bot has {bot.card_count()} cards.")

        current = gs.current_player()
        if current is human:
            human_turn(gs, human)
        else:
            bot_turn(gs, bot, bot_index)

    print("\n" + "=" * 50)
    print(f"Game ended! Winner: {gs.winner.name}")


if __name__ == "__main__":
    main()