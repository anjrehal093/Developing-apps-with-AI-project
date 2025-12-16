import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from prompts import STUDY_PLAN_PROMPT
from prompts import QUOTE_PROMPT
from prompts import NEXT_TASK_EXTRACTION_PROMPT
from prompts import QUICK_INSIGHTS_PROMPT
from prompts import WEEKLY_SUMMARY_PROMPT

from datetime import datetime
import json


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



BASE_DIR = os.getcwd()
PLAN_PATH = os.path.join(BASE_DIR, "current_plan.json")
HABIT_LOG_PATH = os.path.join(BASE_DIR, "habit_log.json")


def save_study_plan(plan_text, tasks, deadline=None):
    print("Saving plan to:", os.path.abspath(PLAN_PATH))

    with open(PLAN_PATH, "w") as f:
        json.dump(
            {
                "plan": plan_text,
                "tasks": tasks,
                "deadline": deadline,
                "completed_tasks": [],
                "next_task": tasks[0] if tasks else None
            },
            f,
            indent=2
        )

def load_study_plan():
    if not os.path.exists(PLAN_PATH):
        return None
    with open(PLAN_PATH, "r") as f:
        return json.load(f)



"""def extract_next_task(plan_text):
    prompt = NEXT_TASK_EXTRACTION_PROMPT.format(plan=plan_text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]"""




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


def log_study_session(hours, tasks_completed):
    log = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "hours": hours,
        "tasks_completed": tasks_completed
    }
    save_habit_data(log)
    return "Study session saved!"

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

