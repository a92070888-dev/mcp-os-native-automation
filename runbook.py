import time
import win32gui
import ctypes

print("[FEOM Engine] Initializing Open-Core Edition...")

def base_click(x: int, y: int):
    """Tier 3 / Basic click interface (DPI conversion & Zero-alloc excluded)"""
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
    return True

def safe_terminate_app(hwnd):
    if win32gui.IsWindow(hwnd):
        win32gui.PostMessage(hwnd, 0x0010, 0, 0)
        return True
    return False

def hybrid_start_app(app_cmd: str):
    import subprocess
    subprocess.Popen(f"start {app_cmd}", shell=True)
    return "App initialized."
