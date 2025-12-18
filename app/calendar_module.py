import gradio as gr
from datetime import date, timedelta,datetime
from backend import load_study_plan





DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIMES = [f"{h:02d}:00" for h in range(8, 21)] 

PINK = "#f07aa6"
PINK_SOFT = "#fde6ee"
PINK_GRID = "#f6c1d3"
WHITE = "#ffffff"

CSS = f"""
:root {{
  --pink: {PINK};
  --pink-soft: {PINK_SOFT};
  --pink-grid: {PINK_GRID};
  --white: {WHITE};
}}

.gradio-container {{
  background: var(--pink-soft) !important;
}}

#planner_wrap {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 10px 10px;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}}

#topbar {{
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}}

#title {{
  font-size: 52px;
  font-weight: 800;
  text-align: center;
  color: var(--pink);
  letter-spacing: 0.5px;
}}

#navBtns {{
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}}

.pl-btn {{
  background: rgba(255,255,255,0.55);
  border: 2px solid var(--pink-grid);
  color: var(--pink);
  padding: 10px 14px;
  border-radius: 10px;
  font-weight: 700;
}}

#grid {{
  border: 2px solid var(--pink-grid);
  border-radius: 2px;
  overflow: hidden;
  background: rgba(255,255,255,0.25);
}}

.pl-row {{
  display: grid;
  grid-template-columns: 160px repeat(7, 1fr);
}}

.pl-head {{
  background: rgba(255,255,255,0.35);
}}

.pl-cell {{
  border-right: 2px solid var(--pink-grid);
  border-bottom: 2px solid var(--pink-grid);
  min-height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--pink);
  font-weight: 700;
}}

.pl-cell:last-child {{
  border-right: none;
}}

.pl-time {{
  justify-content: center;
  font-size: 20px;
  background: rgba(255,255,255,0.12);
}}

.pl-day {{
  font-size: 20px;
}}

.pl-day.active {{
  background: var(--pink);
  color: white;
}}

.pl-slot {{
  background: rgba(255,255,255,0.12);
  font-weight: 600;
  color: rgba(240,122,166,0.95);
  padding: 6px 8px;
  justify-content: flex-start;
}}

#bottomBtns {{
  display: flex;
  gap: 18px;
  justify-content: center;
  margin-top: 18px;
}}

.action {{
  border-radius: 10px !important;
  border: 2px solid var(--pink-grid) !important;
  font-weight: 800 !important;
}}

#saveBtn button {{
  background: var(--pink) !important;
  color: white !important;
  border: 2px solid var(--pink) !important;
}}
.deadline-badge {{
    background: #ffd6e8;
    color: #7a1f4d;
    padding: 4px 6px;
    border-radius: 6px;
    font-size: 11px;
    margin-top: 4px;
    text-align: center;
    font-weight: 600;
}}


#addBtn button, #cancelBtn button {{
  background: rgba(255,255,255,0.55) !important;
  color: var(--pink) !important;
}}

"""
#functions for day and week plans
def start_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())  # Monday

