#!/usr/bin/env python3
"""
Recording Wrapper: starts ffmpeg → runs demo → stops ffmpeg → saves to desktop
"""
import subprocess, time, os, signal, sys

output_path = r"C:\Users\PP\Desktop\os-native-demo-recording.mp4"
demo_path = os.path.expanduser("~/os-native-mcp/complex-demo.py")

print("═══ RECORDING WRAPPER ═══")
print(f"Output: {output_path}")

# Start ffmpeg in background
ffmpeg_cmd = [
    "ffmpeg", "-f", "gdigrab", "-framerate", "15",
    "-video_size", "1280x720", "-offset_x", "320", "-offset_y", "180",
    "-i", "desktop",
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-y", output_path
]

print("Starting ffmpeg recording...")
ffmpeg_proc = subprocess.Popen(
    ffmpeg_cmd,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(1)
print(f"FFmpeg PID: {ffmpeg_proc.pid}")

# Run the demo
print("\nRunning complex demo...")
demo_proc = subprocess.Popen(
    [sys.executable, demo_path],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace',
    env={**os.environ, "PYTHONIOENCODING": "utf-8"}
)

# Stream demo output
for line in iter(demo_proc.stdout.readline, ""):
    print(line, end="", flush=True)

demo_proc.wait()
print(f"\nDemo exited with code {demo_proc.returncode}")

# Wait a beat for ffmpeg to catch final frame
time.sleep(1.5)

# Stop ffmpeg
print("Stopping ffmpeg...")
ffmpeg_proc.terminate()
try:
    ffmpeg_proc.wait(timeout=5)
except:
    ffmpeg_proc.kill()

# Verify output
if os.path.exists(output_path):
    size_mb = os.path.getsize(output_path) / (1024*1024)
    print(f"\n✅ Recording saved: {output_path}")
    print(f"   Size: {size_mb:.2f} MB")
else:
    print(f"\n❌ Recording file not found at {output_path}")
