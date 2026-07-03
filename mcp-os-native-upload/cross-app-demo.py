#!/usr/bin/env python3
"""
Real-World Demo v2: OS Native Cross-Application Pipeline
優化：批次讀取座標 → 快速發射 → 0 截圖 0 Token
"""
import ctypes, time, subprocess, os
from pywinauto import Desktop

# SendInput Engine
INPUT_MOUSE = 0
ABS, MOVE, DOWN, UP = 0x8000, 0x0001, 0x0002, 0x0004
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MOUSEINPUT)]
SI = ctypes.sizeof(INPUT)
user32 = ctypes.windll.user32
sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def sclick(x, y):
    ax, ay = int(x*65535/sw), int(y*65535/sh)
    user32.SendInput(1, ctypes.pointer(INPUT(type=0, mi=MOUSEINPUT(ax, ay, 0, ABS|MOVE, 0, None))), SI)
    user32.SendInput(1, ctypes.pointer(INPUT(type=0, mi=MOUSEINPUT(ax, ay, 0, ABS|DOWN, 0, None))), SI)
    user32.SendInput(1, ctypes.pointer(INPUT(type=0, mi=MOUSEINPUT(ax, ay, 0, ABS|UP, 0, None))), SI)

def get_coords_bulk(title, wanted):
    """Scan UIA tree ONCE and return coords for all wanted elements."""
    d = Desktop(backend="uia")
    wins = [w for w in d.windows() if title.lower() in w.window_text().lower() and w.is_visible()]
    if not wins: return {}
    result = {}
    for e in wins[0].descendants():
        aid = e.element_info.automation_id
        name = e.element_info.name
        if aid in wanted or name in wanted:
            r = e.element_info.rectangle
            result[aid or name] = (int(r.left+r.width()/2), int(r.top+r.height()/2))
    return result

def read_display(title, aid):
    d = Desktop(backend="uia")
    wins = [w for w in d.windows() if title.lower() in w.window_text().lower() and w.is_visible()]
    if not wins: return "?"
    for e in wins[0].descendants():
        if e.element_info.automation_id == aid:
            return e.element_info.name
    return "?"

def clipboard_set(text):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()

def ctrl_v():
    user32.keybd_event(0x11, 0, 0, 0)
    user32.keybd_event(0x56, 0, 0, 0)
    user32.keybd_event(0x56, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)

def ctrl_s():
    user32.keybd_event(0x11, 0, 0, 0)
    user32.keybd_event(0x53, 0, 0, 0)
    user32.keybd_event(0x53, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)

print("═" * 55)
print("  OS Native Cross-App Pipeline v2")
print("  0 screenshots · 0 vision tokens · SendInput clicks")
print("═" * 55)
t0 = time.perf_counter()

# ─── Step 1: Calculator ───
print("\n── [1] Calculator 1234×5.67 ──")
subprocess.run("start calc", shell=True)
time.sleep(1.5)
user32.SetForegroundWindow(
    [w for w in Desktop(backend="uia").windows() 
     if w.window_text() == "小算盤" and w.is_visible()][0].handle
)
time.sleep(0.2)

# Bulk scan ONCE
coords = get_coords_bulk("小算盤", {
    "clearButton", "num1Button", "num2Button", "num3Button", "num4Button",
    "num5Button", "num6Button", "num7Button", "multiplyButton", "equalButton",
    "decimalSeparatorButton"
})
print(f"  Found {len(coords)} button coordinates (1 scan)")

# Execute sequence
seq = ["clearButton","num1Button","num2Button","num3Button","num4Button",
       "multiplyButton","num5Button","decimalSeparatorButton","num6Button","num7Button","equalButton"]
click_times = []
for aid in seq:
    if aid in coords:
        t1 = time.perf_counter()
        sclick(*coords[aid])
        click_times.append((time.perf_counter() - t1) * 1000)
        time.sleep(0.04)

time.sleep(0.3)
result = read_display("小算盤", "CalculatorResults")
result_num = result.replace("顯示是 ", "")
print(f"  1234 × 5.67 = {result_num}")
print(f"  Avg click: {sum(click_times)/len(click_times):.2f}ms")

# ─── Step 2: Open Notepad ───
print("\n── [2] Notepad ──")
subprocess.run("start notepad", shell=True)
time.sleep(1)

# ─── Step 3: Write ──
print("\n── [3] Transfer result ──")
clipboard_set(f"1234 × 5.67 = {result_num}\nComputed: {time.strftime('%H:%M:%S')}\nEngine: OS Native SendInput ({sw}×{sw})")

# Focus Edit area in Notepad (click its center)
coords_np = get_coords_bulk("記事本", {"15", "Edit", "文本"})
if coords_np:
    k = list(coords_np.keys())[0]
    sclick(*coords_np[k]); time.sleep(0.1)
    ctrl_v()
    print("  Result pasted to Notepad ✓")

# ─── Step 4: Save ──
print("\n── [4] Save ──")
ctrl_s(); time.sleep(0.5)
coords_save = get_coords_bulk("另存", {"文件名(&N):", "檔名", "Edit"})
if coords_save:
    k = list(coords_save.keys())[0]
    sclick(*coords_save[k]); time.sleep(0.1)
    
    filename = "os-native-result.txt"
    clipboard_set(filename)
    ctrl_v(); time.sleep(0.1)
    
    # Save button
    for btn_name in ["儲存(&S)", "Save", "儲存"]:
        for e in Desktop(backend="uia").windows():
            if "另存" in e.window_text() and e.is_visible():
                for el in e.descendants():
                    if btn_name in (el.element_info.name or ""):
                        r = el.element_info.rectangle
                        sclick(int(r.left+r.width()/2), int(r.top+r.height()/2))
                        break
                break
else:
    print("  (save dialog auto-focused, pressing Enter)")
    time.sleep(0.2)
    user32.keybd_event(0x0D, 0, 0, 0)
    user32.keybd_event(0x0D, 0, 2, 0)

time.sleep(1)
total = time.perf_counter() - t0

# Verify
for path in [os.path.expanduser(f"~/Desktop/os-native-result.txt"),
             os.path.expanduser("~/os-native-result.txt")]:
    if os.path.exists(path):
        with open(path) as f:
            content = f.read().strip()
        print(f"\n  ✅ Saved to {path}")
        print(f"  Content: {content.split(chr(10))[0]}")
        break

print(f"\n{'='*55}")
print(f"  Total: {total:.2f}s  |  Clicks: {len(click_times)}  |  Vision: 0")
print(f"  {'='*55}")
