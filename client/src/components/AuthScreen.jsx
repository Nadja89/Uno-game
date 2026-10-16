import { useState } from "react";
import { api, session } from "../api";
import Logo from "./Logo";
import UnoCard from "./UnoCard";

const DRIFT = [
  { card: { color: "red", card_type: "number", value: 3 }, left: 4, dur: 17, delay: 0, scale: 0.8 },
  { card: { color: "yellow", card_type: "skip", value: null }, left: 16, dur: 22, delay: 6, scale: 1 },
  { card: { color: "blue", card_type: "number", value: 9 }, left: 30, dur: 19, delay: 11, scale: 0.7 },
  { card: { color: "green", card_type: "reverse", value: null }, left: 48, dur: 24, delay: 3, scale: 0.9 },
  { card: { color: "wild", card_type: "wild_draw_four", value: null }, left: 62, dur: 18, delay: 9, scale: 0.75 },
  { card: { color: "red", card_type: "draw_two", value: null }, left: 76, dur: 21, delay: 14, scale: 1 },
  { card: { color: "blue", card_type: "number", value: 5 }, left: 88, dur: 16, delay: 5, scale: 0.8 },
  { card: { color: "yellow", card_type: "number", value: 1 }, left: 94, dur: 23, delay: 12, scale: 0.65 },
];

const FAN = [
  { color: "blue", card_type: "reverse", value: null, r: -34, x: -150 },
  { color: "yellow", card_type: "number", value: 7, r: -17, x: -75 },
  { color: "wild", card_type: "wild", value: null, r: 0, x: 0 },
  { color: "green", card_type: "draw_two", value: null, r: 17, x: 75 },
  { color: "red", card_type: "skip", value: null, r: 34, x: 150 },
];

export default function AuthScreen({ onAuthed }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const creating = mode === "register";

  async function submit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const action = creating ? api.register : api.login;
      const { access_token } = await action(username.trim(), password);
      session.save(access_token, username.trim());
      onAuthed(username.trim());
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth">
      <div className="drift" aria-hidden="true">
        {DRIFT.map((item, i) => (
          <span
            key={i}
            className="drift__card"
            style={{ left: `${item.left}%`, "--dur": `${item.dur}s`, "--delay": `-${item.delay}s`, "--s": item.scale }}
          >
            <UnoCard card={item.card} />
          </span>
        ))}
      </div>
      <section className="auth__hero">
        <div className="fan" aria-hidden="true">
          {FAN.map((card, i) => (
            <UnoCard
              key={i}
              card={card}
              style={{ "--r": `${card.r}deg`, "--x": `calc(${card.x} / 150 * var(--card-w) * 0.95)`, "--i": i }}
            />
          ))}
        </div>
        <h1>
          <Logo size="xl" />
        </h1>
      </section>
      <form className="panel panel--glass auth__form" onSubmit={submit}>
        <div className="segmented" role="tablist" aria-label="Account">
          <button
            type="button"
            role="tab"
            aria-selected={!creating}
            className={!creating ? "is-active" : ""}
            onClick={() => setMode("login")}
          >
            Sign in
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={creating}
            className={creating ? "is-active" : ""}
            onClick={() => setMode("register")}
          >
            Create account
          </button>
        </div>

        <label className="field">
          <span>Username</span>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
            autoFocus
          />
        </label>
        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={creating ? "new-password" : "current-password"}
            required
          />
        </label>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button className="button button--primary" type="submit" disabled={busy}>
          {busy ? "Please wait…" : creating ? "Create account" : "Sign in"}
        </button>
      </form>
    </main>
  );
}
