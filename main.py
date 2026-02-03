# ===============================
# TradingAiV13 - ENTRY POINT
# ===============================

import os
import sys
import socket
import ctypes

# ===============================
# NETWORK STABILITY FIX
# ===============================
socket.setdefaulttimeout(30)

# ===============================
# PREVENT WINDOWS SLEEP
# ===============================
if os.name == "nt":
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    )

# ===============================
# SAFE PATH FIX (PyInstaller)
# ===============================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp dir
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ===============================
# START GUI
# ===============================
def start_gui():
    import tkinter as tk
    from gui_app import TradingBotGUI

    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    start_gui()
