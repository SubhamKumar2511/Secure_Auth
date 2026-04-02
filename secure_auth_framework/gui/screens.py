import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

try:
    from PIL import Image, ImageDraw, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from ..config import ADMIN_CONTACT_EMAIL, ADMIN_CONTACT_PHONE
from ..auth_service import AuthService
from ..database import DatabaseManager


LIGHT_THEME = {
    "app_bg": "#eef1f5",
    "card_bg": "#ffffff",
    "title_fg": "#0a2240",
    "text_fg": "#14263d",
    "muted_fg": "#5b6777",
    "entry_bg": "#f8fafc",
    "entry_fg": "#14263d",
    "heading_bg": "#dfe5ee",
    "heading_fg": "#10233d",
    "card_border": "#cfd7e3",
    "focus_border": "#1d5ea8",
    "primary_bg": "#1d5ea8",
    "primary_hover": "#164a84",
    "primary_fg": "#ffffff",
    "secondary_bg": "#dce9fb",
    "secondary_hover": "#c8dbf7",
    "secondary_fg": "#10233d",
    "warning_bg": "#f0a500",
    "warning_hover": "#d48f00",
    "warning_fg": "#1f1500",
    "success_bg": "#d9f2e4",
    "success_fg": "#135a35",
    "error_bg": "#fde5e6",
    "error_fg": "#a01622",
    "shadow": "#c9d3df",
    "banner_bg": "#0b2d57",
    "banner_fg": "#f4f8ff",
    "banner_muted": "#c9dbf3",
    "banner_orb_1": "#1f6bc2",
    "banner_orb_2": "#f0a500",
}

DARK_THEME = {
    "app_bg": "#081a33",
    "card_bg": "#122844",
    "title_fg": "#f5f8ff",
    "text_fg": "#e5edf9",
    "muted_fg": "#aec2de",
    "entry_bg": "#0f223c",
    "entry_fg": "#f5f8ff",
    "heading_bg": "#1b3758",
    "heading_fg": "#f5f8ff",
    "card_border": "#25476f",
    "focus_border": "#4da3ff",
    "primary_bg": "#2d7fe6",
    "primary_hover": "#2468bc",
    "primary_fg": "#ffffff",
    "secondary_bg": "#19406a",
    "secondary_hover": "#245585",
    "secondary_fg": "#e5edf9",
    "warning_bg": "#f0a500",
    "warning_hover": "#d48f00",
    "warning_fg": "#1f1500",
    "success_bg": "#14432f",
    "success_fg": "#9de4be",
    "error_bg": "#5a1f27",
    "error_fg": "#ffc9ce",
    "shadow": "#061425",
    "banner_bg": "#061428",
    "banner_fg": "#f2f7ff",
    "banner_muted": "#a7bddb",
    "banner_orb_1": "#2d7fe6",
    "banner_orb_2": "#f0a500",
}


