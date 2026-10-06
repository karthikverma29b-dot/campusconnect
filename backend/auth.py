"""Password hashing and simple token-based login."""
import hashlib
import secrets

from fastapi import Header, HTTPException

from database import get_db


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()


def new_salt() -> str:
    return secrets.token_hex(16)


def create_session(user_id: int) -> str:
    token = secrets.token_hex(32)
    conn = get_db()
    conn.execute(
        "INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id)
    )
    conn.commit()
    conn.close()
    return token


def get_current_user(authorization: str = Header(default="")):
    """Reads 'Authorization: Bearer <token>' and returns the user row."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please log in")
    token = authorization[len("Bearer "):]
    conn = get_db()
    user = conn.execute(
        """SELECT users.id, users.name, users.email, users.created_at
           FROM sessions JOIN users ON users.id = sessions.user_id
           WHERE sessions.token = ?""",
        (token,),
    ).fetchone()
    conn.close()
    if user is None:
        raise HTTPException(status_code=401, detail="Session expired, log in again")
    return dict(user)
