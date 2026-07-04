"""FEOM Quick Demo - Run this to test your setup"""
import time, ctypes
try:
    from pywinauto import Desktop
    d=Desktop(backend="uia")
    wins=[w.window_text() for w in d.windows() if w.is_visible() and w.window_text()]
    print(f"Windows: {len(wins)}")
    for w in wins[:5]: print(f"  - {w}")
except: print("Window scan unavailable")

class I(ctypes.Structure):
    _fields_=[("type",ctypes.c_ulong),("mi",ctypes.c_long*4+ctypes.c_ulong*2)]
n=100;t0=time.perf_counter()
for _ in range(n):
    ctypes.windll.user32.SetCursorPos(500,500)
    ctypes.windll.user32.mouse_event(0x0002,0,0,0,0)
    ctypes.windll.user32.mouse_event(0x0004,0,0,0,0)
avg=(time.perf_counter()-t0)/n*1000
print(f"
SendInput benchmark ({n}x): {avg:.1f}ms avg")
print("Done! https://github.com/a92070888-dev/mcp-os-native-automation")
