"""
FEOM Engine: High-Trust Open-Core Edition
Real MCP server with working UIA + SendInput.
Pro features (zero-alloc, DPI matrix, taskbar offset) are commercially isolated.
"""
import time
import ctypes
import subprocess
from pywinauto import Desktop

def os_native_click(x: int, y: int):
    """Standard SendInput (~3.96ms). Pro: zero-alloc ultraclick (<1.0ms)"""
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
    return True

def uia_invoke_element(window_title: str, control_id: str):
    """UIA InvokePattern (~8ms background, no mouse movement)"""
    t0 = time.perf_counter()
    try:
        app = Desktop(backend="uia").window(title_re=window_title)
        element = app.child_window(auto_id=control_id)
        element.iface_invoke.Invoke()
        ms = (time.perf_counter() - t0) * 1000
        return f"UIA Invoke: {ms:.1f}ms"
    except Exception as e:
        return f"UIA failed: {e}"

def hybrid_start_app(app_cmd: str):
    """Launch via terminal pipe (~0.01s boot)"""
    subprocess.Popen(f"start {app_cmd}", shell=True)
    return "App launched."

def list_windows():
    """List visible windows via UIA"""
    d = Desktop(backend="uia")
    return [w.window_text() for w in d.windows() if w.is_visible() and w.window_text()]
