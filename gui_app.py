import threading
import tkinter as tk
from tkinter import messagebox

from subscription.subscription_manager import SubscriptionManager
from bot.trading_bot import TradingBot


class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TradingBotX")
        self.root.geometry("360x220")
        self.root.resizable(False, False)

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
            text="TradingBotX",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.status_label = tk.Label(
            root,
            text="Checking subscription...",
            fg="blue"
        )
        self.status_label.pack(pady=5)

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

        self.check_subscription()

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
        sub = SubscriptionManager(app_name="TradingBotX")

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

        self.bot = TradingBot(on_signal=self.update_signal, on_price=self.update_price)

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
