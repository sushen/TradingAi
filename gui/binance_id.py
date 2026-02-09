"""
Standalone GUI that asks for a Binance ID first, then reveals API credentials.
"""
import json
import os
import tkinter as tk
from tkinter import messagebox


DEFAULT_APP_NAME = "TradingAi"
DEFAULT_FILENAME = "binance_keys.json"
DEFAULT_ID_KEY = "binance_id"


def _default_config_path() -> str:
    base_dir = os.getenv("APPDATA") or os.getcwd()
    return os.path.join(base_dir, DEFAULT_APP_NAME, DEFAULT_FILENAME)


def _read_config(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_config(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


def load_saved_credentials(
    config_path: str | None = None,
    env_key: str = "binance_api_key",
    env_secret: str = "binance_api_secret",
) -> tuple[str, str]:
    path = config_path or _default_config_path()
    data = _read_config(path)
    key = data.get(env_key) or data.get(env_key.upper(), "")
    secret = data.get(env_secret) or data.get(env_secret.upper(), "")
    if key:
        os.environ[env_key] = key
        os.environ[env_key.upper()] = key
    if secret:
        os.environ[env_secret] = secret
        os.environ[env_secret.upper()] = secret
    return key, secret


class BinanceIdGUI:
    def __init__(
        self,
        master: tk.Tk | None = None,
        config_path: str | None = None,
        id_key: str = DEFAULT_ID_KEY,
        env_key: str = "binance_api_key",
        env_secret: str = "binance_api_secret",
    ) -> None:
        self.root = master or tk.Tk()
        self._owns_root = master is None
        self.config_path = config_path or _default_config_path()
        self.id_key = id_key
        self.env_key = env_key
        self.env_secret = env_secret

        self.id_var = tk.StringVar()
        self.key_var = tk.StringVar()
        self.secret_var = tk.StringVar()
        self.show_secret_var = tk.BooleanVar(value=False)

        self._build_ui()
        self._load_initial_values()

    def _build_ui(self) -> None:
        self.root.title("Binance ID Setup")
        self.root.resizable(False, False)

        self.root.columnconfigure(0, weight=1)

        self.id_frame = tk.Frame(self.root)
        self.id_frame.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")
        self.id_frame.columnconfigure(1, weight=1)

        tk.Label(self.id_frame, text="Binance ID").grid(
            row=0, column=0, sticky="w"
        )
        self.id_entry = tk.Entry(self.id_frame, textvariable=self.id_var, width=36)
        self.id_entry.grid(row=0, column=1, padx=(6, 6), sticky="ew")
        tk.Button(
            self.id_frame, text="Save ID", width=10, command=self.save_id
        ).grid(row=0, column=2, sticky="e")

        self.credentials_frame = tk.Frame(self.root)
        self.credentials_frame.grid(
            row=1, column=0, padx=10, pady=(4, 6), sticky="ew"
        )
        self.credentials_frame.columnconfigure(1, weight=1)

        tk.Label(
            self.credentials_frame,
            text="Enter your Binance API key and secret.",
        ).grid(
            row=0, column=0, columnspan=2, pady=(0, 4), sticky="w"
        )

        tk.Label(self.credentials_frame, text="API key").grid(
            row=1, column=0, pady=(6, 2), sticky="w"
        )
        self.key_entry = tk.Entry(
            self.credentials_frame, textvariable=self.key_var, width=48
        )
        self.key_entry.grid(row=1, column=1, pady=(6, 2), sticky="ew")

        tk.Label(self.credentials_frame, text="API secret").grid(
            row=2, column=0, pady=(6, 2), sticky="w"
        )
        self.secret_entry = tk.Entry(
            self.credentials_frame, textvariable=self.secret_var, show="*", width=48
        )
        self.secret_entry.grid(row=2, column=1, pady=(6, 2), sticky="ew")

        tk.Checkbutton(
            self.credentials_frame,
            text="Show secret",
            variable=self.show_secret_var,
            command=self._toggle_secret,
        ).grid(row=3, column=1, pady=(0, 6), sticky="w")

        tk.Label(
            self.credentials_frame,
            text=f"Saved to: {self.config_path}",
            fg="#555555",
        ).grid(row=4, column=0, columnspan=2, pady=(2, 8), sticky="w")

        button_row = tk.Frame(self.credentials_frame)
        button_row.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        tk.Button(button_row, text="Save", width=10, command=self.save).grid(
            row=0, column=0, padx=5
        )
        tk.Button(button_row, text="Load", width=10, command=self.load).grid(
            row=0, column=1, padx=5
        )
        tk.Button(button_row, text="Clear", width=10, command=self.clear).grid(
            row=0, column=2, padx=5
        )

        self.close_button = tk.Button(
            self.root, text="Close", width=10, command=self.close
        )
        self.close_button.grid(row=2, column=0, pady=(0, 10))

    def _toggle_secret(self) -> None:
        self.secret_entry.config(show="" if self.show_secret_var.get() else "*")

    def _load_initial_values(self) -> None:
        data = _read_config(self.config_path)
        saved_id = data.get(self.id_key) or data.get(self.id_key.upper(), "")
        if saved_id:
            self.id_var.set(saved_id)
            self._show_credentials(True)
        else:
            self._show_credentials(False)

        env_key = os.environ.get(self.env_key) or os.environ.get(self.env_key.upper())
        env_secret = os.environ.get(self.env_secret) or os.environ.get(
            self.env_secret.upper()
        )
        if env_key or env_secret:
            self.key_var.set(env_key or "")
            self.secret_var.set(env_secret or "")
            return
        self.key_var.set(data.get(self.env_key, ""))
        self.secret_var.set(data.get(self.env_secret, ""))

    def _set_env(self, key: str, secret: str) -> None:
        os.environ[self.env_key] = key
        os.environ[self.env_key.upper()] = key
        os.environ[self.env_secret] = secret
        os.environ[self.env_secret.upper()] = secret

    def _set_env_id(self, binance_id: str) -> None:
        os.environ[self.id_key] = binance_id
        os.environ[self.id_key.upper()] = binance_id

    def _show_credentials(self, show: bool) -> None:
        if show:
            self.credentials_frame.grid()
        else:
            self.credentials_frame.grid_remove()

    def save_id(self) -> None:
        binance_id = self.id_var.get().strip()
        if not binance_id:
            messagebox.showerror("Save failed", "Binance ID is required.")
            return

        data = _read_config(self.config_path)
        data[self.id_key] = binance_id
        try:
            _write_config(self.config_path, data)
            self._set_env_id(binance_id)
        except OSError as exc:
            messagebox.showerror("Save failed", f"Unable to save file.\n{exc}")
            return

        self._show_credentials(True)
        messagebox.showinfo("Saved", "Binance ID saved.")

    def save(self) -> None:
        key = self.key_var.get().strip()
        secret = self.secret_var.get().strip()
        if not key or not secret:
            messagebox.showerror("Save failed", "Both fields are required.")
            return

        data = _read_config(self.config_path)
        data[self.env_key] = key
        data[self.env_secret] = secret
        try:
            _write_config(self.config_path, data)
            self._set_env(key, secret)
        except OSError as exc:
            messagebox.showerror("Save failed", f"Unable to save file.\n{exc}")
            return

        messagebox.showinfo("Saved", "Credentials saved successfully.")

    def load(self) -> None:
        data = _read_config(self.config_path)
        key = data.get(self.env_key, "")
        secret = data.get(self.env_secret, "")
        if not key and not secret:
            messagebox.showinfo("Not found", "No saved credentials found.")
            return

        self.key_var.set(key)
        self.secret_var.set(secret)
        self._set_env(key, secret)
        messagebox.showinfo("Loaded", "Credentials loaded.")

    def clear(self) -> None:
        self.key_var.set("")
        self.secret_var.set("")

    def close(self) -> None:
        self.root.destroy()

    def run(self) -> None:
        if self._owns_root:
            self.root.mainloop()


if __name__ == "__main__":
    BinanceIdGUI().run()
