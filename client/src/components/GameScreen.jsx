import { useState } from "react";
import { api } from "../api";
import { COLOR_NAMES, cardName, isWild, sameCard } from "../cards";
import { MAX_LOG_LINES, MAX_OPPONENT_CARDS_SHOWN } from "../config";
import ColorPicker from "./ColorPicker";
import UnoCard from "./UnoCard";

function BotIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="4" y="8" width="16" height="11" rx="3" />
      <path d="M12 8V4.5" />
      <circle cx="12" cy="4" r="1" fill="currentColor" />
      <circle cx="9" cy="13.5" r="1.1" fill="currentColor" stroke="none" />
      <circle cx="15" cy="13.5" r="1.1" fill="currentColor" stroke="none" />
    </svg>
  );
}

function PlayerIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="8.5" r="3.6" />
      <path d="M4.5 20c.8-4 3.8-6 7.5-6s6.7 2 7.5 6" />
    </svg>
  );
}

let logCounter = 0;

function entry(text, tone) {
  logCounter += 1;
  return { id: logCounter, text, tone };
}

function statusText(game) {
  if (game.finished) return game.you_won ? "You won the game." : "The bot won the game.";
  if (game.pending_draw > 0) return `You must draw ${game.pending_draw} cards.`;
  if (game.playable_cards.length === 0) return "No playable card. Draw from the pile.";
  return "Your turn. Play one of the raised cards.";
}

export default function GameScreen({ game, onUpdate, onNewGame, onAuthError, note }) {
  const [busy, setBusy] = useState(false);
  const [pendingWild, setPendingWild] = useState(null);
  const [error, setError] = useState("");
  const [log, setLog] = useState(note ? [entry(note, "system")] : []);

  const mustDraw = !game.finished && (game.pending_draw > 0 || game.playable_cards.length === 0);

  function remember(lines) {
    setLog((previous) => [...lines.reverse(), ...previous].slice(0, MAX_LOG_LINES));
  }

  async function run(action, describeYourMove) {
    setBusy(true);
    setError("");
    try {
      const next = await action();
      const lines = [entry(describeYourMove(next), "you")];
      next.bot_actions.forEach((text) => lines.push(entry(text, "bot")));
      remember(lines);
      onUpdate(next);
    } catch (err) {
      if (err.status === 401) {
        onAuthError();
        return;
      }
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function playCard(card, color) {
    setPendingWild(null);
    run(
      () => api.play(game.game_id, card, color),
      () => `You played ${cardName(card).toLowerCase()}${color ? ` and chose ${COLOR_NAMES[color].toLowerCase()}` : ""}.`
    );
  }

  function drawCard() {
    const before = game.your_hand.length;
    run(
      () => api.draw(game.game_id),
      (next) => {
        const count = next.your_hand.length - before;
        return `You drew ${count} ${count === 1 ? "card" : "cards"}.`;
      }
    );
  }

  function chooseCard(card) {
    if (busy || game.finished) return;
    if (isWild(card)) {
      setPendingWild(card);
      return;
    }
    playCard(card, null);
  }

  const opponentShown = Math.min(game.opponent_card_count, MAX_OPPONENT_CARDS_SHOWN);
  const middle = (game.your_hand.length - 1) / 2;
  const topCard = game.top_card;

  const botTurn = busy && !game.finished;
  const yourTurn = !busy && !game.finished;

  return (
    <section className="arena" aria-busy={busy} style={{ "--glow": `var(--${game.active_color})` }}>
      <div className="arena__main">
        <div className="seat seat--bot">
          <div className={`chip ${botTurn ? "is-active" : ""}`}>
            <span className="avatar">
              <BotIcon />
            </span>
            <span className="chip__text">
              <strong>Bot</strong>
              <span>
                {game.opponent_card_count} {game.opponent_card_count === 1 ? "card" : "cards"}
              </span>
            </span>
          </div>
          <div className="opponent-hand" aria-hidden="true">
            {Array.from({ length: opponentShown }, (_, i) => (
              <UnoCard key={i} back size="sm" />
            ))}
            {game.opponent_card_count > opponentShown && (
              <span className="opponent-hand__more">+{game.opponent_card_count - opponentShown}</span>
            )}
          </div>
        </div>

        <div className="center">
          <div className="pile">
            <button
              type="button"
              className={`pile__draw ${mustDraw ? "is-urgent" : ""}`}
              onClick={drawCard}
              disabled={busy || game.finished}
              aria-label={game.pending_draw > 0 ? `Draw ${game.pending_draw} cards` : "Draw a card"}
            >
              <UnoCard back size="lg" />
              <span className="pile__stack" aria-hidden="true" />
            </button>
            <span className="pile__caption">
              {game.pending_draw > 0 ? `Draw ${game.pending_draw}` : "Draw pile"}
            </span>
          </div>

          <div className="pile">
            <div className="discard" style={{ "--ring": `var(--${game.active_color})` }}>
              <UnoCard
                key={`${cardName(topCard)}-${game.your_hand.length}-${game.opponent_card_count}`}
                card={topCard}
                size="lg"
                label={`Top card: ${cardName(topCard)}`}
              />
            </div>
            <span className="pile__caption">
              <span className={`dot dot--${game.active_color}`} aria-hidden="true" />
              Active color: {COLOR_NAMES[game.active_color]}
            </span>
          </div>
        </div>

        <div className="seat seat--you">
          <div className={`chip ${yourTurn ? "is-active" : ""}`}>
            <span className="avatar">
              <PlayerIcon />
            </span>
            <span className="chip__text">
              <strong>You</strong>
              <span>
                {game.your_hand.length} {game.your_hand.length === 1 ? "card" : "cards"}
              </span>
            </span>
          </div>
          <div className="hand">
            {game.your_hand.map((card, index) => {
              const playable = game.playable_cards.some((p) => sameCard(p, card));
              const offset = index - middle;
              return (
                <UnoCard
                  key={`${card.color}-${card.card_type}-${card.value}-${index}`}
                  card={card}
                  playable={playable}
                  dimmed={!playable && !game.finished}
                  onClick={playable ? () => chooseCard(card) : undefined}
                  style={{ "--tilt": `${offset * 1.6}deg`, "--drop": `${Math.abs(offset) * 1.5}px` }}
                />
              );
            })}
          </div>
        </div>
      </div>

      <aside className="side" role="status" aria-live="polite">
        <div>
          <p className="side__title">Status</p>
          <p className="turn__text">
            {botTurn ? (
              <span className="thinking">
                Bot is thinking<i>.</i>
                <i>.</i>
                <i>.</i>
              </span>
            ) : (
              statusText(game)
            )}
          </p>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
        </div>
        {log.length > 0 && (
          <div>
            <p className="side__title">Recent moves</p>
            <ul className="log" aria-label="Recent moves">
              {log.map((line, index) => (
                <li key={line.id} className={`log__line log__line--${line.tone} ${index === 0 ? "is-latest" : ""}`}>
                  {line.text}
                </li>
              ))}
            </ul>
          </div>
        )}
      </aside>

      {pendingWild && (
        <ColorPicker onPick={(color) => playCard(pendingWild, color)} onCancel={() => setPendingWild(null)} />
      )}

      {game.finished && (
        <div className="overlay" role="dialog" aria-modal="true" aria-label="Game over">
          <div className="panel panel--glass result">
            <h2>{game.you_won ? "You won!" : "The bot won."}</h2>
            <p>
              {game.you_won
                ? "You played your last card first."
                : "The bot played its last card first."}
            </p>
            <button type="button" className="button button--primary" onClick={onNewGame}>
              Play again
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
