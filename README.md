# CampusConnect

A simple web app where students report and track common issues around their college campus. Built for Code2Chill Weekly Project 01.

## Project Idea

Campus problems like a broken fan, a dead Wi-Fi router or a lost ID card are usually reported verbally and then forgotten. CampusConnect gives students one place to log an issue, pick a category, and follow its status from **Open** to **In Progress** to **Resolved**.

## Features

- Register and log in
- Create an issue with a title, description and category
- Categories: Classroom, Campus, Lost & Found, General
- Dashboard listing all submitted issues with counts per status
- Filter the list by status and category
- Issue details page (title, description, category, status, author, dates)
- Update the status: Open, In Progress, Resolved
- Simple profile page for the logged-in student

## Technologies Used

| Part | Technology |
|------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite |
| Version control | Git, GitHub |

## Project Structure

```
campusconnect/
├── backend/
│   ├── main.py        # FastAPI app and all API routes
│   ├── database.py    # SQLite tables and connection
│   └── auth.py        # Password hashing and login tokens
├── frontend/
│   ├── index.html     # Login / Register
│   ├── dashboard.html # Issue list and status counts
│   ├── create.html    # Create issue
│   ├── issue.html     # Issue details and status update
│   ├── profile.html   # Student profile
│   ├── css/style.css
│   └── js/app.js      # Shared helpers (API calls, login check)
├── requirements.txt
└── README.md
```

## How to Run the Project

You need Python 3.9 or newer.

> [!TIP]
> **Run the app with these three commands:**
>
> ```bash
> pip install -r requirements.txt
> cd backend
> uvicorn main:app --reload
> ```
>
> Then open <http://127.0.0.1:8000>.

Full setup from a fresh clone:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd campusconnect

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
cd backend
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000> in your browser. The SQLite database file (`backend/campusconnect.db`) is created automatically on first run.

FastAPI also generates interactive API docs at <http://127.0.0.1:8000/docs>.

## API Overview

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/register` | Create an account |
| POST | `/api/login` | Log in, returns a token |
| GET | `/api/me` | Logged-in student's profile |
| GET | `/api/categories` | Categories and statuses |
| GET | `/api/issues` | List issues (optional `status`, `category` filters) |
| POST | `/api/issues` | Create an issue |
| GET | `/api/issues/{id}` | Issue details |
| PATCH | `/api/issues/{id}/status` | Update status |

## Team Workflow

Everyone works on their own branch and merges through a pull request:

```
Branch -> Commit -> Push -> Pull Request -> Merge
```

```bash
git checkout -b feature/your-feature
git add .
git commit -m "Add create issue page"
git push -u origin feature/your-feature
# then open a Pull Request on GitHub
```

## Team Members

| Name | Contribution |
|------|--------------|
| _Member 1_ | _e.g. Backend API_ |
| _Member 2_ | _e.g. Login / Register page_ |
| _Member 3_ | _e.g. Dashboard and issue details_ |
| _Member 4_ | _e.g. Database, README, testing_ |
