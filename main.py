import tkinter as tk  # מייבא את ספריית tkinter ליצירת ממשק משתמש גרפי (GUI)
from tcp_client import send_request  # מייבא את פונקציית שליחת בקשות ה-TCP לשרת מתוך tcp_client
import os  # מייבא את ספריית os לעבודה עם נתיבים ומערכת הקבצים
from PIL import Image, ImageTk  # מייבא מתוך ספריית Pillow מחלקות לטעינה, עיבוד והצגת תמונות

# --- הגדרת החלון הראשי ---
root = tk.Tk()  # יוצר את מופע החלון הראשי של האפליקציה
root.title("מערכת אבטחה - הזדהות")  # מגדיר את כותרת החלון המוצגת בסרגל העליון
root.geometry("700x950")  # קובע את מידות החלון ההתחלתיות: רוחב 700 פיקסלים וגובה 950 פיקסלים
root.resizable(False, False)  # נועל את גודל החלון ומונע מהמשתמש לשנות את רוחבו או גובהו
root.configure(bg="#0a61c7")  # קובע את צבע הרקע של החלון לצבע כחול (#0a61c7)

# משטח ציור (Canvas) ראשי
canvas = tk.Canvas(root, bg="#0a61c7", highlightthickness=0)  # יוצר משטח ציור גמיש (Canvas) ללא מסגרת חיצונית
canvas.place(x=0, y=0, width=700, height=950)  # ממקם את משטח הציור בפינה השמאלית-עליונה ומותח אותו על כל שטח החלון

# פונקציה לציור מלבן מעוגל מותאם אישית
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, color):  # מגדיר פונקציה לציור מלבן בעל פינות מעוגלות
    canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, fill=color, outline=color)  # מצייר קשת מעגלית לפינה השמאלית-עליונה
    canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, fill=color, outline=color)  # מצייר קשת מעגלית לפינה הימנית-עליונה
    canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, fill=color, outline=color)  # מצייר קשת מעגלית לפינה השמאלית-תחתונה
    canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, fill=color, outline=color)  # מצייר קשת מעגלית לפינה הימנית-תחתונה
    canvas.create_rectangle(x1+radius, y1, x2-radius, y2, fill=color, outline=color)  # ממלא את החלק המרכזי-אופקי של המלבן
    canvas.create_rectangle(x1, y1+radius, x2, y2-radius, fill=color, outline=color)  # ממלא את החלק המרכזי-אנכי של המלבן

# --- טעינת תמונת הלוגו (רוחב אחיד של 600 פיקסל) ---
logo_img = None  # משתנה לאחסון אובייקט התמונה של Tkinter (מאותחל לריק)
logo_height = 0  # משתנה לאחסון הגובה המחושב של התמונה לאחר התאמת הפרופורציות
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_0.png")  # בונה נתיב מלא לקובץ תמונת הלוגו באותה תיקייה

if os.path.exists(logo_path):  # בודק האם קובץ הלוגו אכן קיים בדיסק
    try:  # פותח בלוק לכידת שגיאות בעת טעינת התמונה
        pil_image = Image.open(logo_path)  # פותח את קובץ התמונה באמצעות ספריית PIL
        # רוחב הלוגו מותאם בדיוק לרוחב הכרטיס (600 פיקסל)
        w_percent = 600 / float(pil_image.size[0])  # מחשב את יחס ההקטנה/הגדלה הנדרש כדי להגיע לרוחב 600 פיקסלים
        logo_height = int(float(pil_image.size[1]) * float(w_percent))  # מחשב את הגובה היחסי המתאים לשמירה על פרופורציות התמונה
        pil_image = pil_image.resize((600, logo_height), Image.Resampling.LANCZOS)  # משנה את גודל התמונה באמצעות אלגוריתם סינון איכותי
        logo_img = ImageTk.PhotoImage(pil_image)  # ממיר את תמונת ה-PIL לאובייקט תמונה תואם Tkinter
    except Exception as e:  # לוכד כל שגיאה שעלולה להתרחש במהלך טעינת התמונה
        print(f"Error loading logo: {e}")  # מדפיס את הודעת השגיאה לקונסול

