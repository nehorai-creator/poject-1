import tkinter as tk
from tcp_client import send_request
import os

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# --- הגדרת החלון הראשי ---
root = tk.Tk()
root.title("מערכת אבטחה - הזדהות")
root.geometry("700x950")
root.resizable(False, False)
root.configure(bg="#0a61c7")

# משטח ציור (Canvas) ראשי
canvas = tk.Canvas(root, bg="#0a61c7", highlightthickness=0)
canvas.place(x=0, y=0, width=700, height=950)

# פונקציה לציור מלבן מעוגל מותאם אישית
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, color, tags=None):
    kw = {"fill": color, "outline": color}
    if tags:
        kw["tags"] = tags
    items = [
        canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, **kw),
        canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, **kw),
        canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, **kw),
        canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, **kw),
        canvas.create_rectangle(x1+radius, y1, x2-radius, y2, **kw),
        canvas.create_rectangle(x1, y1+radius, x2, y2-radius, **kw)
    ]
    return items

# --- טעינת תמונת הלוגו (רוחב אחיד של 600 פיקסל) ---
logo_img = None
logo_height = 0
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_0.png")

if os.path.exists(logo_path):
    try:
        if HAS_PIL:
            pil_image = Image.open(logo_path)
            w_percent = 600 / float(pil_image.size[0])
            logo_height = int(float(pil_image.size[1]) * float(w_percent))
            pil_image = pil_image.resize((600, logo_height), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(pil_image)
        else:
            logo_img = tk.PhotoImage(file=logo_path)
            logo_height = logo_img.height()
    except Exception as e:
        print(f"Error loading logo: {e}")

current_mode = "login"
show_password = False
hover_state = None

username_var = tk.StringVar()
password_var = tk.StringVar()
confirm_password_var = tk.StringVar()

# שדות הקלט
username_entry = tk.Entry(root, textvariable=username_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat")
password_entry = tk.Entry(root, textvariable=password_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat", show="*")
confirm_password_entry = tk.Entry(root, textvariable=confirm_password_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat", show="*")

eye_btn1 = None
eye_btn2 = None
eye_slash1 = None
eye_slash2 = None
status_text = None
btn_items = []
link_item = None

current_status_msg = ""
current_status_color = "#ffcccc"

def set_status(msg, color="#ffcccc"):
    global current_status_msg, current_status_color
    current_status_msg = msg
    current_status_color = color
    if status_text:
        canvas.itemconfig(status_text, text=msg, fill=color)

def toggle_password_visibility():
    global show_password
    show_password = not show_password
    char = "" if show_password else "*"
    password_entry.config(show=char)
    confirm_password_entry.config(show=char)
    color = "#1f75de" if show_password else "#777777"
    slash_state = "hidden" if show_password else "normal"

    if eye_btn1:
        canvas.itemconfig(eye_btn1, fill=color)
    if eye_slash1:
        canvas.itemconfig(eye_slash1, state=slash_state)
    if eye_btn2:
        canvas.itemconfig(eye_btn2, fill=color)
    if eye_slash2:
        canvas.itemconfig(eye_slash2, state=slash_state)

def get_current_card_y1():
    top_margin = 15
    return top_margin + logo_height if logo_img else 180

def update_hover_visuals():
    btn_color = "#0a386e" if hover_state == "btn" else "#082a52"
    for item in btn_items:
        canvas.itemconfig(item, fill=btn_color, outline=btn_color)

    link_color = "#b0d4ff" if hover_state == "link" else "#ffffff"
    if link_item:
        canvas.itemconfig(link_item, fill=link_color)

    cursor = "hand2" if hover_state in ("btn", "link", "eye") else ""
    canvas.config(cursor=cursor)

def render_screen():
    global eye_btn1, eye_btn2, eye_slash1, eye_slash2, status_text, btn_items, link_item

    canvas.delete("all")

    char = "" if show_password else "*"
    password_entry.config(show=char)
    confirm_password_entry.config(show=char)
    confirm_password_entry.place_forget()

    cx = 350
    card_y1 = get_current_card_y1()

    # 1. מיקום הלוגו בחלק העליון
    top_margin = 15
    if logo_img:
        logo_center_y = top_margin + (logo_height // 2)
        canvas.create_image(cx, logo_center_y, image=logo_img, anchor="center")

    # כרטיס ראשי (רוחב 600)
    card_x1, card_x2 = 50, 650

    eye_color = "#1f75de" if show_password else "#777777"
    slash_state = "hidden" if show_password else "normal"

    if current_mode == "login":
        card_y2 = 930
        draw_rounded_rect(canvas, card_x1, card_y1, card_x2, card_y2, 22, "#1f75de")
        canvas.create_text(card_x1 + 35, card_y1 + 45, text="Login", fill="white", font=("Arial", 26, "bold"), anchor="w")

        # שם משתמש
        canvas.create_text(card_x1 + 35, card_y1 + 120, text="Username", fill="white", font=("Arial", 11, "bold"), anchor="w")
        draw_rounded_rect(canvas, card_x1 + 35, card_y1 + 145, card_x2 - 35, card_y1 + 187, 6, "white")
        username_entry.place(x=card_x1 + 43, y=card_y1 + 151, width=524, height=30)

        # סיסמה
        canvas.create_text(card_x1 + 35, card_y1 + 225, text="Password", fill="white", font=("Arial", 11, "bold"), anchor="w")
        draw_rounded_rect(canvas, card_x1 + 35, card_y1 + 250, card_x2 - 35, card_y1 + 292, 6, "white")
        password_entry.place(x=card_x1 + 43, y=card_y1 + 256, width=495, height=30)

        # אייקון עין בשדה הסיסמה
        eye_btn1 = canvas.create_text(card_x2 - 55, card_y1 + 271, text="👁", fill=eye_color, font=("Arial", 12), tags="eye_action")
        eye_slash1 = canvas.create_line(card_x2 - 63, card_y1 + 263, card_x2 - 47, card_y1 + 279, fill="#d93025", width=2, state=slash_state, tags="eye_action")
        eye_btn2 = None
        eye_slash2 = None

        # כפתור Sign In
        btn_y1 = card_y1 + 355
        btn_color = "#0a386e" if hover_state == "btn" else "#082a52"
        btn_items = draw_rounded_rect(canvas, card_x1 + 35, btn_y1, card_x2 - 35, btn_y1 + 48, 8, btn_color, tags="submit_action")
        canvas.create_text(cx, btn_y1 + 24, text="Sign in", fill="white", font=("Arial", 14, "bold"), tags="submit_action")

        # הודעת סטטוס
        status_text = canvas.create_text(cx, btn_y1 + 70, text=current_status_msg, fill=current_status_color, font=("Arial", 10, "bold"))

        # מעבר להרשמה
        canvas.create_text(cx, card_y1 + 480, text="Don't have an account?", fill="white", font=("Arial", 10, "normal"))
        link_color = "#b0d4ff" if hover_state == "link" else "#ffffff"
        link_item = canvas.create_text(cx, card_y1 + 510, text="Sign Up", fill=link_color, font=("Arial", 11, "bold"), tags="toggle_action")

    else:
        # כרטיס Sign Up
        card_y2 = 940
        draw_rounded_rect(canvas, card_x1, card_y1, card_x2, card_y2, 22, "#1f75de")
        canvas.create_text(card_x1 + 35, card_y1 + 35, text="Sign Up", fill="white", font=("Arial", 26, "bold"), anchor="w")

        field_x1 = card_x1 + 35
        field_x2 = card_x2 - 35
        field_w = field_x2 - field_x1

        # שם משתמש
        canvas.create_text(field_x1, card_y1 + 95, text="Username", fill="white", font=("Arial", 11, "bold"), anchor="w")
        draw_rounded_rect(canvas, field_x1, card_y1 + 118, field_x2, card_y1 + 158, 6, "white")
        username_entry.place(x=field_x1 + 8, y=card_y1 + 124, width=field_w - 16, height=30)

        # סיסמה
        canvas.create_text(field_x1, card_y1 + 180, text="Password", fill="white", font=("Arial", 11, "bold"), anchor="w")
        draw_rounded_rect(canvas, field_x1, card_y1 + 203, field_x2, card_y1 + 243, 6, "white")
        password_entry.place(x=field_x1 + 8, y=card_y1 + 209, width=field_w - 45, height=30)
        eye_btn1 = canvas.create_text(field_x2 - 22, card_y1 + 223, text="👁", fill=eye_color, font=("Arial", 12), tags="eye_action")
        eye_slash1 = canvas.create_line(field_x2 - 30, card_y1 + 215, field_x2 - 14, card_y1 + 231, fill="#d93025", width=2, state=slash_state, tags="eye_action")

        # אימות סיסמה
        canvas.create_text(field_x1, card_y1 + 265, text="Confirm Password", fill="white", font=("Arial", 11, "bold"), anchor="w")
        draw_rounded_rect(canvas, field_x1, card_y1 + 288, field_x2, card_y1 + 328, 6, "white")
        confirm_password_entry.place(x=field_x1 + 8, y=card_y1 + 294, width=field_w - 45, height=30)
        eye_btn2 = canvas.create_text(field_x2 - 22, card_y1 + 308, text="👁", fill=eye_color, font=("Arial", 12), tags="eye_action")
        eye_slash2 = canvas.create_line(field_x2 - 30, card_y1 + 300, field_x2 - 14, card_y1 + 316, fill="#d93025", width=2, state=slash_state, tags="eye_action")

        # כפתור Register
        btn_y1 = card_y1 + 365
        btn_color = "#0a386e" if hover_state == "btn" else "#082a52"
        btn_items = draw_rounded_rect(canvas, field_x1, btn_y1, field_x2, btn_y1 + 48, 8, btn_color, tags="submit_action")
        canvas.create_text(cx, btn_y1 + 24, text="Register", fill="white", font=("Arial", 14, "bold"), tags="submit_action")

        # הודעת סטטוס
        status_text = canvas.create_text(cx, btn_y1 + 70, text=current_status_msg, fill=current_status_color, font=("Arial", 10, "bold"))

        # מעבר להתחברות
        canvas.create_text(cx, card_y1 + 475, text="Already have an account?", fill="white", font=("Arial", 10, "normal"))
        link_color = "#b0d4ff" if hover_state == "link" else "#ffffff"
        link_item = canvas.create_text(cx, card_y1 + 505, text="Sign In", fill=link_color, font=("Arial", 11, "bold"), tags="toggle_action")

    # חיבור ישיר של אירועי לחיצה לתגיות
    canvas.tag_bind("submit_action", "<Button-1>", lambda e: submit_form())
    canvas.tag_bind("toggle_action", "<Button-1>", lambda e: toggle_mode())
    canvas.tag_bind("eye_action", "<Button-1>", lambda e: toggle_password_visibility())

def submit_form(event=None):
    username = username_var.get().strip()
    password = password_var.get().strip()

    if not username or not password:
        set_status("Please enter username and password", "#ffcccc")
        return

    if current_mode == "signup":
        confirm = confirm_password_var.get().strip()
        if not confirm:
            set_status("Please confirm your password", "#ffcccc")
            return
        if password != confirm:
            set_status("Passwords do not match!", "#ffcccc")
            return

    action = "login" if current_mode == "login" else "register"

    set_status("Connecting to server...", "white")
    root.update()

    try:
        res_data = send_request(action, username, password)
        if not isinstance(res_data, dict):
            set_status("Unexpected server response", "#ffcccc")
            return

        is_success = (
            res_data.get("code") == 200
            or res_data.get("status") in (200, "success")
            or res_data.get("success") is True
        )
        if is_success:
            msg = "Login Successful!" if current_mode == "login" else "Account Created Successfully!"
            set_status(msg, "#88ff88")
        else:
            err_msg = res_data.get("message") or res_data.get("error") or "Operation failed"
            set_status(err_msg, "#ffcccc")
    except (OSError, RuntimeError, ValueError):
        set_status("Cannot connect to server", "#ffcccc")

def toggle_mode():
    global current_mode, show_password
    current_mode = "signup" if current_mode == "login" else "login"
    show_password = False
    username_var.set("")
    password_var.set("")
    confirm_password_var.set("")
    set_status("", "#ffcccc")
    render_screen()

def on_mouse_motion(e):
    global hover_state
    old_state = hover_state
    card_y1 = get_current_card_y1()

    if current_mode == "login":
        if 50 < e.x < 650 and (card_y1 + 355) < e.y < (card_y1 + 403):
            hover_state = "btn"
        elif 290 < e.x < 410 and (card_y1 + 495) < e.y < (card_y1 + 530):
            hover_state = "link"
        elif 570 < e.x < 620 and (card_y1 + 250) < e.y < (card_y1 + 292):
            hover_state = "eye"
        else:
            hover_state = None
    else:
        if 50 < e.x < 650 and (card_y1 + 365) < e.y < (card_y1 + 413):
            hover_state = "btn"
        elif 290 < e.x < 410 and (card_y1 + 490) < e.y < (card_y1 + 525):
            hover_state = "link"
        elif 570 < e.x < 620 and ((card_y1 + 203) < e.y < (card_y1 + 243) or (card_y1 + 288) < e.y < (card_y1 + 328)):
            hover_state = "eye"
        else:
            hover_state = None

    if old_state != hover_state:
        update_hover_visuals()

def on_canvas_click(e):
    card_y1 = get_current_card_y1()
    if current_mode == "login":
        if 570 < e.x < 620 and (card_y1 + 250) < e.y < (card_y1 + 292):
            toggle_password_visibility()
        elif 50 < e.x < 650 and (card_y1 + 355) < e.y < (card_y1 + 403):
            submit_form()
        elif 290 < e.x < 410 and (card_y1 + 495) < e.y < (card_y1 + 530):
            toggle_mode()
    else:
        if 570 < e.x < 620 and ((card_y1 + 203) < e.y < (card_y1 + 243) or (card_y1 + 288) < e.y < (card_y1 + 328)):
            toggle_password_visibility()
        elif 50 < e.x < 650 and (card_y1 + 365) < e.y < (card_y1 + 413):
            submit_form()
        elif 290 < e.x < 410 and (card_y1 + 490) < e.y < (card_y1 + 525):
            toggle_mode()

canvas.bind("<Button-1>", on_canvas_click)
canvas.bind("<Motion>", on_mouse_motion)

username_entry.bind("<Return>", submit_form)
password_entry.bind("<Return>", submit_form)
confirm_password_entry.bind("<Return>", submit_form)
root.bind("<Return>", submit_form)

render_screen()
root.mainloop()
