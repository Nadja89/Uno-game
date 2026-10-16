import { useCallback, useEffect, useState } from "react";
import { api, session } from "./api";
import { CONFIRM_RESET_MS } from "./config";
import Logo from "./components/Logo";
import AuthScreen from "./components/AuthScreen";
import GameScreen from "./components/GameScreen";

export default function App() {
  const [user, setUser] = useState(() => (session.token() ? session.user() || "Player" : null));
  const [game, setGame] = useState(null);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(Boolean(session.token()));
  const [error, setError] = useState("");
  const [confirmingNew, setConfirmingNew] = useState(false);

  const signOut = useCallback(() => {
    session.clear();
    setUser(null);
    setGame(null);
    setNote("");
    setError("");
  }, []);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    setLoading(true);
    api
      .activeGame()
      .then((active) => {
        if (cancelled) return;
        setGame(active);
        setNote(active ? "Welcome back. Your unfinished game was restored." : "");
      })
      .catch((err) => {
        if (cancelled) return;
        if (err.status === 401) signOut();
        else setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [user, signOut]);

  useEffect(() => {
    if (!confirmingNew) return;
    const timer = setTimeout(() => setConfirmingNew(false), CONFIRM_RESET_MS);
    return () => clearTimeout(timer);
  }, [confirmingNew]);

  async function startGame() {
    setError("");
    setConfirmingNew(false);
    try {
      const created = await api.newGame();
      setNote("");
      setGame(created);
    } catch (err) {
      if (err.status === 401) signOut();
      else setError(err.message);
    }
  }

  function onNewGameClick() {
    if (game && !game.finished && !confirmingNew) {
      setConfirmingNew(true);
      return;
    }
    startGame();
  }

  if (!user) {
    return <AuthScreen onAuthed={setUser} />;
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar__brand">
          <Logo />
        </div>
        <div className="topbar__actions">
          <span className="topbar__user">{user}</span>
          {game && (
            <button type="button" className="button button--quiet" onClick={onNewGameClick}>
              {confirmingNew ? "Abandon this game?" : "New game"}
            </button>
          )}
          <button type="button" className="button button--quiet" onClick={signOut}>
            Sign out
          </button>
        </div>
      </header>

      <main className="stage">
        {loading && <p className="hint">Loading your game…</p>}

        {!loading && error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        {!loading && !game && (
          <div className="panel panel--glass lobby">
            <h2>Ready when you are</h2>
            <p>You and the bot each start with seven cards. The first to play every card wins.</p>
            <button type="button" className="button button--primary" onClick={startGame}>
              Start a game
            </button>
          </div>
        )}

        {!loading && game && (
          <GameScreen
            key={game.game_id}
            game={game}
            note={note}
            onUpdate={setGame}
            onNewGame={startGame}
            onAuthError={signOut}
          />
        )}
      </main>
    </div>
  );
}