def format_date_eu(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")

def week_label(week_start: date) -> str:
    week_end = week_start + timedelta(days=6)
    return f"Week: {week_start.isoformat()} → {week_end.isoformat()}"

def render_planner_html(week_start: date, tasks: dict) -> str:
    head = f"""
    <div id="planner_wrap">
      <div id="topbar">
        <div id="title">Weekly Planner</div>
        <div id="navBtns">
          <span class="pl-btn">Previous Week ›</span>
          <span class="pl-btn">Next Week ›</span>
        </div>
      </div>

      <div style="text-align:center; color:{PINK}; font-weight:700; margin-bottom:10px;">
        {week_label(week_start)}
      </div>

      <div id="grid">
        <div class="pl-row pl-head">
          <div class="pl-cell pl-day">Time</div>
          {"".join([
    f'''
    <div class="pl-cell pl-day {"active" if i==0 else ""}">
        <div class="day-name">{d}</div>
        {render_deadline_badge(week_start + timedelta(days=i))}
    </div>
    '''
    for i, d in enumerate(DAYS)
])}

        </div>
    """

    rows = []
    for t in TIMES:
        row_cells = [f'<div class="pl-cell pl-time">{t}</div>']
        for di in range(7):
            cell = tasks.get((di, t), "")
            txt = cell["label"] if isinstance(cell, dict) else (cell or "")

            row_cells.append(f'<div class="pl-cell pl-slot">{txt}</div>')
        rows.append(f'<div class="pl-row">{"".join(row_cells)}</div>')

    tail = """
      </div>
    </div>
    """
    return head + "\n".join(rows) + tail
def render_deadline_badge(day_date: date) -> str:
    plan = load_study_plan()
    if not plan:
        return ""

    badges = []

    for d in plan.get("deadlines", []):
        if d["date"] == day_date.isoformat():
            badges.append(
                f"""
                <div class="deadline-badge">
                    📌 {d['name']} — {format_date_eu(d['date'])}
                </div>
                """
            )

    return "".join(badges)

def init_state():
    return {
        "week_start": start_of_week(date.today()),
        "tasks": {}  # (day_index, time_str) -> str
    }
def assign_session_to_slot(state, day_name, time_str, session_id):
    if not session_id:
        return ui_refresh(state)

    plan = load_study_plan()
    if not plan:
        return ui_refresh(state)

    session = next(
        (s for s in plan.get("sessions", []) if s["session_id"] == session_id),
        None
    )
    if not session:
        return ui_refresh(state)

    di = DAYS.index(day_name)
    state["tasks"][(di, time_str)] = {
        "label": session["task"],
        "notes": session.get("notes", ""),
        "session_id": session_id
    }

    return ui_refresh(state)

def ui_refresh(state):
    return render_planner_html(state["week_start"], state["tasks"]), week_label(state["week_start"])
def session_choices():
    plan = load_study_plan()
    print("DEBUG plan loaded in calendar:", plan)
    sessions = plan.get("sessions", []) if plan else []

    choices = [(f"Session {s['session_id']} — {s['task']}", s["session_id"]) for s in sessions]

    # IMPORTANT: return an update so Gradio sets choices + clears value safely
    return gr.update(choices=choices, value=None)



def prev_week(state):
    state["week_start"] = state["week_start"] - timedelta(days=7)
    return ui_refresh(state)

def next_week(state):
    state["week_start"] = state["week_start"] + timedelta(days=7)
    return ui_refresh(state)

def add_task(state, day_name, time_str, text):
    if not text.strip():
        return ui_refresh(state)
    di = DAYS.index(day_name)
    state["tasks"][(di, time_str)] = {
    "label": text.strip(),
    "notes": "",
    "session_id": None
}


    return ui_refresh(state)

def cancel_clear(state):
    state["tasks"] = {}
    return ui_refresh(state)
def save_export_json(state):
    out = {
        "week_start": state["week_start"].isoformat(),
        "tasks": []
    }

    for (di, t), cell in sorted(state["tasks"].items(), key=lambda x: (x[0][0], x[0][1])):
        if isinstance(cell, dict):
            out["tasks"].append({
                "day": DAYS[di],
                "time": t,
                "text": cell.get("label", ""),
                "notes": cell.get("notes", ""),
                "session_id": cell.get("session_id")
            })
        else:
            out["tasks"].append({
                "day": DAYS[di],
                "time": t,
                "text": str(cell)
            })

    return out

def view_slot_notes(state, day_name, time_str):
    di = DAYS.index(day_name)
    cell = state["tasks"].get((di, time_str))
    if isinstance(cell, dict):
        return cell.get("notes", "")
    return "No notes for this slot."









def calendar_tab():
    # Local state for this tab
    
    print("DEBUG calendar_tab called")

    state = gr.State(init_state())
    


    # Inject calendar-only CSS (pink)
    gr.HTML(f"<style>{CSS}</style>")  # or CALENDAR_CSS if you renamed it

    # Planner display (HTML grid)
    planner_html = gr.HTML()
    week_text = gr.Textbox(label="Week", interactive=False)

    # Week nav
    with gr.Row():
        prev_btn = gr.Button("Previous Week", variant="secondary")
        next_btn = gr.Button("Next Week", variant="secondary")

    # Controls to add tasks
    with gr.Row():
        day_dd = gr.Dropdown(DAYS, value="Monday", label="Day")
        time_dd = gr.Dropdown(TIMES, value="08:00", label="Time (24h)")
        task_tb = gr.Textbox(label="Task", placeholder="e.g., Math revision")
        session_dd = gr.Dropdown(label="Pick a generated session",choices=[],value=None)
        refresh_sessions_btn = gr.Button("🔄 Refresh Sessions", variant="secondary")


    

    with gr.Row():
        add_btn = gr.Button("＋ Add Task", elem_id="addBtn", elem_classes=["action"])
        save_btn = gr.Button("Save", elem_id="saveBtn", elem_classes=["action"])
        cancel_btn = gr.Button("Cancel", elem_id="cancelBtn", elem_classes=["action"])
    

    saved_out = gr.JSON(label="Saved output (example)")

    # Initial render (replaces demo.load)
    # In a tab/module, we trigger it using planner_html's load event.
    planner_html.load(fn=ui_refresh, inputs=state, outputs=[planner_html, week_text])
   

    # Wire buttons 
    prev_btn.click(fn=prev_week, inputs=state, outputs=[planner_html, week_text])
    next_btn.click(fn=next_week, inputs=state, outputs=[planner_html, week_text])

    add_btn.click(fn=add_task, inputs=[state, day_dd, time_dd, task_tb], outputs=[planner_html, week_text])
    cancel_btn.click(fn=cancel_clear, inputs=state, outputs=[planner_html, week_text])
    save_btn.click(fn=save_export_json, inputs=state, outputs=saved_out)
   

    assign_btn = gr.Button("＋ Assign Session to Slot", elem_classes=["action"])
    assign_btn.click(
    fn=assign_session_to_slot,
    inputs=[state, day_dd, time_dd, session_dd],
    outputs=[planner_html, week_text]
)
    view_btn = gr.Button("View Slot Notes", variant="secondary")
    notes_box = gr.Textbox(label="Session Notes", lines=6)
    view_btn.click(
    fn=view_slot_notes,
    inputs=[state, day_dd, time_dd],
    outputs=notes_box
)   
    refresh_sessions_btn.click(
    fn=session_choices,
    inputs=None,
    outputs=session_dd
)








    
    return planner_html, week_text, saved_out

