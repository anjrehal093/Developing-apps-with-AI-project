from openai import OpenAI
from prompts import STUDY_PLAN_PROMPT
from prompts import QUOTE_PROMPT

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

    return response.choices[0].message["content"]

import json
import os

PLAN_PATH = "current_plan.json"

def save_study_plan(plan_text):
    with open(PLAN_PATH, "w") as f:
        json.dump({"plan": plan_text}, f)

def load_study_plan():
    if not os.path.exists(PLAN_PATH):
        return None
    with open(PLAN_PATH, "r") as f:
        return json.load(f).get("plan")

from prompts import NEXT_TASK_EXTRACTION_PROMPT

def extract_next_task(plan_text):
    prompt = NEXT_TASK_EXTRACTION_PROMPT.format(plan=plan_text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]

HABIT_LOG_PATH = "habit_log.json"


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

from datetime import datetime

def log_study_session(hours, tasks_completed):
    log = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "hours": hours,
        "tasks_completed": tasks_completed
    }
    save_habit_data(log)
    return "Study session saved!"

from prompts import QUICK_INSIGHTS_PROMPT

def generate_quick_insights():
    logs = load_habit_data()

    prompt = QUICK_INSIGHTS_PROMPT.format(logs=logs)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]

from prompts import WEEKLY_SUMMARY_PROMPT

def generate_weekly_summary():
    logs = load_habit_data()

    prompt = WEEKLY_SUMMARY_PROMPT.format(logs=logs)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]

def generate_quote():
    prompt = QUOTE_PROMPT
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]