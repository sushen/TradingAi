import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Resolve data files in both dev and PyInstaller builds.
    - onedir: data is next to the exe
    - onefile: data is in sys._MEIPASS
    """
    if getattr(sys, "frozen", False):
        exe_base = os.path.dirname(sys.executable)
        candidate = os.path.join(exe_base, relative_path)
        if os.path.exists(candidate):
            return candidate
        base_path = getattr(sys, "_MEIPASS", exe_base)
        return os.path.join(base_path, relative_path)

    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)
