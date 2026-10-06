"""CampusConnect - FastAPI backend.

Run from the backend folder:
    uvicorn main:app --reload
"""
import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from auth import create_session, get_current_user, hash_password, new_salt
from database import CATEGORIES, STATUSES, get_db, init_db

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="CampusConnect")
init_db()


# ---------- Request models ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=6, max_length=100)


class LoginIn(BaseModel):
    email: str
    password: str


class IssueIn(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=5, max_length=1000)
    category: str


class StatusIn(BaseModel):
    status: str


# ---------- Auth ----------
@app.post("/api/register")
def register(data: RegisterIn):
    email = data.email.strip().lower()
    if "@" not in email:
        raise HTTPException(400, "Enter a valid email")
    salt = new_salt()
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            (data.name.strip(), email, hash_password(data.password, salt), salt),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(400, "That email is already registered")
    finally:
        conn.close()
    return {"token": create_session(cur.lastrowid)}


@app.post("/api/login")
def login(data: LoginIn):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (data.email.strip().lower(),)
    ).fetchone()
    conn.close()
    if user is None or user["password_hash"] != hash_password(data.password, user["salt"]):
        raise HTTPException(401, "Wrong email or password")
    return {"token": create_session(user["id"])}


@app.get("/api/me")
def me(user: dict = Depends(get_current_user)):
    conn = get_db()
    count = conn.execute(
        "SELECT COUNT(*) FROM issues WHERE created_by = ?", (user["id"],)
    ).fetchone()[0]
    conn.close()
    return {**user, "issues_reported": count}


# ---------- Issues ----------
@app.get("/api/categories")
def categories():
    return {"categories": CATEGORIES, "statuses": STATUSES}


ISSUE_SELECT = """
    SELECT issues.*, users.name AS author
    FROM issues JOIN users ON users.id = issues.created_by
"""


@app.get("/api/issues")
def list_issues(
    status: str = "",
    category: str = "",
    user: dict = Depends(get_current_user),
):
    query = ISSUE_SELECT + " WHERE 1=1"
    params = []
    if status:
        query += " AND issues.status = ?"
        params.append(status)
    if category:
        query += " AND issues.category = ?"
        params.append(category)
    query += " ORDER BY issues.id DESC"
    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    summary = {
        s: conn.execute("SELECT COUNT(*) FROM issues WHERE status = ?", (s,)).fetchone()[0]
        for s in STATUSES
    }
    conn.close()
    return {"issues": [dict(r) for r in rows], "summary": summary}


@app.post("/api/issues", status_code=201)
def create_issue(data: IssueIn, user: dict = Depends(get_current_user)):
    if data.category not in CATEGORIES:
        raise HTTPException(400, "Pick a valid category")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO issues (title, description, category, created_by) VALUES (?, ?, ?, ?)",
        (data.title.strip(), data.description.strip(), data.category, user["id"]),
    )
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid}


@app.get("/api/issues/{issue_id}")
def get_issue(issue_id: int, user: dict = Depends(get_current_user)):
    conn = get_db()
    row = conn.execute(ISSUE_SELECT + " WHERE issues.id = ?", (issue_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(404, "Issue not found")
    return dict(row)


@app.patch("/api/issues/{issue_id}/status")
def update_status(issue_id: int, data: StatusIn, user: dict = Depends(get_current_user)):
    if data.status not in STATUSES:
        raise HTTPException(400, "Status must be Open, In Progress or Resolved")
    conn = get_db()
    cur = conn.execute(
        "UPDATE issues SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (data.status, issue_id),
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(404, "Issue not found")
    return {"ok": True, "status": data.status}


# ---------- Frontend ----------
@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