class AppUI:
    def __init__(self, root: tk.Tk, auth_service: AuthService, db: DatabaseManager):
        self.root = root
        self.auth_service = auth_service
        self.db = db
        self.is_dark_mode = False
        self.is_theme_animating = False
        self.active_screen = None
        self.theme_button = None
        self.scroll_canvas = None
        self.is_screen_animating = False
        self.disable_next_transition = False
        self.root.title("Secure Authentication Framework for Operating Systems")
        self.root.geometry("1100x760")
        self.root.minsize(980, 680)
        self.root.resizable(True, True)
        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.current_frame = None
        self._apply_theme()
        self.show_login_screen()

    def _apply_theme(self):
        self.colors = DARK_THEME if self.is_dark_mode else LIGHT_THEME

        self.root.configure(bg=self.colors["app_bg"])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background=self.colors["app_bg"])
        style.configure("Card.TFrame", background=self.colors["card_bg"], borderwidth=1, relief="solid")
        style.configure("TLabelframe", background=self.colors["app_bg"])
        style.configure("Title.TLabel", background=self.colors["app_bg"], font=("Segoe UI", 24, "bold"), foreground=self.colors["title_fg"])
        style.configure("AppSubtitle.TLabel", background=self.colors["app_bg"], font=("Segoe UI", 10), foreground=self.colors["muted_fg"])
        style.configure("Subtitle.TLabel", background=self.colors["card_bg"], font=("Segoe UI", 10), foreground=self.colors["muted_fg"])
        style.configure("Label.TLabel", background=self.colors["card_bg"], font=("Segoe UI", 10), foreground=self.colors["text_fg"])
        style.configure("CardTitle.TLabel", background=self.colors["card_bg"], font=("Segoe UI", 14, "bold"), foreground=self.colors["text_fg"])
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.colors["primary_bg"],
            foreground=self.colors["primary_fg"],
            bordercolor=self.colors["primary_bg"],
            focusthickness=0,
            padding=(10, 6),
        )
        style.map("Primary.TButton", background=[("active", self.colors["primary_hover"])])
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            background=self.colors["secondary_bg"],
            foreground=self.colors["secondary_fg"],
            bordercolor=self.colors["card_border"],
            focusthickness=0,
            padding=(10, 6),
        )
        style.map("Secondary.TButton", background=[("active", self.colors["secondary_hover"])])
        style.configure(
            "Warning.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.colors["warning_bg"],
            foreground=self.colors["warning_fg"],
            bordercolor=self.colors["warning_bg"],
            focusthickness=0,
            padding=(10, 6),
        )
        style.map("Warning.TButton", background=[("active", self.colors["warning_hover"])])
        style.configure(
            "Theme.TButton",
            font=("Segoe UI Emoji", 13),
            background=self.colors["secondary_bg"],
            foreground=self.colors["secondary_fg"],
            bordercolor=self.colors["card_border"],
            focusthickness=0,
            padding=(10, 3),
        )
        style.map("Theme.TButton", background=[("active", self.colors["secondary_hover"])])
        style.configure(
            "App.TEntry",
            fieldbackground=self.colors["entry_bg"],
            foreground=self.colors["entry_fg"],
            insertcolor=self.colors["entry_fg"],
            bordercolor=self.colors["card_border"],
            lightcolor=self.colors["card_border"],
            darkcolor=self.colors["card_border"],
        )
        style.configure(
            "Focus.TEntry",
            fieldbackground=self.colors["entry_bg"],
            foreground=self.colors["entry_fg"],
            insertcolor=self.colors["entry_fg"],
            bordercolor=self.colors["focus_border"],
            lightcolor=self.colors["focus_border"],
            darkcolor=self.colors["focus_border"],
        )
        style.configure(
            "App.TCombobox",
            fieldbackground=self.colors["entry_bg"],
            foreground=self.colors["entry_fg"],
            background=self.colors["entry_bg"],
            arrowcolor=self.colors["text_fg"],
        )
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Segoe UI", 10),
            background=self.colors["card_bg"],
            fieldbackground=self.colors["card_bg"],
            foreground=self.colors["text_fg"],
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=self.colors["heading_bg"],
            foreground=self.colors["heading_fg"],
        )

    def _show_alert(self, title: str, message: str, kind: str = "success"):
        bg = self.colors["success_bg"] if kind == "success" else self.colors["error_bg"]
        fg = self.colors["success_fg"] if kind == "success" else self.colors["error_fg"]

        win = tk.Toplevel(self.root)
        win.title(title)
        win.transient(self.root)
        win.grab_set()
        win.configure(bg=self.colors["app_bg"])
        win.resizable(False, False)

        panel = tk.Frame(win, bg=bg, bd=1, highlightthickness=1, highlightbackground=fg)
        panel.pack(padx=16, pady=16, fill="both", expand=True)

        tk.Label(panel, text=title, bg=bg, fg=fg, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Label(panel, text=message, bg=bg, fg=fg, justify="left", wraplength=380, font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(0, 12))
        ttk.Button(panel, text="OK", style="Primary.TButton", command=win.destroy).pack(anchor="e", padx=12, pady=(0, 10))

        self.root.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 220
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 110
        win.geometry(f"440x220+{x}+{y}")

    def _create_entry(self, parent, width=45, show=None):
        kwargs = {"width": width, "style": "App.TEntry"}
        if show is not None:
            kwargs["show"] = show
        entry = ttk.Entry(parent, **kwargs)
        entry.bind("<FocusIn>", lambda _e: entry.configure(style="Focus.TEntry"))
        entry.bind("<FocusOut>", lambda _e: entry.configure(style="App.TEntry"))
        return entry

    def _create_combobox(self, parent, textvariable, values, width=42, state="readonly"):
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            width=width,
            state=state,
            style="App.TCombobox",
        )
        return combo

    def _load_profile_photo(self, photo_path: str, max_size=(110, 110)):
        if not photo_path:
            return None
        if not Path(photo_path).exists():
            return None

        if PIL_AVAILABLE:
            try:
                diameter = min(max_size)
                image = Image.open(photo_path).convert("RGBA")
                src_w, src_h = image.size
                crop_size = min(src_w, src_h)
                left = (src_w - crop_size) // 2
                top = (src_h - crop_size) // 2
                image = image.crop((left, top, left + crop_size, top + crop_size))
                image = image.resize((diameter, diameter), Image.Resampling.LANCZOS)

                mask = Image.new("L", (diameter, diameter), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=255)

                rounded = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
                rounded.paste(image, (0, 0), mask)
                return ImageTk.PhotoImage(rounded)
            except Exception:
                return None

        try:
            image = tk.PhotoImage(file=photo_path)
        except tk.TclError:
            return None

        width = max(image.width(), 1)
        height = max(image.height(), 1)
        sample_x = max(width // max_size[0], 1)
        sample_y = max(height // max_size[1], 1)
        if sample_x > 1 or sample_y > 1:
            image = image.subsample(sample_x, sample_y)
        return image

    def _on_mousewheel(self, event):
        if self.scroll_canvas is None:
            return
        if not self.scroll_canvas.winfo_exists():
            return
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_profile_photo_section(self, parent, username: str, title: str = "Profile Photo"):
        profile_wrap = ttk.Frame(parent, style="Card.TFrame")
        profile_wrap.pack(fill="x", pady=(0, 12))

        avatar = tk.Canvas(
            profile_wrap,
            width=112,
            height=112,
            bg=self.colors["card_bg"],
            highlightthickness=0,
            bd=0,
        )
        avatar.pack(side="left", padx=(0, 12))

        avatar.create_oval(
            4,
            4,
            108,
            108,
            fill=self.colors["secondary_bg"],
            outline=self.colors["card_border"],
            width=2,
            tags="ring",
        )

        profile_info = ttk.Frame(profile_wrap, style="Card.TFrame")
        profile_info.pack(side="left", fill="x", expand=True)
        ttk.Label(profile_info, text=title, style="CardTitle.TLabel").pack(anchor="w")
        photo_status = ttk.Label(profile_info, text="No photo selected", style="Subtitle.TLabel")
        photo_status.pack(anchor="w", pady=(1, 5))

        btns = ttk.Frame(profile_info, style="Card.TFrame")
        btns.pack(anchor="w")

        def refresh_profile_photo():
            user_row = self.db.get_user(username)
            photo_path = user_row["profile_photo_path"] if user_row else ""
            image = self._load_profile_photo(photo_path, max_size=(96, 96))
            if image:
                avatar.delete("photo")
                avatar.delete("initials")
                avatar.create_image(56, 56, image=image, tags="photo")
                avatar.image = image
                photo_status.configure(text=f"Photo: {Path(photo_path).name}")
                return

            avatar.delete("photo")
            avatar.delete("initials")
            avatar.image = None
            initials = (username[:2] if username else "U").upper()
            avatar.create_text(
                56,
                56,
                text=initials,
                fill=self.colors["secondary_fg"],
                font=("Segoe UI", 18, "bold"),
                tags="initials",
            )
            if photo_path:
                photo_status.configure(text="Photo not found or unsupported.")
            else:
                photo_status.configure(text="No photo selected")

        def upload_profile_photo():
            path = filedialog.askopenfilename(
                title="Select Profile Photo",
                filetypes=[
                    ("Image files", "*.png *.gif *.ppm *.pgm *.jpg *.jpeg *.webp *.bmp"),
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("GIF", "*.gif"),
                    ("All files", "*.*"),
                ],
            )
            if not path:
                return
            self.db.update_profile_photo(username, path)
            refresh_profile_photo()
            self._show_alert("Success", "Profile photo updated.", "success")

        def remove_profile_photo():
            self.db.update_profile_photo(username, "")
            refresh_profile_photo()
            self._show_alert("Success", "Profile photo removed.", "success")

        ttk.Button(btns, text="Upload Photo", style="Primary.TButton", command=upload_profile_photo).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Remove Photo", style="Secondary.TButton", command=remove_profile_photo).pack(side="left")
        refresh_profile_photo()

    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def _transition_to_frame(self, new_frame: tk.Frame, animate: bool = True):
        if self.current_frame is None:
            new_frame.pack(fill="both", expand=True)
            self.current_frame = new_frame
            return

        if not animate:
            self.current_frame.destroy()
            self.current_frame = None
            new_frame.pack(fill="both", expand=True)
            self.current_frame = new_frame
            return

        if self.is_screen_animating:
            self.current_frame.destroy()
            self.current_frame = None
            new_frame.pack(fill="both", expand=True)
            self.current_frame = new_frame
            return

        self.is_screen_animating = True
        old_frame = self.current_frame
        self.root.update_idletasks()
        width = max(self.root.winfo_width(), 980)
        steps = 24
        step_delay_ms = 12

        old_frame.place(in_=self.root, x=0, y=0, relwidth=1, relheight=1)
        old_frame.lift()
        new_frame.place(in_=self.root, x=width, y=0, relwidth=1, relheight=1)
        new_frame.lift()

        def animate(step=0):
            progress = step / steps
            eased = 1 - ((1 - progress) ** 3)
            new_x = int(width * (1 - eased))
            old_x = -int(width * eased)
            new_frame.place_configure(x=new_x)
            old_frame.place_configure(x=old_x)
            if step < steps:
                self.root.after(step_delay_ms, lambda: animate(step + 1))
                return

            old_frame.destroy()
            new_frame.place_forget()
            new_frame.pack(fill="both", expand=True)
            self.current_frame = new_frame
            self.is_screen_animating = False

        animate()

    def make_container(self, title: str, subtitle: str = "") -> ttk.Frame:
        frame = tk.Frame(self.root, bg=self.colors["app_bg"])

        banner = tk.Canvas(
            frame,
            bg=self.colors["banner_bg"],
            height=150,
            highlightthickness=0,
            bd=0,
        )
        banner.pack(fill="x")
        banner.create_oval(-40, -70, 190, 170, fill=self.colors["banner_orb_1"], outline="")
        banner.create_oval(730, -100, 1030, 200, fill=self.colors["banner_orb_2"], outline="")
        banner.create_oval(600, 28, 820, 220, fill=self.colors["banner_orb_1"], outline="")

        banner_text = tk.Frame(banner, bg=self.colors["banner_bg"])
        banner.create_window(22, 18, anchor="nw", window=banner_text)

        tk.Label(
            banner_text,
            text=title,
            bg=self.colors["banner_bg"],
            fg=self.colors["banner_fg"],
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                banner_text,
                text=subtitle,
                bg=self.colors["banner_bg"],
                fg=self.colors["banner_muted"],
                font=("Segoe UI", 10),
            ).pack(anchor="w", pady=(2, 0))

        header = tk.Frame(banner, bg=self.colors["banner_bg"])
        header.place(relx=1.0, x=-20, y=18, anchor="ne")

        self.theme_button = ttk.Button(
            header,
            text="🌙" if not self.is_dark_mode else "🌞",
            style="Theme.TButton",
            command=self.toggle_theme,
        )
        self.theme_button.pack(side="right")

        content_wrap = ttk.Frame(frame, style="App.TFrame")
        content_wrap.pack(fill="both", expand=True)

        canvas = tk.Canvas(content_wrap, bg=self.colors["app_bg"], highlightthickness=0, bd=0)
        vscroll = ttk.Scrollbar(content_wrap, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = ttk.Frame(canvas, style="App.TFrame", padding=(24, 18, 24, 24))
        content_window = canvas.create_window((0, 0), window=content, anchor="nw")

        def on_content_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(content_window, width=event.width)

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        self.scroll_canvas = canvas
        animate = not self.disable_next_transition
        self._transition_to_frame(frame, animate=animate)
        self.disable_next_transition = False
        return content

    def make_card(self, parent) -> ttk.Frame:
        shadow = tk.Frame(parent, bg=self.colors["shadow"], bd=0, highlightthickness=0)
        shadow.pack(anchor="center", pady=(2, 8))
        card = ttk.Frame(shadow, style="Card.TFrame", padding=20)
        card.pack(padx=(0, 2), pady=(0, 2), ipadx=8, ipady=8)
        return card

    def show_login_screen(self):
        self.active_screen = self.show_login_screen
        frame = self.make_container("Secure Login", "Safe access with password + OTP verification")
        card = self.make_card(frame)

        ttk.Label(card, text="Username", style="Label.TLabel").pack(anchor="w")
        username_entry = self._create_entry(card, width=45)
        username_entry.pack(pady=(4, 10), ipady=3)

        ttk.Label(card, text="Password", style="Label.TLabel").pack(anchor="w")
        password_entry = self._create_entry(card, width=45, show="*")
        password_entry.pack(pady=(4, 14), ipady=3)

        def login_action():
            ok, msg = self.auth_service.login_step_one(username_entry.get(), password_entry.get())
            if ok:
                self._show_alert("Login", msg, "success")
                self.show_otp_screen()
            else:
                self._show_alert("Login Failed", msg, "error")

        def go_register():
            self.show_register_screen()

        def go_reset():
            self.show_password_reset_screen()

        def contact_admin():
            self._show_alert(
                "Contact Admin",
                "For account unlock or support, contact admin:\n\n"
                f"Email: {ADMIN_CONTACT_EMAIL}\n"
                f"Phone: {ADMIN_CONTACT_PHONE}",
                "success",
            )

        btn_row = ttk.Frame(card, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(2, 8))
        ttk.Button(btn_row, text="Login", style="Primary.TButton", command=login_action).pack(fill="x", pady=4, ipady=4)
        ttk.Button(btn_row, text="Create New Account", style="Secondary.TButton", command=go_register).pack(fill="x", pady=4, ipady=4)
        ttk.Button(btn_row, text="Forgot Password (OTP Reset)", style="Secondary.TButton", command=go_reset).pack(fill="x", pady=4, ipady=4)
        ttk.Button(btn_row, text="Contact Admin", style="Secondary.TButton", command=contact_admin).pack(fill="x", pady=4, ipady=4)

        ttk.Label(
            card,
            text="Sample users: admin / Admin@123   |   student / Student@123",
            style="Subtitle.TLabel",
        ).pack(pady=(10, 2), anchor="w")

    def show_register_screen(self):
        self.active_screen = self.show_register_screen
        frame = self.make_container("User Registration", "Create a secure account with strong password policy")
        card = self.make_card(frame)

        ttk.Label(card, text="Username", style="Label.TLabel").pack(anchor="w")
        username_entry = self._create_entry(card, width=45)
        username_entry.pack(pady=(4, 10), ipady=3)

        ttk.Label(card, text="Password", style="Label.TLabel").pack(anchor="w")
        password_entry = self._create_entry(card, width=45, show="*")
        password_entry.pack(pady=(4, 10), ipady=3)

        ttk.Label(card, text="Role", style="Label.TLabel").pack(anchor="w")
        role_var = tk.StringVar(value="user")
        self._create_combobox(card, textvariable=role_var, values=["user", "admin"], width=42, state="readonly").pack(pady=(4, 10))

        ttk.Label(
            card,
            text="Password policy: min 8 chars, uppercase, lowercase, number, special character",
            style="Subtitle.TLabel",
        ).pack(pady=(2, 10), anchor="w")

        def register_action():
            ok, msg = self.auth_service.register_user(username_entry.get(), password_entry.get(), role_var.get())
            if ok:
                self._show_alert("Registration", msg, "success")
                self.show_login_screen()
            else:
                self._show_alert("Registration Failed", msg, "error")

        ttk.Button(card, text="Create Account", style="Primary.TButton", command=register_action).pack(fill="x", pady=4, ipady=4)
        ttk.Button(card, text="Back to Login", style="Secondary.TButton", command=self.show_login_screen).pack(fill="x", pady=4, ipady=4)

    def show_otp_screen(self):
        self.active_screen = self.show_otp_screen
        frame = self.make_container("OTP Verification", "Enter the one-time code shown in terminal")
        card = self.make_card(frame)
        ttk.Label(card, text="OTP Code", style="Label.TLabel").pack(anchor="w")
        otp_entry = self._create_entry(card, width=45)
        otp_entry.pack(pady=(4, 12), ipady=3)

        def verify_otp():
            ok, msg = self.auth_service.verify_login_otp(otp_entry.get())
            if ok:
                self._show_alert("Success", msg, "success")
                self.show_dashboard()
            else:
                self._show_alert("OTP Failed", msg, "error")

        ttk.Button(card, text="Verify OTP", style="Primary.TButton", command=verify_otp).pack(fill="x", pady=4, ipady=4)
        ttk.Button(card, text="Back to Login", style="Secondary.TButton", command=self.show_login_screen).pack(fill="x", pady=4, ipady=4)

    def show_password_reset_screen(self):
        self.active_screen = self.show_password_reset_screen
        frame = self.make_container("Password Reset", "Generate OTP, then set a new strong password")
        card = self.make_card(frame)

        ttk.Label(card, text="Username", style="Label.TLabel").pack(anchor="w")
        username_entry = self._create_entry(card, width=45)
        username_entry.pack(pady=(4, 10), ipady=3)

        ttk.Label(card, text="OTP (after generating)", style="Label.TLabel").pack(anchor="w")
        otp_entry = self._create_entry(card, width=45)
        otp_entry.pack(pady=(4, 10), ipady=3)

        ttk.Label(card, text="New Password", style="Label.TLabel").pack(anchor="w")
        new_password_entry = self._create_entry(card, width=45, show="*")
        new_password_entry.pack(pady=(4, 12), ipady=3)

        def generate_reset_otp():
            ok, msg = self.auth_service.start_password_reset(username_entry.get())
            if ok:
                self._show_alert("OTP", msg, "success")
            else:
                self._show_alert("Error", msg, "error")

        def complete_reset():
            ok, msg = self.auth_service.complete_password_reset(otp_entry.get(), new_password_entry.get())
            if ok:
                self._show_alert("Reset", msg, "success")
                self.show_login_screen()
            else:
                self._show_alert("Reset Failed", msg, "error")

        ttk.Button(card, text="Generate OTP", style="Warning.TButton", command=generate_reset_otp).pack(fill="x", pady=4, ipady=4)
        ttk.Button(card, text="Reset Password", style="Primary.TButton", command=complete_reset).pack(fill="x", pady=4, ipady=4)
        ttk.Button(card, text="Back to Login", style="Secondary.TButton", command=self.show_login_screen).pack(fill="x", pady=4, ipady=4)

    def show_dashboard(self):
        self.active_screen = self.show_dashboard
        user = self.auth_service.current_user
        role = self.auth_service.get_current_user_role()
        frame = self.make_container("Dashboard", "Session is active until you logout")
        card = self.make_card(frame)
        self._build_profile_photo_section(card, user, "Your Profile Photo")

        ttk.Label(card, text=f"Welcome, {user}!", style="CardTitle.TLabel").pack(pady=(0, 6), anchor="w")
        ttk.Label(card, text=f"Role: {role}", style="Subtitle.TLabel").pack(pady=(0, 12), anchor="w")

        if role == "admin":
            ttk.Button(card, text="Open Admin Panel", style="Primary.TButton", command=self.show_admin_panel).pack(fill="x", pady=4, ipady=4)

        ttk.Button(card, text="Logout", style="Secondary.TButton", command=self.logout_action).pack(fill="x", pady=4, ipady=4)

    def logout_action(self):
        self.auth_service.logout()
        self._show_alert("Logout", "You have been logged out.", "success")
        self.show_login_screen()

    def show_admin_panel(self):
        self.active_screen = self.show_admin_panel
        frame = self.make_container("Admin Panel")

        current_admin = self.auth_service.current_user
        admin_profile_card = self.make_card(frame)
        self._build_profile_photo_section(admin_profile_card, current_admin, "Admin Profile Photo")

        action_row = ttk.Frame(frame, style="App.TFrame")
        action_row.pack(fill="x", pady=(6, 10))
        ttk.Label(action_row, text="Unlock username:", style="AppSubtitle.TLabel").pack(side="left")
        unlock_entry = self._create_entry(action_row, width=24)
        unlock_entry.pack(side="left", padx=(8, 12), ipady=2)

        users_wrap = ttk.Frame(frame, style="Card.TFrame", padding=10)
        users_wrap.pack(fill="x", pady=(4, 12))
        ttk.Label(users_wrap, text="Registered Users", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        users_tree = ttk.Treeview(users_wrap, columns=("username", "attempts", "locked", "role"), show="headings", height=7)
        users_tree.heading("username", text="Username")
        users_tree.heading("attempts", text="Failed Attempts")
        users_tree.heading("locked", text="Locked")
        users_tree.heading("role", text="Role")
        users_tree.column("username", width=260, anchor="w")
        users_tree.column("attempts", width=160, anchor="center")
        users_tree.column("locked", width=140, anchor="center")
        users_tree.column("role", width=140, anchor="center")
        users_tree.pack(fill="x")

        logs_wrap = ttk.Frame(frame, style="Card.TFrame", padding=10)
        logs_wrap.pack(fill="both", expand=True, pady=(0, 4))
        ttk.Label(logs_wrap, text="Login Logs", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        logs_tree = ttk.Treeview(logs_wrap, columns=("username", "timestamp", "status"), show="headings", height=9)
        logs_tree.heading("username", text="Username")
        logs_tree.heading("timestamp", text="Timestamp")
        logs_tree.heading("status", text="Status")
        logs_tree.column("username", width=220, anchor="w")
        logs_tree.column("timestamp", width=420, anchor="center")
        logs_tree.column("status", width=160, anchor="center")
        logs_tree.pack(fill="both", expand=True)

        def refresh_data():
            for item in users_tree.get_children():
                users_tree.delete(item)
            for row in self.db.get_all_users():
                username, attempts, locked, role = row
                users_tree.insert("", "end", values=(username, attempts, bool(locked), role))

            for item in logs_tree.get_children():
                logs_tree.delete(item)
            for row in self.db.get_logs():
                logs_tree.insert("", "end", values=row)

        def unlock_action():
            username = unlock_entry.get().strip()
            if not username:
                self._show_alert("Error", "Enter a username to unlock.", "error")
                return
            user = self.db.get_user(username)
            if not user:
                self._show_alert("Error", "User not found.", "error")
                return
            self.db.unlock_account(username)
            self._show_alert("Success", f"Unlocked account for '{username}'.", "success")
            refresh_data()

        ttk.Button(action_row, text="Unlock Account", style="Primary.TButton", command=unlock_action).pack(side="left", padx=4)
        ttk.Button(action_row, text="Refresh", style="Secondary.TButton", command=refresh_data).pack(side="left", padx=4)
        ttk.Button(action_row, text="Back", style="Secondary.TButton", command=self.show_dashboard).pack(side="right")

        refresh_data()

    def toggle_theme(self):
        if self.is_theme_animating:
            return
        self.is_theme_animating = True
        self._finish_theme_toggle()

    def _finish_theme_toggle(self):
        self.is_dark_mode = not self.is_dark_mode
        self._apply_theme()
        if self.active_screen:
            self.disable_next_transition = True
            self.active_screen()
        self.is_theme_animating = False

    def _pulse_background(self):
        pulse_color = "#1b2b4a" if self.is_dark_mode else "#e8f0ff"
        base_color = self.colors["app_bg"]
        self.root.configure(bg=pulse_color)
        self.root.after(90, lambda: self.root.configure(bg=base_color))

