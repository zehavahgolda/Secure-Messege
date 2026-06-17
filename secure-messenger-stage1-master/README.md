# Secure Messenger

Authenticated FastAPI messenger with encrypted-at-rest messages and an SSE stream for realtime delivery.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Generate real secrets for `.env`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
```

Put the first value in `JWT_SECRET_KEY` and the second in `AES_KEY`.

Run the API:

```powershell
uvicorn server.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Design Decisions

Passwords are hashed with bcrypt because password hashing should be intentionally slow. Fast hashes like SHA-256 are built for speed, which makes stolen password databases much easier to brute-force.

Messages are encrypted with AES-256-GCM before they are stored. GCM provides confidentiality and tamper detection. The database stores `ciphertext`; API responses and SSE events return decrypted `content` only to authenticated users.

JWT authentication is implemented as a FastAPI dependency with `Depends(require_auth)`, so protected routes share one validation path instead of duplicating token checks.

SSE is used for realtime delivery because this app only needs one-way server-to-client events. The stream emits named `message` events, so browser clients can use `addEventListener("message", ...)`. A full browser client would also need query-token or cookie-based stream auth because native `EventSource` cannot set custom headers.

Secrets are loaded from environment variables. This keeps keys out of source control and makes the AES key stable across server restarts, so previously stored ciphertext remains decryptable.

CORS is configured for local browser development on `localhost:3000` and `127.0.0.1:3000`.

Alembic is configured so schema changes can be migrated instead of dropping the database during development.

## Security Notes

`POST /login` always performs a bcrypt check, even when the username does not exist, using a dummy hash. That reduces timing differences between "unknown user" and "wrong password". A production version should still add rate limiting and account lockout/backoff.

The `.env` file is ignored by git. Never commit real `JWT_SECRET_KEY` or `AES_KEY` values.

## Tests

```powershell
pytest tests/ -v
```
