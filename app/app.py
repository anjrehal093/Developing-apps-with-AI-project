


import gradio as gr
import os
from backend import (
    generate_study_plan,
    generate_quote,
    save_study_plan,
    generate_quick_insights,
    get_next_task,
    load_habit_data,
    log_study_session,
    calculate_total_hours,
    calculate_streak,
    generate_weekly_summary,
    complete_current_task
)
from calendar_module import calendar_tab
import matplotlib.pyplot as plt
from backend import get_study_hours_by_task

def render_donut_chart():
    data = get_study_hours_by_task()

    fig, ax = plt.subplots(figsize=(4, 4))

    if not data:
        ax.text(0.5, 0.5, "No study data yet",
                ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    labels = list(data.keys())
    values = list(data.values())

    ax.pie(
        values,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        wedgeprops=dict(width=0.4)
    )

    ax.set_title("Study Time Breakdown")

    return fig




def load_dashboard():
        logs = load_habit_data()

        # ---- KPIs ----
        total_hours = calculate_total_hours(logs) if logs else 0
        streak = calculate_streak(logs) if logs else 0

        
        quote = generate_quote()
        quote_html = f"<div class='quote-bubble'>Stay consistent</div>"
        hours_html = f"<div class='kpi-box'>Hours Studied<br><b>{total_hours}</b></div>"
        streak_html = f"<div class='kpi-box'>Study Streak<br><b>{streak} days</b></div>"

        next_task = get_next_task()
        donut = render_donut_chart()
        if next_task:
            task_html = (
                f"<div class='next-task'>"
                f"Your next task:<br><b>{next_task}</b>"
                f"</div>"
            )
        else:
            task_html = (
                "<div class='next-task'>"
                "Generate a study plan to see your next task"
                "</div>"
            )



        return quote_html, hours_html, streak_html, task_html, donut
# -------------------------
# App Layout
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_css(theme):
    filename = "dark.css" if theme == "Dark" else "light.css"
    css_path = os.path.join(BASE_DIR, "assets", filename)
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()

dark_css = load_css("Dark")
light_css = load_css("Light")

def switch_theme(choice):
    css = light_css if choice == "Light" else dark_css
    return f"<style>{css}</style>"




with gr.Blocks() as demo:
    css_box = gr.HTML(f"<style>{dark_css}</style>")

    theme_state = gr.State("Dark")
    with gr.Tabs():
        
 
        # -----------------------------------------
        # HOME TAB
        # -----------------------------------------
        with gr.Tab("Home"):

            # Header
            gr.Markdown("<div class='sense-header'> SenseFlow Dashboard</div>")

            # Quote bubble
            quote_box = gr.Markdown("<div class='quote-bubble'> Quote loading...</div>")
            
           
            theme_toggle = gr.Radio(
            ["Dark", "Light"],
            value="Dark",
            label="Theme",
            elem_classes="theme-toggle"
        )
            
          


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
                    donut_plot = gr.Plot(label="Study Breakdown")


            # NEXT TASK BOX
            next_task_box = gr.Markdown(
                "<div class='next-task'>📌 Your next task is...<br>(Will be populated from study plan)</div>"
            )

            # NAVIGATION BUTTONS
            gr.Markdown("<div style='color:white; font-size:20px; margin-top:25px;'>Navigation</div>")

            with gr.Row():
                planner_btn = gr.Button("📘 Generate Study Plan", elem_classes="nav-btn")
                calendar_btn = gr.Button("📅 Calendar ", elem_classes="nav-btn")
                tracker_btn = gr.Button("📝 Log Studies", elem_classes="nav-btn")
                complete_task_btn = gr.Button("✅ Complete Task")
                complete_task_btn.click(
                    fn=complete_current_task,
                    inputs=None,
                    outputs=next_task_box
                )


                refresh_dashboard_btn = gr.Button("🔄 Refresh Dashboard", elem_classes="nav-btn")
                refresh_dashboard_btn.click(
                fn=load_dashboard,
                inputs=None,
                outputs=[quote_box, kpi_hours, kpi_streak, next_task_box,donut_plot]
            )

                quote_btn = gr.Button("🔄 Refresh Quote", elem_classes="nav-btn")
                quote_btn.click(
                fn=lambda: f"<div class='quote-bubble'>{generate_quote()}</div>",
                inputs=None,
                outputs=quote_box
)
       
        
        # -----------------------------------------
        # OTHER TABS (unchanged)
        # -----------------------------------------
        with gr.Tab("Study Planner"):

            gr.Markdown("## STUDY PLANNER")

            # ---- Add Task UI ----
            new_task = gr.Textbox(label="Add a Task")
            add_task_btn = gr.Button("➕ Add Task", elem_classes="nav-btn")

            # This holds the tasks internally
            task_list_state = gr.State([])

            # Where tasks will be shown on screen
            task_list_display = gr.Markdown("<div class='task-list'>No tasks added yet.</div>")

            # ---- Function to update tasks ----
            def add_task(task, task_list):
                if not task.strip():
                    return task_list, "<div class='task-list'>Enter a task first.</div>", ""

                new_list = (task_list or []) + [task.strip()]

                html = "<div class='task-list'><ul>"
                for t in new_list:
                    html += f"<li>{t}</li>"
                html += "</ul></div>"

                return new_list, html, ""

            add_task_btn.click(
                fn=add_task,
                inputs=[new_task, task_list_state],
                outputs=[task_list_state, task_list_display,new_task]
            )

            # ---- Study plan options ----
            time_input = gr.Slider(1, 8, label="Available Hours")
            difficulty = gr.Dropdown(["Easy", "Medium", "Hard"])
            style = gr.Dropdown(["Pomodoro", "Deep Work", "Short Sessions"])
             # ---- Deadline Input Section ----
            gr.Markdown("### ADD A DEADLINE")


            deadline_name = gr.Textbox(label="Deadline Name (e.g., Maths Exam)")
            deadline_date = gr.Textbox(label="Deadline Date (YYYY-MM-DD HH:MM)")

           

            generate_btn = gr.Button("Generate Plan", elem_classes="nav-btn")
            plan_output = gr.Markdown()

            # Function to combine tasks for the LLM (later)
            def prepare_plan(task_list, hours, diff, style, deadline_name, deadline_date):
                print("DEBUG prepare_plan called")
                print("tasks:", task_list)
                print("hours:", hours)
                print("difficulty:", diff)
                print("style:", style)
                print("deadline_name:", deadline_name)
                print("deadline_date:", deadline_date)
                if not task_list:
                    return "Add at least 1 task before generating a plan."

                tasks_joined = "\n".join(task_list)

                try:
                    plan = generate_study_plan(tasks_joined, hours, diff, style)
                except Exception as e:
                    print("LLM ERROR:", e)
                    return "AI plan generation failed."

                save_study_plan(
                    plan_text=plan,
                    tasks=task_list,
                    hours=hours,
                    study_style=style,
                    deadline={
                        "name": deadline_name or "Deadline",
                        "date": deadline_date
                    }
                )

                return plan
            generate_btn.click(
                    fn=prepare_plan,
                    inputs=[
                        task_list_state,
                        time_input,
                        difficulty,
                        style,
                        deadline_name,
                        deadline_date
                    ],
                    outputs=plan_output
                )



        with gr.Tab("Habit Tracker"):
            hours_input = gr.Slider(0, 6, label="Hours Studied")
            task_input = gr.Textbox(
        label="Task Studied",
        placeholder="e.g. maths"
    )

            log_btn = gr.Button("Log Session")
            log_output = gr.Markdown()
            log_btn.click(
            fn=log_study_session,
            inputs=[hours_input, task_input],
            outputs=log_output
)

        
        with gr.Tab("Calendar"):
            calendar_tab()
           
            



        with gr.Tab("Motivation"):

            # ---- Page Title ----
            gr.Markdown("<div class='motivation-title'>STUDY MOTIVATION</div>")

            # ---- Quote Placeholder ----
            motivation_quote = gr.Markdown(
                "<div class='motivation-quote'>Your motivational quote will appear here...</div>"
            )

            refresh_quote_btn = gr.Button("🔄 Refresh Quote", elem_classes="nav-btn")

            gr.Markdown("<hr style='border:1px solid #444; margin-top:20px;'>")

           

            # ---- Deadline List Placeholder ----
            deadlines_list = gr.Markdown(
                "<div class='deadline-list'>Your deadlines will appear here...</div>"
            )

            
    
    theme_toggle.change(
            fn=switch_theme,
            inputs=theme_toggle,
            outputs=css_box,
        )
    
    
    demo.load(
    fn=load_dashboard,
    inputs=None,
    outputs=[quote_box, kpi_hours, kpi_streak, next_task_box]
)



demo.launch()
