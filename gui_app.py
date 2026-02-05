import os
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser

from resource_path import resource_path
from subscription.subscription_manager import SubscriptionManager


class GuiLogStream:
    def __init__(self, queue_handle, fallback):
        self.queue_handle = queue_handle
        self.fallback = fallback

    def write(self, message):
        if self.fallback:
            try:
                self.fallback.write(message)
            except Exception:
                pass
        if message:
            self.queue_handle.put(message)

    def flush(self):
        if self.fallback:
            try:
                self.fallback.flush()
            except Exception:
                pass


class TradingBotGUI:
    SPLASH_DURATION_MS = 1500
    SPLASH_WIDTH = 420
    SPLASH_HEIGHT = 240
    SPLASH_LOGO_SCALE = 0.5
    TRIAL_WIDTH = 420
    TRIAL_HEIGHT = 300

    def __init__(self, root):
        self.root = root
        self.root.title("TradingAi")
        self.root.geometry("360x320")
        self.root.resizable(False, False)

        self._app_icon = None
        self._splash_logo = None
        self._apply_app_icon()

        self.subscription = SubscriptionManager(
            app_name="TradingAi",
            legacy_app_name=["Trading Ai", "TradingBotX"],
        )

        self.root.withdraw()
        if not self._ensure_trial_started():
            self.root.destroy()
            return
        self._show_splash()

        self.bot_thread = None
        self.bot = None

        self.signal_var = tk.StringVar(value="Signal: --")
        self.price_var = tk.StringVar(value="BTC Price: --")
        # ===============================
        # UI
        # ===============================

        tk.Label(
            root,
            textvariable=self.signal_var,
            font=("Arial", 12, "bold"),
            fg="purple"
        ).pack(pady=5)

        tk.Label(
            root,
            textvariable=self.price_var,
            font=("Arial", 12, "bold"),
            fg="black"
        ).pack(pady=5)

        tk.Label(
            root,
            text="TradingAi",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.status_label = tk.Label(
            root,
            text="Checking subscription...",
            fg="blue"
        )
        self.status_label.pack(pady=5)

        self.alert_var = tk.StringVar(value="Alert: --")
        self.alert_label = tk.Label(
            root,
            textvariable=self.alert_var,
            fg="#b91c1c"
        )
        self.alert_label.pack(pady=4)

        self.start_btn = tk.Button(
            root,
            text="▶ Start Bot",
            width=20,
            command=self.start_bot,
            state="disabled"
        )
        self.start_btn.pack(pady=8)

        self.stop_btn = tk.Button(
            root,
            text="⛔ Stop Bot",
            width=20,
            command=self.stop_bot,
            state="disabled"
        )
        self.stop_btn.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(
            root,
            height=8,
            width=44,
            state="disabled",
            wrap="word",
            font=("Consolas", 9)
        )
        self.log_text.pack(padx=8, pady=(6, 8), fill="both", expand=False)

        self._init_log_stream()

        self._build_link_buttons()

        self.root.update_idletasks()
        desired_height = max(320, self.root.winfo_reqheight())
        self.root.geometry(f"360x{desired_height}")

        self.root.deiconify()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.check_subscription()

    def _build_link_buttons(self):
        container = tk.Frame(self.root)
        container.pack(pady=(6, 10))

        tk.Label(
            container,
            text="Join Learning Program",
            font=("Arial", 10),
            fg="#555555",
        ).pack(pady=(0, 6))

        button_row = tk.Frame(container)
        button_row.pack()

        tk.Button(
            button_row,
            text="Discord",
            width=12,
            command=lambda: self._open_url("https://discord.gg/GHjeawSYcp"),
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            button_row,
            text="Binance",
            width=12,
            command=lambda: self._open_url(
                "https://accounts.binance.com/register?ref=35023868"
            ),
        ).grid(row=0, column=1, padx=8)

    def _open_url(self, url: str):
        try:
            webbrowser.open_new_tab(url)
        except Exception as exc:
            messagebox.showerror("Open Link", f"Unable to open link.\n{exc}")

    def _ensure_trial_started(self) -> bool:
        if not self.subscription.needs_trial_start():
            return True
        return self._show_trial_start()

    def _show_trial_start(self) -> bool:
        started = {"value": False}

        trial = tk.Toplevel(self.root)
        trial.title("Start Trial")
        trial.resizable(False, False)
        trial.configure(bg="#0f172a")
        trial.attributes("-topmost", True)
        self._apply_app_icon(trial)

        width, height = self.TRIAL_WIDTH, self.TRIAL_HEIGHT
        trial.update_idletasks()
        screen_w = trial.winfo_screenwidth()
        screen_h = trial.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        trial.geometry(f"{width}x{height}+{x}+{y}")
        trial.update()
        try:
            trial.lift()
            trial.focus_force()
        except Exception:
            pass

        container = tk.Frame(trial, bg="#0f172a")
        container.pack(expand=True, fill="both")

        logo_image = self._load_logo_image(60)
        if logo_image is not None:
            self._trial_logo = logo_image
            tk.Label(
                container,
                image=logo_image,
                bg="#0f172a",
            ).pack(pady=(18, 6))

        tk.Label(
            container,
            text="Start your free trial",
            font=("Segoe UI", 16, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        ).pack(pady=(6, 6))

        tk.Label(
            container,
            text=f"Activate your {self.subscription.TRIAL_DAYS}-day trial to continue.",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0f172a",
        ).pack(pady=(0, 18))

        def start_trial():
            self.subscription.start_trial()
            started["value"] = True
            trial.destroy()

        def cancel():
            started["value"] = False
            trial.destroy()

        button_row = tk.Frame(container, bg="#0f172a")
        button_row.pack()

        tk.Button(
            button_row,
            text="Start Trial",
            width=12,
            command=start_trial,
        ).pack(side="left", padx=8)

        tk.Button(
            button_row,
            text="Exit",
            width=8,
            command=cancel,
        ).pack(side="left", padx=8)

        tk.Label(
            container,
            text="Join Learning Program",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0f172a",
        ).pack(pady=(12, 6))

        link_row = tk.Frame(container, bg="#0f172a")
        link_row.pack(pady=(0, 6))

        link_btn_kwargs = {
            "width": 11,
            "font": ("Segoe UI", 9),
            "fg": "#cbd5f5",
            "bg": "#3a3f4b",
            "activeforeground": "#e2e8f0",
            "activebackground": "#4a5161",
            "relief": "flat",
            "bd": 1,
            "highlightthickness": 1,
            "highlightbackground": "#4a5161",
            "cursor": "hand2",
        }

        tk.Button(
            link_row,
            text="Discord",
            command=lambda: self._open_url("https://discord.gg/GHjeawSYcp"),
            **link_btn_kwargs,
        ).pack(side="left", padx=8)

        tk.Button(
            link_row,
            text="Binance",
            command=lambda: self._open_url(
                "https://accounts.binance.com/register?ref=35023868"
            ),
            **link_btn_kwargs,
        ).pack(side="left", padx=8)

        trial.protocol("WM_DELETE_WINDOW", cancel)
        trial.grab_set()
        self.root.wait_window(trial)

        return started["value"]

    def _show_splash(self):
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True)
        splash.configure(bg="#0f172a")
        splash.attributes("-topmost", True)

        width, height = self.SPLASH_WIDTH, self.SPLASH_HEIGHT
        splash.update_idletasks()
        screen_w = splash.winfo_screenwidth()
        screen_h = splash.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        splash.geometry(f"{width}x{height}+{x}+{y}")
        splash.update()

        container = tk.Frame(splash, bg="#0f172a")
        container.pack(expand=True, fill="both")

        logo_size = int(self.SPLASH_HEIGHT * self.SPLASH_LOGO_SCALE)
        logo_image = self._load_logo_image(logo_size)
        if logo_image is not None:
            tk.Label(
                container,
                image=logo_image,
                bg="#0f172a",
            ).pack(pady=(30, 8))
            title_pady = (0, 8)
        else:
            title_pady = (60, 10)

        tk.Label(
            container,
            text="TradingAi",
            font=("Segoe UI", 24, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        ).pack(pady=title_pady)

        tk.Label(
            container,
            text="Starting up...",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0f172a",
        ).pack()

        self.root.after(self.SPLASH_DURATION_MS, splash.destroy)
        self.root.wait_window(splash)

    def _load_logo_image(self, size_px):
        try:
            logo_path = resource_path("logo.png")
            if not os.path.isfile(logo_path):
                return None

            from PIL import Image, ImageTk

            image = Image.open(logo_path).convert("RGBA")
            image.thumbnail((size_px, size_px), Image.LANCZOS)
            self._splash_logo = ImageTk.PhotoImage(image)
            return self._splash_logo
        except Exception:
            return None

    def _apply_app_icon(self, window=None):
        if window is None:
            window = self.root

        ico_path = resource_path("logo.ico")
        png_path = resource_path("logo.png")

        if os.path.isfile(ico_path):
            try:
                window.iconbitmap(ico_path)
                return
            except Exception:
                pass

        if os.path.isfile(png_path):
            try:
                if self._app_icon is None:
                    self._app_icon = tk.PhotoImage(file=png_path)
                window.iconphoto(True, self._app_icon)
            except Exception:
                pass

    def _init_log_stream(self):
        self._log_queue = queue.Queue()
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = GuiLogStream(self._log_queue, self._stdout)
        sys.stderr = GuiLogStream(self._log_queue, self._stderr)
        self._drain_log_queue()

    def _restore_stdio(self):
        if hasattr(self, "_stdout") and self._stdout is not None:
            sys.stdout = self._stdout
        if hasattr(self, "_stderr") and self._stderr is not None:
            sys.stderr = self._stderr

    def _on_close(self):
        self._restore_stdio()
        self.root.destroy()

    def _append_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _drain_log_queue(self):
        try:
            while True:
                message = self._log_queue.get_nowait()
                if message:
                    self._append_log(message)
        except queue.Empty:
            pass
        self.root.after(100, self._drain_log_queue)

    def show_alert(self, message, color="red"):
        self.root.after(0, lambda: self._set_alert(message, color))

    def _set_alert(self, message, color):
        self.alert_var.set(message)
        self.alert_label.config(fg=color)

    def update_signal(self, value):
        # Tkinter-safe update
        self.root.after(
            0,
            lambda: self.signal_var.set(f"Signal: {value}")
        )

    def update_price(self, value):
        def format_price():
            self.price_var.set(f"BTC Price: ${value:,.2f}")

        self.root.after(0, format_price)

    # ===============================
    # SUBSCRIPTION CHECK
    # ===============================
    def check_subscription(self):
        sub = self.subscription

        if not sub.is_allowed():
            self.status_label.config(
                text="❌ Subscription expired",
                fg="red"
            )
            messagebox.showerror(
                "Access Denied",
                "Trial expired.\nPlease subscribe to continue."
            )
            return

        if sub.is_trial():
            days = sub.days_left()
            self.status_label.config(
                text=f"⏳ Trial active ({days} days left)",
                fg="orange"
            )
        else:
            self.status_label.config(
                text="✅ Subscription active",
                fg="green"
            )

        self.start_btn.config(state="normal")

    # ===============================
    # BOT CONTROL
    # ===============================
    def start_bot(self):
        if self.bot_thread and self.bot_thread.is_alive():
            return

        from bot.trading_bot import TradingBot
        self.bot = TradingBot(
            on_signal=self.update_signal,
            on_price=self.update_price,
            on_alert=self.show_alert
        )

        self.bot_thread = threading.Thread(
            target=self.bot.run_trading_bot,
            daemon=True
        )
        self.bot_thread.start()

        self.status_label.config(
            text="🚀 Bot running...",
            fg="green"
        )
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def stop_bot(self):
        messagebox.showinfo(
            "Stop Bot",
            "Please close the application to stop the bot.\n"
            "(Safe shutdown)"
        )


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
