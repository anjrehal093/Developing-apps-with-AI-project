
# ------------------------------------------------------------
# STUDY PLAN GENERATOR PROMPT
# ------------------------------------------------------------
STUDY_PLAN_PROMPT = """
You are an AI study coach helping a user plan their day efficiently.

Here is the information provided:
- Tasks to complete: {tasks}
- Available study time: {hours} hours
- Difficulty preference: {difficulty}
- Study style preference: {study_style}

Create a structured and realistic study plan that:
1. Breaks tasks into time blocks that fit within the available study hours.
2. Includes appropriate break intervals based on the study style.
3. Prioritises the most important tasks first.
4. Ensures the schedule is achievable and not overwhelming.
5. Ends with a short motivational message.

Format the output clearly with headings and time blocks.
"""


# ------------------------------------------------------------
# EXTRACT FIRST (NEXT) TASK FROM STUDY PLAN
# ------------------------------------------------------------
NEXT_TASK_EXTRACTION_PROMPT = """
You are an AI assistant. Your job is to extract ONLY the very first actionable task 
from the user’s generated study plan below.

Study plan:
{plan}

Return ONLY the first task as a short sentence. Do not explain anything.
"""


# ------------------------------------------------------------
# QUOTE OF THE DAY PROMPT
# ------------------------------------------------------------
QUOTE_PROMPT = """
Give me one short motivational study quote under 15 words.
Keep it encouraging, simple, and inspiring.
"""


# ------------------------------------------------------------
# QUICK INSIGHTS FROM HABIT LOG PROMPT
# ------------------------------------------------------------
QUICK_INSIGHTS_PROMPT = """
You are an AI analysing a student's study habit logs.

Here are the logs:
{logs}

Based on the data, provide EXACTLY three short insights about:
- productivity patterns
- consistency
- best/worst study days
- hours trend or task completion patterns

Make each insight one concise bullet point.
"""


# ------------------------------------------------------------
# WEEKLY SUMMARY PROMPT
# ------------------------------------------------------------
WEEKLY_SUMMARY_PROMPT = """
You are an AI study coach summarising a student's weekly performance.

Habit logs for the week:
{logs}

Write a clear weekly summary that includes:
1. Total hours studied this week
2. Best study day
3. Weakest study day
4. Tasks completed versus planned (based on detectable patterns)
5. Consistency observations
6. A final personalised recommendation

Format using short paragraphs and bullet points.
"""


# ------------------------------------------------------------
# DONUT PROGRESS (TASK COMPLETION) PROMPT – OPTIONAL
# ------------------------------------------------------------
DONUT_PROGRESS_PROMPT = """
You are an AI assistant summarising progress.

Tasks completed: {completed}
Tasks remaining: {remaining}

Return a VERY short sentence describing progress (e.g., "You have completed 60% of your tasks today.").
"""