current_mode = "login"  # משתנה למעקב אחר מצב המסך הנוכחי ("login" להתחברות או "signup" להרשמה)
show_password = False  # משתנה בוליאני הקובע האם הסיסמה תוצג כטקסט גלוי (True) או מוסתרת (False)
hover_state = None  # משתנה למעקב אחר אלמנט שהעכבר מרחף מעליו ("btn", "link" או None)

username_var = tk.StringVar()  # משתנה מיוחד של Tkinter לשמירה ומעקב אחר הטקסט בשדה שם המשתמש
password_var = tk.StringVar()  # משתנה מיוחד של Tkinter לשמירה ומעקב אחר הטקסט בשדה הסיסמה
confirm_password_var = tk.StringVar()  # משתנה מיוחד של Tkinter לשמירה ומעקב אחר הטקסט בשדה אימות הסיסמה

# שדות הקלט עצמם
username_entry = tk.Entry(root, textvariable=username_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat")  # תיבת טקסט להזנת שם משתמש
password_entry = tk.Entry(root, textvariable=password_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat", show="*")  # תיבת טקסט להזנת סיסמה (מוסתרת כברירת מחדל בכוכביות)
confirm_password_entry = tk.Entry(root, textvariable=confirm_password_var, font=("Arial", 12), bd=0, bg="white", fg="#333333", relief="flat", show="*")  # תיבת טקסט לאימות סיסמה במסך הרשמה

eye_btn1 = None  # מזהה Canvas עבור אייקון העין של שדה הסיסמה הראשי
eye_btn2 = None  # מזהה Canvas עבור אייקון העין של שדה אימות הסיסמה
eye_slash1 = None  # מזהה Canvas עבור הקו האלכסוני האדום שחוצה את העין הראשונה
eye_slash2 = None  # מזהה Canvas עבור הקו האלכסוני האדום שחוצה את העין השנייה
status_text = None  # מזהה Canvas עבור טקסט הודעות הסטטוס והמשוב למשתמש

def toggle_password_visibility():  # פונקציה להחלפת מצב תצוגת הסיסמה (גלויה/מוסתרת)
    global show_password  # שימוש במשתנה הגלובלי המייצג את מצב הצגת הסיסמה
    show_password = not show_password  # הופך את הערך: מ-False ל-True או להיפך
    char = "" if show_password else "*"  # מגדיר תו הסתרה: ריק אם הסיסמה גלויה, כוכבית אם היא מוסתרת
    password_entry.config(show=char)  # מעדכן את תו ההסתרה בשדה הסיסמה
    confirm_password_entry.config(show=char)  # מעדכן את תו ההסתרה בשדה אימות הסיסמה
    color = "#1f75de" if show_password else "#777777"  # קובע צבע עין כחול כאשר הסיסמה גלויה ואפור כשהיא מוסתרת
    slash_state = "hidden" if show_password else "normal"  # מסתיר את הקו האדום כשהסיסמה גלויה ומציג אותו כשהיא מוסתרת

    if eye_btn1:  # אם רכיב העין הראשונה קיים במסך
        canvas.itemconfig(eye_btn1, fill=color)  # מעדכן את צבע העין הראשונה
    if eye_slash1:  # אם הקו האדום הראשון קיים במסך
        canvas.itemconfig(eye_slash1, state=slash_state)  # מציג או מסתיר את הקו הראשון
    if eye_btn2:  # אם רכיב העין השנייה קיים במסך
        canvas.itemconfig(eye_btn2, fill=color)  # מעדכן את צבע העין השנייה
    if eye_slash2:  # אם הקו האדום השני קיים במסך
        canvas.itemconfig(eye_slash2, state=slash_state)  # מציג או מסתיר את הקו השני

def render_screen():  # פונקציה המציירת מחדש את כל רכיבי המסך בהתאם למצב הנוכחי
    global eye_btn1, eye_btn2, eye_slash1, eye_slash2, status_text  # גישה למזהי הרכיבים הגלובליים על ה-Canvas
    
    canvas.delete("all")  # מוחק את כל הרכיבים הגרפיים הקיימים על משטח הציור

    global show_password  # גישה למשתנה הגלובלי של הצגת הסיסמה
    show_password = False  # מחזיר את מצב הסיסמה להסתרה כברירת מחדל בעת טעינת מסך מחדש
    password_entry.config(show="*")  # מגדיר מחדש תו כוכבית לשדה הסיסמה
    confirm_password_entry.config(show="*")  # מגדיר מחדש תו כוכבית לשדה אימות הסיסמה
    confirm_password_entry.place_forget()  # מסיר את שדה אימות הסיסמה מהתצוגה (יוחזר רק במצב הרשמה)

    cx = 350  # קובע את נקודת המרכז האופקית של החלון (רוחב 700 חלקי 2)

    # --- 1. מיקום הלוגו בחלק העליון ---
    top_margin = 15  # מרווח עליון בפיקסלים מתחילת החלון
    if logo_img:  # אם תמונת הלוגו נטענה בהצלחה
        logo_center_y = top_margin + (logo_height // 2)  # מחשב את נקודת המרכז האנכית של הלוגו
        canvas.create_image(cx, logo_center_y, image=logo_img, anchor="center")  # מצייר את תמונת הלוגו ממורכזת בחלק העליון
        # נקודת הסיום המדויקת של הלוגו למטה
        card_y1 = top_margin + logo_height  # קובע את גובה ההתחלה של כרטיס הטופס בצמוד לסיום הלוגו
    else:  # אם אין תמונת לוגו זמינה
        card_y1 = 180  # משתמש במיקום ברירת מחדל של 180 פיקסלים מלמעלה

    # רוחב אחיד לכרטיס (מ-50 עד 650 = רוחב 600)
    card_x1, card_x2 = 50, 650  # קובע את הגבול השמאלי (50) והימני (650) של כרטיס הטופס

    if current_mode == "login":  # בדיקה האם המסך הנוכחי הוא מסך התחברות
        card_y2 = 930  # קובע את הגבול התחתון של כרטיס ההתחברות
        draw_rounded_rect(canvas, card_x1, card_y1, card_x2, card_y2, 22, "#1f75de")  # מצייר את הרקע הכחול המעוגל של כרטיס ההתחברות
        canvas.create_text(card_x1 + 35, card_y1 + 45, text="Login", fill="white", font=("Arial", 26, "bold"), anchor="w")  # מצייר את כותרת הכרטיס "Login"

        # שם משתמש
        canvas.create_text(card_x1 + 35, card_y1 + 120, text="Username", fill="white", font=("Arial", 11, "bold"), anchor="w")  # מצייר תווית טקסט "Username"
        draw_rounded_rect(canvas, card_x1 + 35, card_y1 + 145, card_x2 - 35, card_y1 + 187, 6, "white")  # מצייר רקע לבן ומעוגל לשדה שם המשתמש
        username_entry.place(x=card_x1 + 43, y=card_y1 + 151, width=524, height=30)  # ממקם את תיבת הטקסט להזנת שם המשתמש על גבי הרקע הלבן

        # סיסמה
        canvas.create_text(card_x1 + 35, card_y1 + 225, text="Password", fill="white", font=("Arial", 11, "bold"), anchor="w")  # מצייר תווית טקסט "Password"
        draw_rounded_rect(canvas, card_x1 + 35, card_y1 + 250, card_x2 - 35, card_y1 + 292, 6, "white")  # מצייר רקע לבן ומעוגל לשדה הסיסמה
        password_entry.place(x=card_x1 + 43, y=card_y1 + 256, width=495, height=30)  # ממקם את תיבת הטקסט להזנת הסיסמה על גבי הרקע הלבן

        # אייקון עין בשדה הסיסמה
        eye_btn1 = canvas.create_text(card_x2 - 55, card_y1 + 271, text="👁", fill="#777777", font=("Arial", 12))  # מצייר את אייקון העין להצגת/הסתרת סיסמה
        eye_slash1 = canvas.create_line(card_x2 - 63, card_y1 + 263, card_x2 - 47, card_y1 + 279, fill="#d93025", width=2, state="normal")  # מצייר קו אלכסוני אדום מעל העין
        eye_btn2 = None  # מאפס את מזהה העין השנייה (אינו פעיל במסך התחברות)
        eye_slash2 = None  # מאפס את מזהה הקו השני (אינו פעיל במסך התחברות)

        # כפתור Sign In
        btn_y1 = card_y1 + 355  # קובע את המיקום האנכי העליון של כפתור ההתחברות
        btn_color = "#0a386e" if hover_state == "btn" else "#082a52"  # משנה את גוון הכפתור בהתאם למצב ריחוף העכבר (אפקט Hover)
        draw_rounded_rect(canvas, card_x1 + 35, btn_y1, card_x2 - 35, btn_y1 + 48, 8, btn_color)  # מצייר את המלבן המעוגל של הכפתור
        canvas.create_text(cx, btn_y1 + 24, text="Sign in", fill="white", font=("Arial", 14, "bold"))  # מצייר את הטקסט "Sign in" במרכז הכפתור

        # הודעת סטטוס
        status_text = canvas.create_text(cx, btn_y1 + 70, text="", fill="#ffcccc", font=("Arial", 10, "bold"))  # יוצר אלמנט טקסט להצגת הודעות שגיאה או הצלחה למשתמש

        # מעבר להרשמה
        canvas.create_text(cx, card_y1 + 480, text="Don't have an account?", fill="white", font=("Arial", 10, "normal"))  # מצייר את השאלה המזמינה להירשם
        link_color = "#ffffff" if hover_state != "link" else "#b0d4ff"  # משנה את צבע קישור ההרשמה בעת ריחוף עכבר מעליו
        canvas.create_text(cx, card_y1 + 510, text="Sign Up", fill=link_color, font=("Arial", 11, "bold"))  # מצייר את הקישור הלחיץ "Sign Up"

    else:  # אם המצב הוא הרשמה ("signup")
        # --- כרטיס Sign Up ---
        card_y2 = 940  # קובע את הגבול התחתון של כרטיס ההרשמה (מעט מוגדל עבור שדה נוסף)
        draw_rounded_rect(canvas, card_x1, card_y1, card_x2, card_y2, 22, "#1f75de")  # מצייר את הרקע הכחול המעוגל של כרטיס ההרשמה
        canvas.create_text(card_x1 + 35, card_y1 + 35, text="Sign Up", fill="white", font=("Arial", 26, "bold"), anchor="w")  # מצייר את כותרת הכרטיס "Sign Up"

        field_x1 = card_x1 + 35  # קובע את הגבול השמאלי עבור שדות הקלט בכרטיס ההרשמה
        field_x2 = card_x2 - 35  # קובע את הגבול הימני עבור שדות הקלט בכרטיס ההרשמה
        field_w = field_x2 - field_x1  # מחשב את הרוחב הכולל של שדה קלט

        canvas.create_text(field_x1, card_y1 + 95, text="Username", fill="white", font=("Arial", 11, "bold"), anchor="w")  # מצייר תווית "Username"
        draw_rounded_rect(canvas, field_x1, card_y1 + 118, field_x2, card_y1 + 158, 6, "white")  # מצייר רקע לבן לשדה שם המשתמש
        username_entry.place(x=field_x1 + 8, y=card_y1 + 124, width=field_w - 16, height=30)  # ממקם את שדה שם המשתמש

        canvas.create_text(field_x1, card_y1 + 180, text="Password", fill="white", font=("Arial", 11, "bold"), anchor="w")  # מצייר תווית "Password"
        draw_rounded_rect(canvas, field_x1, card_y1 + 203, field_x2, card_y1 + 243, 6, "white")  # מצייר רקע לבן לשדה הסיסמה
        password_entry.place(x=field_x1 + 8, y=card_y1 + 209, width=field_w - 45, height=30)  # ממקם את שדה הסיסמה (מותיר מקום בצד לאייקון העין)
        eye_btn1 = canvas.create_text(field_x2 - 22, card_y1 + 223, text="👁", fill="#777777", font=("Arial", 12))  # מצייר את אייקון העין לשדה הסיסמה
        eye_slash1 = canvas.create_line(field_x2 - 30, card_y1 + 215, field_x2 - 14, card_y1 + 231, fill="#d93025", width=2, state="normal")  # מצייר קו אדום מעל העין הראשונה

        canvas.create_text(field_x1, card_y1 + 265, text="Confirm Password", fill="white", font=("Arial", 11, "bold"), anchor="w")  # מצייר תווית "Confirm Password"
        draw_rounded_rect(canvas, field_x1, card_y1 + 288, field_x2, card_y1 + 328, 6, "white")  # מצייר רקע לבן לשדה אימות הסיסמה
        confirm_password_entry.place(x=field_x1 + 8, y=card_y1 + 294, width=field_w - 45, height=30)  # ממקם את שדה אימות הסיסמה
        eye_btn2 = canvas.create_text(field_x2 - 22, card_y1 + 308, text="👁", fill="#777777", font=("Arial", 12))  # מצייר את אייקון העין לשדה אימות הסיסמה
        eye_slash2 = canvas.create_line(field_x2 - 30, card_y1 + 300, field_x2 - 14, card_y1 + 316, fill="#d93025", width=2, state="normal")  # מצייר קו אדום מעל העין השנייה

        btn_y1 = card_y1 + 365  # קובע את המיקום האנכי העליון של כפתור ההרשמה
        btn_color = "#0a386e" if hover_state == "btn" else "#082a52"  # משנה את גוון הכפתור בעת ריחוף עכבר
        draw_rounded_rect(canvas, field_x1, btn_y1, field_x2, btn_y1 + 48, 8, btn_color)  # מצייר את הרקע המעוגל של כפתור ההרשמה
        canvas.create_text(cx, btn_y1 + 24, text="Register", fill="white", font=("Arial", 14, "bold"))  # מצייר את הכיתוב "Register" במרכז הכפתור

        status_text = canvas.create_text(cx, btn_y1 + 70, text="", fill="#ffcccc", font=("Arial", 10, "bold"))  # יוצר אלמנט להודעות סטטוס במסך הרשמה

        canvas.create_text(cx, card_y1 + 475, text="Already have an account?", fill="white", font=("Arial", 10, "normal"))  # מצייר את השאלה המזמינה להתחבר
        link_color = "#ffffff" if hover_state != "link" else "#b0d4ff"  # קובע צבע עבור קישור החזרה להתחברות בעת ריחוף
        canvas.create_text(cx, card_y1 + 505, text="Sign In", fill=link_color, font=("Arial", 11, "bold"))  # מצייר את הקישור הלחיץ "Sign In"

def submit_form(event=None):  # פונקציה לבדיקת תקינות הקלט ושליחת הטופס לשרת
    username = username_var.get().strip()  # שולף את שם המשתמש שהוקלד ומסיר רווחים מיותרים מהקצוות
    password = password_var.get().strip()  # שולף את הסיסמה שהוקלדה ומסיר רווחים מיותרים מהקצוות

    if not username or not password:  # בודק האם אחד מהשדות (שם משתמש או סיסמה) נשאר ריק
        canvas.itemconfig(status_text, text="Please enter username and password", fill="#ffcccc")  # מציג הודעת שגיאה באדום בהיר
        return  # עוצר את ביצוע הפונקציה

    if current_mode == "signup":  # בדיקות נוספות הייחודיות למצב הרשמה
        confirm = confirm_password_var.get().strip()  # שולף את טקסט אימות הסיסמה ומנקה רווחים
        if not confirm:  # בודק האם שדה אימות הסיסמה ריק
            canvas.itemconfig(status_text, text="Please confirm your password", fill="#ffcccc")  # מציג הודעת שגיאה לדרוש אימות סיסמה
            return  # עוצר את ביצוע הפונקציה
        if password != confirm:  # בודק האם הסיסמה ואימות הסיסמה אינם תואמים
            canvas.itemconfig(status_text, text="Passwords do not match!", fill="#ffcccc")  # מציג הודעת שגיאה שהסיסמאות אינן תואמות
            return  # עוצר את ביצוע הפונקציה

    action = "login" if current_mode == "login" else "register"  # קובע את סוג הפעולה לשליחה לשרת ("login" או "register")

    try:  # מנסה לעדכן את הודעת הסטטוס
        canvas.itemconfig(status_text, text="Connecting to server...", fill="white")  # מציג הודעה שההתחברות לשרת מתבצעת כעת
    except Exception:  # מונע קריסה במקרה שהאלמנט הגרפי טרם נוצר במלואו
        pass  # מתעלם וממשיך
    root.update()  # מעדכן מיידית את החלון הגרפי כדי שהמשתמש יראה את הודעת ההתחברות

    try:  # פותח בלוק לתקשורת מול שרת ה-TCP
        res_data = send_request(action, username, password)  # שולח בקשת TCP לשרת וממתין לתשובת JSON
        if res_data.get("code") == 200:  # בודק האם קוד התגובה מהשרת מציין הצלחה (קוד 200)
            msg = "Login Successful!" if current_mode == "login" else "Account Created Successfully!"  # מנסח הודעת הצלחה מתאימה
            canvas.itemconfig(status_text, text=msg, fill="#88ff88")  # מציג את הודעת ההצלחה בצבע ירוק בהיר
        else:  # אם השרת החזיר קוד שגיאה (למשל פרטים שגויים או משתמש קיים)
            canvas.itemconfig(status_text, text=res_data.get("message", "Error"), fill="#ffcccc")  # מציג את הודעת השגיאה מהשרת באדום
    except (OSError, RuntimeError, ValueError):  # לוכד שגיאות תקשורת או קריסה ברמת הרשת (למשל כשהשרת סגור)
        canvas.itemconfig(status_text, text="Cannot connect to server", fill="#ffcccc")  # מציג הודעה שלא ניתן להתחבר לשרת

def toggle_mode():  # פונקציה להחלפה בין מצב התחברות למצב הרשמה
    global current_mode  # גישה למשתנה המצב הגלובלי
    current_mode = "signup" if current_mode == "login" else "login"  # הופך את המצב הנוכחי ("login" הופך ל-"signup" ולהיפך)
    username_var.set("")  # מנקה את תוכן שדה שם המשתמש
    password_var.set("")  # מנקה את תוכן שדה הסיסמה
    confirm_password_var.set("")  # מנקה את תוכן שדה אימות הסיסמה
    render_screen()  # קורא לציור מחדש של המסך בהתאם למצב החדש

def get_current_card_y1():  # פונקציית עזר לחישוב נקודת ההתחלה האנכית של כרטיס הטופס
    top_margin = 15  # גודל המרווח העליון
    return top_margin + logo_height if logo_img else 180  # מחזיר מיקום מתחת ללוגו, או 180 אם אין לוגו

def on_mouse_motion(e):  # פונקציה המופעלת בעת תנועת עכבר על גבי ה-Canvas (לטיפול באפקטי ריחוף)
    global hover_state  # גישה למשתנה הגלובלי של מצב הריחוף
    old_state = hover_state  # שומר את מצב הריחוף הקודם כדי לבדוק האם חל שינוי
    card_y1 = get_current_card_y1()  # מקבל את גובה תחילת הכרטיס
    
    if current_mode == "login":  # בדיקת ריחוף עבור מסך התחברות
        if 50 < e.x < 650 and (card_y1 + 355) < e.y < (card_y1 + 403):  # בודק האם סמן העכבר נמצא בתוך גבולות כפתור Sign In
            hover_state = "btn"  # מסמן שהעכבר מרחף מעל הכפתור
        elif 290 < e.x < 410 and (card_y1 + 495) < e.y < (card_y1 + 530):  # בודק האם סמן העכבר נמצא מעל קישור Sign Up
            hover_state = "link"  # מסמן שהעכבר מרחף מעל הקישור
        else:  # אם העכבר בכל מקום אחר
            hover_state = None  # מאפס את מצב הריחוף
    else:  # בדיקת ריחוף עבור מסך הרשמה
        if 50 < e.x < 650 and (card_y1 + 365) < e.y < (card_y1 + 413):  # בודק האם סמן העכבר נמצא בתוך כפתור Register
            hover_state = "btn"  # מסמן שהעכבר מרחף מעל הכפתור
        elif 290 < e.x < 410 and (card_y1 + 490) < e.y < (card_y1 + 525):  # בודק האם סמן העכבר נמצא מעל קישור Sign In
            hover_state = "link"  # מסמן שהעכבר מרחף מעל הקישור
        else:  # אם העכבר בכל מקום אחר
            hover_state = None  # מאפס את מצב הריחוף
            
    if old_state != hover_state:  # בודק האם מצב הריחוף השתנה בהשוואה לפריים הקודם
        render_screen()  # מצייר מחדש את המסך כדי לעדכן את צבעי הכפתור או הקישור

def on_canvas_click(e):  # פונקציה המופעלת בכל לחיצת עכבר על משטח הציור
    card_y1 = get_current_card_y1()  # מקבל את גובה תחילת הכרטיס
    if current_mode == "login":  # טיפול בלחיצות במסך התחברות
        if 595 < e.x < 630 and (card_y1 + 250) < e.y < (card_y1 + 292):  # בודק האם הלחיצה בוצעה על תחום אייקון העין
            toggle_password_visibility()  # משנה את מצב הצגת/הסתרת הסיסמה
        elif 50 < e.x < 650 and (card_y1 + 355) < e.y < (card_y1 + 403):  # בודק האם הלחיצה בוצעה על כפתור Sign in
            submit_form()  # מפעיל את שליחת טופס ההתחברות
        elif 290 < e.x < 410 and (card_y1 + 495) < e.y < (card_y1 + 530):  # בודק האם הלחיצה בוצעה על קישור Sign Up
            toggle_mode()  # עובר למסך הרשמה
    else:  # טיפול בלחיצות במסך הרשמה
        if 610 < e.x < 645 and ((card_y1 + 203) < e.y < (card_y1 + 243) or (card_y1 + 288) < e.y < (card_y1 + 328)):  # בודק האם נלחצה אחת משתי העיניים
            toggle_password_visibility()  # משנה את מצב הצגת/הסתרת הסיסמה
        elif 50 < e.x < 650 and (card_y1 + 365) < e.y < (card_y1 + 413):  # בודק האם הלחיצה בוצעה על כפתור Register
            submit_form()  # מפעיל את שליחת טופס ההרשמה
        elif 290 < e.x < 410 and (card_y1 + 490) < e.y < (card_y1 + 525):  # בודק האם הלחיצה בוצעה על קישור Sign In
            toggle_mode()  # עובר למסך התחברות

canvas.bind("<Button-1>", on_canvas_click)  # מחבר את אירוע לחיצת העכבר השמאלית (Button-1) לפונקציה on_canvas_click
canvas.bind("<Motion>", on_mouse_motion)  # מחבר את אירוע תנועת העכבר (Motion) לפונקציה on_mouse_motion

username_entry.bind("<Return>", submit_form)  # מחבר לחיצה על מקש Enter בשדה שם המשתמש לשליחת הטופס
password_entry.bind("<Return>", submit_form)  # מחבר לחיצה על מקש Enter בשדה הסיסמה לשליחת הטופס
confirm_password_entry.bind("<Return>", submit_form)  # מחבר לחיצה על מקש Enter בשדה אימות הסיסמה לשליחת הטופס

render_screen()  # קורא לרינדור הראשוני של המסך בעת עליית התוכנית
root.mainloop()  # מפעיל את לולאת האירועים האינסופית של Tkinter המשאירה את החלון פתוח ומגיבה למשתמש
