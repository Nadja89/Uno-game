 UNO + Monte Carlo Tree Search

Igra UNO za dva igrača (čovek protiv bota) sa botom zasnovanim na Monte Carlo Tree Search
algoritmu. Praktični deo diplomskog rada „Primena Monte Carlo Tree Search algoritma za
donošenje odluka u igri UNO".

 Struktura

| Fajl / folder | Sadržaj |

| `config.py` | svi parametri (MCTS, heuristika, pravila, bezbednost) na jednom mestu |
| `game/` | pravila igre: `card`, `deck`, `player`, `game_state`, `belief`, `serialization` |
| `game/bots/` | `mcts_bot.py` (MCTS sa determinizacijom), `heuristics.py` (politika za simulaciju) |
| `api/`, `db/` | FastAPI + PostgreSQL, JWT autentifikacija |
| `client/` | React klijent (Vite) |
| `tests/` | pytest testovi |

 Pokretanje servera


python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn api.main:app --reload


U `.env` popuni `DATABASE_URL` i `JWT_SECRET_KEY`. Dokumentacija i probanje API-ja:
`http://127.0.0.1:8000/docs` (dugme Authorize, token se dobija preko `/auth/login`).
Testovi: `pytest`.

 Pokretanje klijenta

Potreban je Node.js. Server mora da radi na portu 8000.


cd client
npm install
npm run dev


Klijent se otvara na `http://localhost:5173`. Adresa servera se menja u `client/.env`
(`VITE_API_URL`, primer u `client/.env.example`).
