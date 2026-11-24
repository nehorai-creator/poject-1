import os
import customtkinter as ctk
from tcp_client import send_request

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# פלטת צבעים אחידה למסך ההזדהות וללוח הבקרה
BG_OBSIDIAN = "#090d16"
PANEL_DARK = "#101726"
CARD_BG = "#131c2e"
CARD_HOVER = "#18243b"
INPUT_BG = "#0c1322"
BORDER_SUBTLE = "#22314d"
BORDER_GLOW = "#38bdf8"
CYAN_ACCENT = "#38bdf8"
BLUE_ACCENT = "#2563eb"
EMERALD = "#10b981"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"


class CyberVaultDashboardGUI(ctk.CTkToplevel):
    def __init__(self, master, on_logout, username="מנהל", role="מנהל מערכת"):
        super().__init__(master)
        self.on_logout = on_logout
        self.username = username
        self.role = role

        self.title("ENC SECURE CAM — Command & Encrypted Vault")
        self.geometry("1040x700")
        self.resizable(False, False)
        self.configure(fg_color=BG_OBSIDIAN)
        self.protocol("WM_DELETE_WINDOW", self.handle_logout)
        self.setup_ui()

    def setup_ui(self):
        # --- 1. סרגל עליון ---
        top_bar = ctk.CTkFrame(
            self, fg_color=PANEL_DARK, height=74,
            corner_radius=0, border_width=1, border_color=BORDER_SUBTLE
        )
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        left_group = ctk.CTkFrame(top_bar, fg_color="transparent")
        left_group.pack(side="left", padx=24)

        brand_mark = ctk.CTkLabel(
            left_group, text="◈", font=("Segoe UI", 22, "bold"),
            text_color=CYAN_ACCENT, fg_color="#0c253b",
            width=42, height=42, corner_radius=10
        )
        brand_mark.pack(side="left", padx=(0, 12))

        brand_titles = ctk.CTkFrame(left_group, fg_color="transparent")
        brand_titles.pack(side="left")

        ctk.CTkLabel(
            brand_titles, text="ENC SECURE CAM",
            font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_titles, text="ENCRYPTED SURVEILLANCE & ACCESS CONTROL",
            font=("Segoe UI", 10, "bold"), text_color=CYAN_ACCENT
        ).pack(anchor="w")

        status_pill = ctk.CTkFrame(
            top_bar, fg_color="#072923", corner_radius=20,
            border_width=1, border_color="#065f46"
        )
        status_pill.pack(side="left", padx=12)

        ctk.CTkLabel(
            status_pill, text="●  הצפנה פעילה  |  מצב מאובטח",
            font=("Segoe UI", 11, "bold"), text_color=EMERALD
        ).pack(padx=14, pady=5)

        right_group = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_group.pack(side="right", padx=24)

        logout_btn = ctk.CTkButton(
            right_group, text="התנתקות  ↪", width=114, height=36,
            corner_radius=10, fg_color="#2a1219", hover_color="#3f1722",
            border_width=1, border_color="#7f1d1d",
            text_color="#fda4af", font=("Segoe UI", 12, "bold"),
            command=self.handle_logout
        )
        logout_btn.pack(side="right", padx=(14, 0))

        profile_chip = ctk.CTkFrame(
            right_group, fg_color=CARD_BG, corner_radius=10,
            border_width=1, border_color=BORDER_SUBTLE
        )
        profile_chip.pack(side="right")

        ctk.CTkLabel(
            profile_chip,
            text=f"👤  {self.username}   •   {self.role}",
            font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY
        ).pack(padx=14, pady=7)

        # --- 2. סרגל ניווט תחתון ---
        bottom_bar = ctk.CTkFrame(
            self, fg_color=PANEL_DARK, height=62,
            corner_radius=0, border_width=1, border_color=BORDER_SUBTLE
        )
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)

        nav_box = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        nav_box.pack(expand=True)

        nav_items = [
            ("👤  פרופיל", False),
            ("🔔  התראות", False),
            ("⚙️  הגדרות", False),
            ("🏠  בית", True)
        ]

        for label, is_active in nav_items:
            btn = ctk.CTkButton(
                nav_box, text=label, width=145, height=40,
                corner_radius=10,
                fg_color="#132b47" if is_active else "transparent",
                hover_color="#173456" if is_active else "#182235",
                border_width=1 if is_active else 0,
                border_color="#1d4ed8" if is_active else PANEL_DARK,
                text_color=CYAN_ACCENT if is_active else TEXT_SECONDARY,
                font=("Segoe UI", 13, "bold" if is_active else "normal"),
                command=lambda name=label: self.on_click(f"Tab: {name.strip()}")
            )
            btn.pack(side="left", padx=10)

        # --- 3. אזור מרכזי ---
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=28, pady=20)

        hero_banner = ctk.CTkFrame(
            workspace, fg_color=PANEL_DARK, corner_radius=16,
            border_width=1, border_color=BORDER_SUBTLE
        )
        hero_banner.pack(fill="x", pady=(0, 16))

        hero_inner = ctk.CTkFrame(hero_banner, fg_color="transparent")
        hero_inner.pack(fill="x", padx=22, pady=14)

        ctk.CTkLabel(
            hero_inner, text="לוח בקרה ראשי — ניהול מערכת צילום מאובטחת",
            font=("Segoe UI", 19, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="right")

        ctk.CTkLabel(
            hero_inner, text="סינון צילומים, תפעול מצלמה, יומן פעילות וגישה לקבצים מוצפנים",
            font=("Segoe UI", 12), text_color=TEXT_SECONDARY
        ).pack(side="left")

        grid = ctk.CTkFrame(workspace, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        grid.columnconfigure(0, weight=1, uniform="c")
        grid.columnconfigure(1, weight=1, uniform="c")
        grid.rowconfigure(0, weight=1, uniform="r")
        grid.rowconfigure(1, weight=1, uniform="r")

        cards_config = [
            (
                0, 0, "01", "🔍",
                "חיפוש וסינון מתקדם",
                "Advanced Search & Filter",
                "איתור מהיר של הקלטות ואירועים לפי טווח תאריכים, שעות ופרמטרים מותאמים.",
                "סינון לפי תאריך ושעה",
                "Search & Filter"
            ),
            (
                0, 1, "02", "📹",
                "פעולות מצלמה",
                "Camera Operations",
                "שליטה שוטפת במצלמה, בדיקת תקשורת מול השרת והפעלה או עצירה של צילום והקלטה.",
                "תפעול וחיבור שרת",
                "Camera Operations"
            ),
            (
                1, 0, "03", "🛡️",
                "יומן אבטחה מוגן",
                "Security Logs",
                "תיעוד מפורט ומוגן של התחברויות, פעולות משתמשים ואירועי גישה במערכת.",
                "מעקב פעילות והרשאות",
                "Security Logs"
            ),
            (
                1, 1, "04", "🔐",
                "צילומים מוצפנים",
                "Encrypted Recordings",
                "צפייה וניהול מבוקרים של קובצי וידאו השמורים בהצפנה ופתיחתם למשתמשים מורשים.",
                "גישה לכספת המוצפנת",
                "Encrypted Recordings"
            )
        ]

        for r, c, num, icon, title_he, title_en, desc, tag, action in cards_config:
            self.create_vault_card(grid, r, c, num, icon, title_he, title_en, desc, tag, action)

    def create_vault_card(self, parent, row, col, num, icon, title_he, title_en, desc, tag, action_name):
        card = ctk.CTkFrame(
            parent, fg_color=CARD_BG, corner_radius=18,
            border_width=1.5, border_color=BORDER_SUBTLE, cursor="hand2"
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        top_accent = ctk.CTkFrame(card, fg_color="#1e3a5f", height=4, corner_radius=2)
        top_accent.pack(fill="x", padx=18, pady=(14, 0))

        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=20, pady=(12, 6))

        right_title = ctk.CTkFrame(header_row, fg_color="transparent")
        right_title.pack(side="right")

        icon_holder = ctk.CTkLabel(
            header_row, text=icon, font=("Segoe UI", 24),
            fg_color="#0f243d", text_color=CYAN_ACCENT,
            width=48, height=48, corner_radius=12
        )
        icon_holder.pack(side="right", padx=(12, 0))

        ctk.CTkLabel(
            right_title, text=title_he,
            font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="e")

        ctk.CTkLabel(
            right_title, text=title_en,
            font=("Segoe UI", 11, "bold"), text_color=CYAN_ACCENT
        ).pack(anchor="e")

        num_lbl = ctk.CTkLabel(
            header_row, text=f"MOD // {num}",
            font=("Consolas", 11, "bold"), text_color=TEXT_SECONDARY
        )
        num_lbl.pack(side="left", anchor="n")

        desc_lbl = ctk.CTkLabel(
            card, text=desc, font=("Segoe UI", 12),
            text_color=TEXT_SECONDARY, justify="right", wraplength=410
        )
        desc_lbl.pack(anchor="e", padx=20, pady=(6, 12))

        footer_row = ctk.CTkFrame(card, fg_color="transparent")
        footer_row.pack(fill="x", side="bottom", padx=20, pady=(0, 16))

        tag_lbl = ctk.CTkLabel(
            footer_row, text=tag, font=("Segoe UI", 11, "bold"),
            text_color="#93c5fd", fg_color="#102542",
            corner_radius=8, padx=10, pady=4
        )
        tag_lbl.pack(side="right")

        enter_lbl = ctk.CTkLabel(
            footer_row, text="← כניסה למודול",
            font=("Segoe UI", 12, "bold"), text_color=CYAN_ACCENT
        )
        enter_lbl.pack(side="left")

        def on_enter(_):
            card.configure(fg_color=CARD_HOVER, border_color=BORDER_GLOW)
            top_accent.configure(fg_color=CYAN_ACCENT)
            enter_lbl.configure(text_color="#ffffff")

        def on_leave(_):
            card.configure(fg_color=CARD_BG, border_color=BORDER_SUBTLE)
            top_accent.configure(fg_color="#1e3a5f")
            enter_lbl.configure(text_color=CYAN_ACCENT)

        def on_press(_):
            self.on_click(action_name)

        widgets = [
            card, top_accent, header_row, right_title, icon_holder,
            num_lbl, desc_lbl, footer_row, tag_lbl, enter_lbl
        ]
        for child in right_title.winfo_children():
            widgets.append(child)

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_press)

    def on_click(self, name):
        print(f"[Cyber Vault UI] נלחץ: {name} | משתמש: {self.username} ({self.role})")

    def handle_logout(self):
        self.destroy()
        if callable(self.on_logout):
            self.on_logout()


class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ENC SECURE CAM — הזדהות מאובטחת")
        self.geometry("620x740")
        self.resizable(False, False)
        self.configure(fg_color=BG_OBSIDIAN)

        self.current_mode = "login"
        self.show_password = False
        self.dashboard_win = None

        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.confirm_password_var = ctk.StringVar()

        self.logo_ctk_img = self._load_logo()

        self._build_top_bar()
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=44, pady=24)

        self.bind("<Return>", self.submit_form)
        self.render_auth_card()

    def _load_logo(self):
        if not HAS_PIL:
            return None
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_0.png")
        if not os.path.exists(logo_path):
            return None
        try:
            pil_img = Image.open(logo_path)
            target_w = 190
            ratio = target_w / float(pil_img.size[0])
            target_h = max(36, min(72, int(float(pil_img.size[1]) * ratio)))
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_w, target_h))
        except Exception as e:
            print(f"Error loading logo: {e}")
            return None

    def _build_top_bar(self):
        top_bar = ctk.CTkFrame(
            self, fg_color=PANEL_DARK, height=68,
            corner_radius=0, border_width=1, border_color=BORDER_SUBTLE
        )
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        brand = ctk.CTkFrame(top_bar, fg_color="transparent")
        brand.pack(side="left", padx=22)

        ctk.CTkLabel(
            brand, text="◈", font=("Segoe UI", 20, "bold"),
            text_color=CYAN_ACCENT, fg_color="#0c253b",
            width=38, height=38, corner_radius=10
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            brand, text="ENC SECURE CAM",
            font=("Segoe UI", 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left")

        status_pill = ctk.CTkFrame(
            top_bar, fg_color="#072923", corner_radius=20,
            border_width=1, border_color="#065f46"
        )
        status_pill.pack(side="right", padx=22)

        ctk.CTkLabel(
            status_pill, text="●  הצפנה פעילה",
            font=("Segoe UI", 11, "bold"), text_color=EMERALD
        ).pack(padx=12, pady=4)

    def set_status(self, msg, color="#fda4af"):
        if hasattr(self, "status_label") and self.status_label.winfo_exists():
            self.status_label.configure(text=msg, text_color=color)

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        show_char = "" if self.show_password else "*"
        self.password_entry.configure(show=show_char)
        if hasattr(self, "confirm_entry") and self.confirm_entry.winfo_exists():
            self.confirm_entry.configure(show=show_char)

        eye_text = "🙈" if self.show_password else "👁"
        eye_color = CYAN_ACCENT if self.show_password else TEXT_SECONDARY
        for btn in getattr(self, "eye_buttons", []):
            if btn.winfo_exists():
                btn.configure(text=eye_text, text_color=eye_color)

    def render_auth_card(self):
        for child in self.main_container.winfo_children():
            child.destroy()
        self.eye_buttons = []

        is_login = self.current_mode == "login"

        card = ctk.CTkFrame(
            self.main_container, fg_color=CARD_BG, corner_radius=20,
            border_width=1.5, border_color=BORDER_SUBTLE
        )
        card.pack(fill="both", expand=True)

        # פס הדגשה עליון כמו בכרטיסי ה-Vault
        top_accent = ctk.CTkFrame(card, fg_color=CYAN_ACCENT, height=4, corner_radius=2)
        top_accent.pack(fill="x", padx=24, pady=(16, 0))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=34, pady=(14, 24))

        # לוגו מותאם אישית אם קיים
        if self.logo_ctk_img:
            ctk.CTkLabel(inner, image=self.logo_ctk_img, text="").pack(pady=(0, 6))

        # כותרת + תגית מצב
        header_row = ctk.CTkFrame(inner, fg_color="transparent")
        header_row.pack(fill="x", pady=(2, 4))

        ctk.CTkLabel(
            header_row,
            text="התחברות למערכת" if is_login else "יצירת חשבון חדש",
            font=("Segoe UI", 22, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="right")

        ctk.CTkLabel(
            header_row,
            text="AUTH // LOGIN" if is_login else "AUTH // REGISTER",
            font=("Consolas", 11, "bold"), text_color=CYAN_ACCENT,
            fg_color="#0f243d", corner_radius=8, padx=10, pady=4
        ).pack(side="left")

        ctk.CTkLabel(
            inner,
            text=(
                "הזן פרטי משתמש לגישה לכספת הצילומים המוצפנים וללוח הבקרה"
                if is_login else
                "הרשם למערכת כדי לקבל גישה מאובטחת בהתאם להרשאות החשבון"
            ),
            font=("Segoe UI", 12), text_color=TEXT_SECONDARY, anchor="e"
        ).pack(fill="x", pady=(0, 14))

        # --- שדה שם משתמש ---
        ctk.CTkLabel(
            inner, text="שם משתמש (Username)",
            font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY, anchor="e"
        ).pack(fill="x", pady=(0, 5))

        self.username_entry = ctk.CTkEntry(
            inner, textvariable=self.username_var, height=42, corner_radius=10,
            fg_color=INPUT_BG, border_width=1.5, border_color=BORDER_SUBTLE,
            text_color=TEXT_PRIMARY, placeholder_text="הזן שם משתמש...",
            placeholder_text_color="#64748b", font=("Segoe UI", 13)
        )
        self.username_entry.pack(fill="x", pady=(0, 12))
        self.username_entry.bind("<Return>", self.submit_form)

        # --- שדה סיסמה ---
        ctk.CTkLabel(
            inner, text="סיסמה (Password)",
            font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY, anchor="e"
        ).pack(fill="x", pady=(0, 5))

        pw_row = ctk.CTkFrame(inner, fg_color="transparent")
        pw_row.pack(fill="x", pady=(0, 12))

        show_char = "" if self.show_password else "*"
        self.password_entry = ctk.CTkEntry(
            pw_row, textvariable=self.password_var, height=42, corner_radius=10,
            fg_color=INPUT_BG, border_width=1.5, border_color=BORDER_SUBTLE,
            text_color=TEXT_PRIMARY, show=show_char, placeholder_text="הזן סיסמה...",
            placeholder_text_color="#64748b", font=("Segoe UI", 13)
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.password_entry.bind("<Return>", self.submit_form)

        eye_btn1 = ctk.CTkButton(
            pw_row, text="🙈" if self.show_password else "👁",
            width=44, height=42, corner_radius=10,
            fg_color=PANEL_DARK, hover_color=CARD_HOVER,
            border_width=1, border_color=BORDER_SUBTLE,
            text_color=CYAN_ACCENT if self.show_password else TEXT_SECONDARY,
            font=("Segoe UI", 15), command=self.toggle_password_visibility
        )
        eye_btn1.pack(side="right")
        self.eye_buttons.append(eye_btn1)

        # --- שדה אימות סיסמה (בהרשמה בלבד) ---
        if not is_login:
            ctk.CTkLabel(
                inner, text="אימות סיסמה (Confirm Password)",
                font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY, anchor="e"
            ).pack(fill="x", pady=(0, 5))

            confirm_row = ctk.CTkFrame(inner, fg_color="transparent")
            confirm_row.pack(fill="x", pady=(0, 12))

            self.confirm_entry = ctk.CTkEntry(
                confirm_row, textvariable=self.confirm_password_var, height=42, corner_radius=10,
                fg_color=INPUT_BG, border_width=1.5, border_color=BORDER_SUBTLE,
                text_color=TEXT_PRIMARY, show=show_char, placeholder_text="הזן שוב את הסיסמה...",
                placeholder_text_color="#64748b", font=("Segoe UI", 13)
            )
            self.confirm_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
            self.confirm_entry.bind("<Return>", self.submit_form)

            eye_btn2 = ctk.CTkButton(
                confirm_row, text="🙈" if self.show_password else "👁",
                width=44, height=42, corner_radius=10,
                fg_color=PANEL_DARK, hover_color=CARD_HOVER,
                border_width=1, border_color=BORDER_SUBTLE,
                text_color=CYAN_ACCENT if self.show_password else TEXT_SECONDARY,
                font=("Segoe UI", 15), command=self.toggle_password_visibility
            )
            eye_btn2.pack(side="right")
            self.eye_buttons.append(eye_btn2)

        # --- הודעת סטטוס ---
        self.status_label = ctk.CTkLabel(
            inner, text="", font=("Segoe UI", 12, "bold"), text_color="#fda4af"
        )
        self.status_label.pack(pady=(4, 8))

        # --- כפתור שליחה ראשי ---
        submit_btn = ctk.CTkButton(
            inner,
            text="כניסה למערכת (Sign In)" if is_login else "הרשמה (Register)",
            height=46, corner_radius=12,
            fg_color=BLUE_ACCENT, hover_color="#1d4ed8",
            border_width=1, border_color=BORDER_GLOW,
            text_color="#ffffff", font=("Segoe UI", 14, "bold"),
            command=self.submit_form
        )
        submit_btn.pack(fill="x", pady=(2, 14))

        # --- החלפת מצב בין Login ל-Sign Up ---
        switch_row = ctk.CTkFrame(inner, fg_color="transparent")
        switch_row.pack()

        ctk.CTkLabel(
            switch_row,
            text="אין לך חשבון עדיין?" if is_login else "כבר יש לך חשבון?",
            font=("Segoe UI", 12), text_color=TEXT_SECONDARY
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            switch_row,
            text="הרשמה עכשיו" if is_login else "חזרה להתחברות",
            width=120, height=30, corner_radius=8,
            fg_color="transparent", hover_color=CARD_HOVER,
            text_color=CYAN_ACCENT, font=("Segoe UI", 12, "bold"),
            command=self.toggle_mode
        ).pack(side="right")

    def toggle_mode(self):
        self.current_mode = "signup" if self.current_mode == "login" else "login"
        self.show_password = False
        self.username_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        self.render_auth_card()

    def on_dashboard_logout(self):
        self.dashboard_win = None
        self.current_mode = "login"
        self.show_password = False
        self.username_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        self.render_auth_card()
        self.deiconify()
        self.focus_force()

    def open_dashboard(self, username, role):
        if self.dashboard_win is not None and self.dashboard_win.winfo_exists():
            self.dashboard_win.destroy()
        self.withdraw()
        self.dashboard_win = CyberVaultDashboardGUI(
            master=self,
            on_logout=self.on_dashboard_logout,
            username=username,
            role=role
        )

    def submit_form(self, _event=None):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.set_status("Please enter username and password", "#fda4af")
            return

        if self.current_mode == "signup":
            confirm = self.confirm_password_var.get().strip()
            if not confirm:
                self.set_status("Please confirm your password", "#fda4af")
                return
            if password != confirm:
                self.set_status("Passwords do not match!", "#fda4af")
                return

        action = "login" if self.current_mode == "login" else "register"
        self.set_status("Connecting to server...", TEXT_PRIMARY)
        self.update()

        try:
            res_data = send_request(action, username, password)
            if not isinstance(res_data, dict):
                self.set_status("Unexpected server response", "#fda4af")
                return

            is_success = (
                res_data.get("code") == 200
                or res_data.get("status") in (200, "success")
                or res_data.get("success") is True
            )
            if is_success:
                if self.current_mode == "login":
                    role = res_data.get("role") or res_data.get("user_role") or "מנהל מערכת"
                    self.set_status("Login Successful!", EMERALD)
                    self.after(250, lambda u=username, r=role: self.open_dashboard(u, r))
                else:
                    self.set_status("Account Created Successfully!", EMERALD)
            else:
                err_msg = res_data.get("message") or res_data.get("error") or "Operation failed"
                self.set_status(err_msg, "#fda4af")
        except (OSError, RuntimeError, ValueError):
            self.set_status("Cannot connect to server", "#fda4af")


if __name__ == "__main__":
    app = AuthApp()
    app.mainloop()