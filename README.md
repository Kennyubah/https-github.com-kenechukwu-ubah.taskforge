# TaskForge

TaskForge is a small single-user Flask web application for managing software development tasks across SDLC phases. It is designed as a simple university prototype with SQLite persistence and a clean Bootstrap interface.

## Features

- Dashboard with total, completed, and blocked task counts
- Task count by SDLC phase
- Create, view, edit, and delete tasks
- Task fields for priority, status, SDLC phase, due date, notes, blocker reason, and timestamps
- Basic validation requiring every task to have a title
- SQLite database stored locally as `taskforge.db`

## Folder Structure

```text
TaskForge/
├── app.py
├── requirements.txt
├── README.md
├── static/
│   └── css/
│       └── styles.css
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── task_form.html
    └── tasks.html
```

## How to Run

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows, use:

```bash
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the application:

```bash
python app.py
```

4. Open the application in your browser:

```text
http://127.0.0.1:5050
```

The SQLite database is created automatically the first time the app runs.

Note: TaskForge uses port `5050` because port `5000` may already be used by Apple AirPlay/Control Center on macOS.
