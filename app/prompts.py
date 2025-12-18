
# ------------------------------------------------------------
# STUDY PLAN GENERATOR PROMPT
# ------------------------------------------------------------
STUDY_PLAN_PROMPT = """
You are an AI study coach helping a user plan their study time for the day.

Here is the information provided:
- Tasks to complete: {tasks}
- Available study time: {hours} hours
- Difficulty preference: {difficulty}
- Study style preference: {study_style}

Create a clear, realistic study plan that follows these rules:

1. Allocate the available study time into ONE-HOUR study blocks.
2. Each task may appear multiple times if more than one hour is available.
3. Do NOT include exact clock times.
4. Prioritise higher-importance or harder tasks earlier.
5. Study style rules:
   - Pomodoro: describe each hour as two 25-minute focus sessions with short breaks.
   - Deep Work: describe each hour as uninterrupted focused work.
   - Short Sessions: describe each hour as lighter review-focused study.

For EACH study hour, include:
- Task name
- Duration (always 1 hour)
- Focus (how the hour should be used)
- Notes (practical guidance for the user)

End with a short motivational message.

Format the output clearly using headings and bullet points.
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
