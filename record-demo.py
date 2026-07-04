"""
FEOM Demo — Screen Recording
Records a proper MP4 demo showing FEOM in action
Uses ffmpeg for screen capture, pywinauto for automation
"""
import os, time, subprocess, threading, sys

OUT = r"C:\Users\PP\Desktop\FEOM-Demo"
os.makedirs(OUT, exist_ok=True)

MP4 = os.path.join(OUT, "feom-demo.mp4")
DURATION = 15  # seconds

def record_screen(duration, output):
    """Record screen with ffmpeg"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "gdigrab",
        "-framerate", "10",
        "-t", str(duration),
        "-i", "desktop",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-crf", "28",
        output
    ]
    subprocess.run(cmd, capture_output=True)

# Start recording in background
print(f"Recording {DURATION}s demo to {MP4}...")
recorder = threading.Thread(target=record_screen, args=(DURATION, MP4), daemon=True)
recorder.start()
time.sleep(2)  # Let ffmpeg warm up

# === DEMO ACTIONS ===
print("\n1. Opening Notepad...")
subprocess.Popen("start notepad", shell=True)
time.sleep(2)

print("2. Typing via UIA...")
try:
    from pywinauto import Desktop
    from pywinauto.keyboard import send_keys
    d = Desktop(backend="uia")
    notepad = d.window(title_re=".*無標題.*|.*Untitled.*|.*記事本.*|.*Notepad.*")
    notepad.set_focus()
    send_keys("FEOM - Windows GUI Automation Demo{ENTER}", with_spaces=True)
    send_keys("Zero GPU. Zero API tokens. 8ms clicks.{ENTER}", with_spaces=True)
    time.sleep(2)
except Exception as e:
    print(f"   Type failed: {e}")
    # Fallback: type via ctypes
    time.sleep(1)

print("3. Scanning windows via UIA...")
try:
    from pywinauto import Desktop
    d = Desktop(backend="uia")
    wins = [w.window_text() for w in d.windows() if w.is_visible() and w.window_text()]
    print(f"   Found {len(wins)} windows")
    for w in wins[:5]:
        print(f"   - {w}")
except Exception as e:
    print(f"   UIA scan: {e}")
time.sleep(3)

print("4. Clicking via SendInput...")
import ctypes
t0 = time.perf_counter()
for _ in range(50):
    ctypes.windll.user32.SetCursorPos(300, 400)
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
avg = (time.perf_counter() - t0) / 50 * 1000
print(f"   SendInput: {avg:.1f}ms avg")
time.sleep(3)

print("5. Closing Notepad...")
subprocess.run("taskkill /f /im notepad.exe 2>nul", shell=True)
time.sleep(1)

# Wait for recording to finish
recorder.join(timeout=DURATION+5)
print(f"\nDone! Demo saved to: {MP4}")
print(f"Size: {os.path.getsize(MP4)/1024:.0f} KB" if os.path.exists(MP4) else "FAILED")
