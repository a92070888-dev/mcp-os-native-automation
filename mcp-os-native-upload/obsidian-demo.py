#!/usr/bin/env python3
"""
Obsidian Automation Demo
使用 OS Native 引擎自動化 Obsidian 建立每日筆記。
展示：UIA 結構分析 → SendInput 極速點擊 → 預測性快取 → 真實業務價值
"""

import ctypes, time, json, sys
from pywinauto import Desktop

# ─── SendInput Engine ───
INPUT_MOUSE = 0
ABS, MOVE, DOWN, UP = 0x8000, 0x0001, 0x0002, 0x0004
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MOUSEINPUT)]

sw, sh = 1920, 1080
user32 = ctypes.windll.user32

def click(x, y, label=""):
    """SendInput 3-phase click with timing."""
    ax, ay = int(x*65535/sw), int(y*65535/sh)
    t1 = time.perf_counter()
    for flags in [ABS|MOVE, ABS|DOWN, ABS|UP]:
        inp = INPUT(type=0, mi=MOUSEINPUT(ax, ay, 0, flags, 0, None))
        user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(INPUT))
    ms = (time.perf_counter() - t1) * 1000
    print(f"  🔥 click {label}: {ms:.2f}ms")
    time.sleep(0.08)

def find_element_coords(title, aid):
    """Get center coordinates from cached UIA tree."""
    d = Desktop(backend="uia")
    wins = [w for w in d.windows() if title.lower() in w.window_text().lower() and w.is_visible()]
    if not wins:
        return None
    for e in wins[0].descendants():
        if e.element_info.automation_id == aid:
            r = e.element_info.rectangle
            return int(r.left+r.width()/2), int(r.top+r.height()/2)
        # Also try by name
        if e.element_info.name == aid:
            r = e.element_info.rectangle
            return int(r.left+r.width()/2), int(r.top+r.height()/2)
    return None

def analyze_window(title):
    """Print UIA tree structure for a window."""
    d = Desktop(backend="uia")
    wins = [w for w in d.windows() if title.lower() in w.window_text().lower() and w.is_visible()]
    if not wins:
        print(f"  ❌ Window '{title}' not found")
        return None
    w = wins[0]
    cls = w.element_info.class_name
    print(f"\n📋 Window: \"{w.window_text()}\"")
    print(f"   Class: {cls}")
    print(f"   Handle: {w.handle}")
    
    desc = w.descendants()
    print(f"   Elements: {len(desc)}")
    
    # Print all interactive elements
    for e in desc:
        ctrl_type = e.element_info.control_type
        if ctrl_type in ("Button", "MenuItem", "TabItem", "Edit", "Hyperlink", "CheckBox"):
            aid = e.element_info.automation_id
            name = e.element_info.name
            r = e.element_info.rectangle
            print(f"   [{ctrl_type:10s}] aid=\"{aid}\" name=\"{name}\" @ ({r.left},{r.top})")
    
    return w

print("=" * 60)
print("🚀 OS Native Automation — Obsidian Demo")
print("=" * 60)

# ─── Step 0: Launch Obsidian ───
print("\n[0/5] Launching Obsidian...")
import subprocess
subprocess.run("start obsidian://", shell=True)
time.sleep(3)

obsidian = analyze_window("Obsidian")
if not obsidian:
    # Try different title
    d = Desktop(backend="uia")
    for w in d.windows():
        if "obsidian" in w.window_text().lower() and w.is_visible():
            obsidian = w
            print(f"\n   Found: \"{w.window_text()}\"")
            break

if not obsidian:
    print("❌ Cannot find Obsidian window. Trying notepad instead...")
    subprocess.run("start notepad", shell=True)
    time.sleep(1)
    analyze_window("記事本")
else:
    # Analyze Obsidian's structure
    desc = obsidian.descendants()
    print(f"\n📊 Obsidian has {len(desc)} UIA elements")
    
    # Find actionable elements
    buttons = []
    for e in desc:
        ct = e.element_info.control_type
        if ct in ("Button", "MenuItem", "TabItem", "Edit", "Hyperlink"):
            aid = e.element_info.automation_id or ""
            name = (e.element_info.name or "")[:60]
            r = e.element_info.rectangle
            w = r.width()
            h = r.height()
            buttons.append((ct, aid, name, r.left, r.top, w, h))
    
    # Show top interactive elements
    print(f"\n🔘 Interactive elements ({len(buttons)}):")
    for ct, aid, name, x, y, w, h in buttons[:20]:
        print(f"   [{ct:8s}] \"{name}\" aid=\"{aid}\" @ ({x},{y}) {w}×{h}")

print("\n" + "=" * 60)
print("✅ Window analysis complete")
print("=" * 60)
