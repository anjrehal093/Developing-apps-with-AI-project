import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from prompts import STUDY_PLAN_PROMPT
from prompts import QUOTE_PROMPT
from prompts import NEXT_TASK_EXTRACTION_PROMPT
from prompts import QUICK_INSIGHTS_PROMPT
from prompts import WEEKLY_SUMMARY_PROMPT
from collections import defaultdict
from datetime import datetime
import json
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_study_plan(tasks, hours, difficulty, style):
    
    prompt = STUDY_PLAN_PROMPT.format(
        tasks=tasks,
        hours=hours,
        difficulty=difficulty,
        study_style=style
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAN_PATH = os.path.join(BASE_DIR, "current_plan.json")

HABIT_LOG_PATH = os.path.join(BASE_DIR, "habit_log.json")


def save_study_plan(plan_text, tasks, hours, study_style, deadline=None):
    """
    Saves:
    - Full plan text (for display)
    - Structured sessions (for calendar)
    """
    focus_blocks = extract_focus_blocks(plan_text)
    notes_lines = extract_notes_lines(plan_text)

    sessions = []
    session_id = 1

    # Repeat tasks to fill available hours
    task_index = 0
    while len(sessions) < hours:
        task_name = tasks[task_index % len(tasks)]

        focus_text = (
            focus_blocks[session_id - 1]
            if session_id - 1 < len(focus_blocks)
            else study_style
        )

        notes_text = (
            notes_lines[session_id - 1]
            if session_id - 1 < len(notes_lines)
            else f"Focus on {task_name} using {study_style}."
        )

        sessions.append({
            "session_id": session_id,
            "task": task_name,
            "duration_hours": 1,
            "focus": focus_text,
            "notes": notes_text
        })

        session_id += 1
        task_index += 1

    print("DEBUG saving sessions:", sessions)
    deadlines = []

    if deadline and deadline.get("date"):
        deadlines.append({
        "name": deadline.get("name", "Deadline"),
        "date": deadline["date"]
    })
    with open(PLAN_PATH, "w") as f:
        json.dump(
    {
        "plan": plan_text,
        "sessions": sessions,
        "deadlines": deadlines,
        "completed_sessions": [],
        "next_session": sessions[0]["session_id"] if sessions else None
    },
    f,
    indent=2
)



def extract_focus_blocks(plan_text):
    """
    Extracts Pomodoro / study-style breakdown per hour.
    Returns a list of multi-line strings.
    """
    focus_blocks = []
    current = []

    for line in plan_text.splitlines():
        line = line.strip()

        # Start collecting after Focus:
        if line.lower().startswith("focus:"):
            current = []
            continue

        # Stop when Notes starts
        if line.lower().startswith("notes:"):
            if current:
                focus_blocks.append("\n".join(current))
                current = []
            continue

        # Collect Pomodoro / style lines
        if any(
            line.lower().startswith(prefix)
            for prefix in ["25 minutes", "short break", "30 minutes", "15 minutes"]
        ):
            current.append(line)

    # Safety append
    if current:
        focus_blocks.append("\n".join(current))

    return focus_blocks

def extract_notes_lines(plan_text):
    """
    Extracts Notes per Study Hour from markdown plan.
    Supports:
    1) Inline:  - **Notes:** some text
    2) Block:   - **Notes:** then multiple bullet lines
    """
    notes = []
    collecting = False
    current = []

    for line in plan_text.splitlines():
        stripped = line.strip()

        # Start Notes section (inline or block)
        if stripped.startswith("- **Notes:**"):
            # Inline case: text after Notes:
            inline = stripped.replace("- **Notes:**", "").strip()
            if inline:
                notes.append(inline)
                collecting = False
                current = []
            else:
                collecting = True
                current = []
            continue

        # Stop collecting at separators / next hour / motivation
        if collecting and (
            stripped.startswith("---")
            or stripped.startswith("### Study Hour")
            or stripped.startswith("## Study Hour")
            or stripped.startswith("**Motivational")
        ):
            notes.append("\n".join(current).strip())
            collecting = False
            current = []
            continue

        # Collect block bullets / indented bullets
        if collecting:
            # accept both "- ..." and "  - ..."
            if stripped.startswith("-") or stripped.startswith("•"):
                current.append(stripped.lstrip("-• ").strip())
            elif stripped:  # also accept plain lines if model outputs them
                current.append(stripped)

    if collecting:
        notes.append("\n".join(current).strip())

    # Remove empty notes to avoid saving ""
    return [n for n in notes if n.strip()]




def load_study_plan():
    if not os.path.exists(PLAN_PATH):
        return None
    with open(PLAN_PATH, "r") as f:
        return json.load(f)




def get_next_task():
    plan = load_study_plan()
    if not plan:
        return None

    sessions = plan.get("sessions", [])
    completed = set(plan.get("completed_sessions", []))

    for s in sessions:
        if s["session_id"] not in completed:
            return f"{s['task']} ({s['focus']})"

    return "All sessions completed 🎉"




def load_habit_data():
    if not os.path.exists(HABIT_LOG_PATH):
        return []
    with open(HABIT_LOG_PATH, "r") as f:
        return json.load(f)


def save_habit_data(log):
    data = load_habit_data()
    data.append(log)
    with open(HABIT_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)
def complete_next_session():
    plan = load_study_plan()
    if not plan:
        return

    sessions = plan.get("sessions", [])
    completed = plan.get("completed_sessions", [])

    for s in sessions:
        sid = s["session_id"]
        if sid not in completed:
            completed.append(sid)
            break

    plan["completed_sessions"] = completed
    plan["next_session"] = next(
        (s["session_id"] for s in sessions if s["session_id"] not in completed),
        None
    )

    with open(PLAN_PATH, "w") as f:
        json.dump(plan, f, indent=2)

def log_study_session(hours, task):
    log = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "task": task,
        "hours": hours
        
    }
    save_habit_data(log)
    return "Study session saved!"
    complete_next_session()

def get_study_hours_by_task():
    logs = load_habit_data()

    if not logs:
        return {}

    task_hours = defaultdict(float)

    for log in logs:
        task = log.get("task")
        hours = log.get("hours", 0)

        if task:
            task_hours[task] += hours

    return dict(task_hours)
def calculate_total_hours(logs):
    return sum(log.get("hours", 0) for log in logs)

def calculate_streak(logs):
    # unique study dates
    dates = {log.get("date") for log in logs if "date" in log}
    return len(dates)



def generate_quick_insights():
    logs = load_habit_data()

    prompt = QUICK_INSIGHTS_PROMPT.format(logs=logs)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content



def generate_weekly_summary():
    logs = load_habit_data()

    prompt = WEEKLY_SUMMARY_PROMPT.format(logs=logs)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_quote():
    prompt = QUOTE_PROMPT
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def complete_current_task():
    plan = load_study_plan()
    if not plan or not plan.get("next_task"):
        return "<div class='next-task'>No active task.</div>"

    current = plan["next_task"]

    # Prevent double completion
    if current in plan["completed_tasks"]:
        return "<div class='next-task'>Task already completed.</div>"

    plan["completed_tasks"].append(current)

    remaining = [
        t for t in plan["tasks"]
        if t not in plan["completed_tasks"]
    ]

    if remaining:
        plan["next_task"] = remaining[0]
        message = f" Next task:<br><b>{remaining[0]}</b>"
    else:
        plan["next_task"] = None
        message = " All tasks completed!"

    

    with open(PLAN_PATH, "w") as f:
        json.dump(plan, f, indent=2)

    return f"<div class='next-task'>{message}</div>"

