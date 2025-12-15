import gradio as gr
from prompts import QUOTE_PROMPT

# -------------------------
# Custom CSS (matches your image)
# -------------------------

custom_css = """
/* Page background */
body { 
    background-color: #0c0c0f !important; 
}

/* Header */
.sense-header {
    color: white;
    font-size: 32px;
    text-align: center;
    margin-bottom: 20px;
}

/* Quote bubble */
.quote-bubble {
    background: #e8c8ff;
    color: black;
    padding: 15px;
    border-radius: 50px;
    text-align: center;
    width: 60%;
    margin: 0 auto;
    font-size: 18px;
}

/* KPI cards */
.kpi-box {
    background: #d8b7ff;
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 12px;
    color: black;
    font-size: 18px;
    text-align: center;
}

/* Next Task banner */
.next-task {
    background: #e3c2ff;
    padding: 25px;
    border-radius: 25px;
    margin-top: 25px;
    text-align: center;
    font-size: 20px;
}

/* Navigation Buttons */
.nav-btn {
    background: #dcb8ff !important;
    color: black !important;
    border-radius: 50px !important;
    padding: 14px !important;
    font-size: 16px !important;
    border: none !important;
}
"""


# -------------------------
# Dashboard placeholder loader
# -------------------------
from backend import (
    generate_quick_insights,
    extract_next_task,
    load_study_plan,
    load_habit_data
)


def load_dashboard():
    # Quote
    quote = "✨ " + generate_quick_insights().split("\n")[0]  # temporary until quote function made

    # Hours studied
    logs = load_habit_data()
    total_hours = sum(log["hours"] for log in logs)

    # Streak (you will add calculate_streak() later)
    streak = len(logs)

    # Next task
    plan = load_study_plan()
    if plan:
        next_task = extract_next_task(plan)
    else:
        next_task = "No study plan yet."

    return quote, f"{total_hours} hours", f"{streak} days", next_task


# -------------------------
# App Layout
# -------------------------

with gr.Blocks(css=custom_css) as demo:

    with gr.Tabs():

        # -----------------------------------------
        # HOME TAB
        # -----------------------------------------
        with gr.Tab("Home"):

            # Header
            gr.Markdown("<div class='sense-header'> SenseFlow Dashboard</div>")

            # Quote bubble
            quote_box = gr.Markdown("<div class='quote-bubble'> Quote loading...</div>")

            # KPI + Donut layout
            with gr.Row():

                # LEFT SIDE KPIs
                with gr.Column(scale=1):
                    kpi_hours = gr.Markdown("<div class='kpi-box'>Hours Studied: --</div>")
                    kpi_streak = gr.Markdown("<div class='kpi-box'>Study Streak: --</div>")

                # RIGHT SIDE DONUT
                with gr.Column(scale=2):
                    gr.Markdown(
                        "<div style='color:white; font-size:20px; margin-bottom:10px;'>Progress Donut</div>"
                    )
                    donut_placeholder = gr.Markdown(
                        "<div style='color:white;'>🍩 Donut chart will appear here (Tasks Completed vs Tasks Left)</div>"
                    )

            # NEXT TASK BOX
            next_task_box = gr.Markdown(
                "<div class='next-task'>📌 Your next task is...<br>(Will be populated from study plan)</div>"
            )

            # NAVIGATION BUTTONS
            gr.Markdown("<div style='color:white; font-size:20px; margin-top:25px;'>Navigation</div>")

            with gr.Row():
                planner_btn = gr.Button("📘 Generate Study Plan", elem_classes="nav-btn")
                calendar_btn = gr.Button("📅 Calendar (optional)", elem_classes="nav-btn")
                tracker_btn = gr.Button("📝 Log Studies", elem_classes="nav-btn")

        # -----------------------------------------
        # OTHER TABS (unchanged)
        # -----------------------------------------
        with gr.Tab("Study Planner"):
            tasks_input = gr.Textbox(label="Tasks")
            time_input = gr.Slider(1, 8, label="Available Hours")
            difficulty = gr.Dropdown(["Easy", "Medium", "Hard"])
            style = gr.Dropdown(["Pomodoro", "Deep Work", "Short Sessions"])

            generate_btn = gr.Button("Generate Plan")
            plan_output = gr.Markdown()

        with gr.Tab("Habit Tracker"):
            hours_input = gr.Slider(0, 6, label="Hours Studied")
            tasks_completed = gr.Slider(0, 10, label="Tasks Completed")
            log_btn = gr.Button("Log Session")
            log_output = gr.Markdown()

        with gr.Tab("Weekly Insights"):
            summary_btn = gr.Button("Generate Weekly Summary")
            summary_output = gr.Markdown()


    # Load homepage values
    demo.load(
        load_dashboard,
        inputs=None,
        outputs=[quote_box, kpi_hours, kpi_streak, next_task_box]
    )

demo.launch()
