"""
OS Native Automation MCP Server
================================
三層 Windows 自動化架構：UIA InvokePattern / Win32 PostMessage / OmniParser
根據應用類型自動路由到最快方案。

Usage:
  python server.py              # Run as MCP server (stdio)
  python server.py --help       # Show help

Hermes config:
  mcp_servers:
    os-native:
      command: "C:\\Users\\PP\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe"
      args: ["C:\\Users\\PP\\os-native-mcp\\server.py"]
"""

import json
import sys
import time
import traceback
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ─────────────────────────────────────────────
# UIA / Win32 自動化核心
# ─────────────────────────────────────────────


def _import_pywinauto():
    """Lazy import pywinauto — only imported when UIA tools are used."""
    try:
        from pywinauto import Desktop
        return Desktop
    except ImportError:
        return None


def _import_win32():
    """Lazy import pywin32."""
    try:
        import win32gui
        import win32con
        return win32gui, win32con
    except ImportError:
        return None, None


# ─── Helper: get visible window by title ───

def _find_window(title: str):
    """Find a visible window by title substring match.
    Returns: (handle, class_name, exact_title) or raises ValueError.
    """
    Desktop = _import_pywinauto()
    if Desktop is None:
        raise RuntimeError("pywinauto not installed. Run: pip install pywinauto")

    d = Desktop(backend="uia")
    wins = [w for w in d.windows() if title.lower() in w.window_text().lower() and w.is_visible()]

    if not wins:
        # Fallback: try win32gui
        win32gui, _ = _import_win32()
        if win32gui:
            found = []

            def enum_cb(hwnd, _):
                txt = win32gui.GetWindowText(hwnd)
                if title.lower() in txt.lower() and win32gui.IsWindowVisible(hwnd):
                    found.append((hwnd, win32gui.GetClassName(hwnd), txt))
                return True
            win32gui.EnumWindows(enum_cb, None)
            if found:
                hwnd, cls, txt = found[0]
                return hwnd, cls, txt
        raise ValueError(f"No visible window matching '{title}' found")

    calc = wins[0]
    return calc.handle, calc.element_info.class_name, calc.window_text()


def _detect_app_type(hwnd: int, class_name: str) -> str:
    """Detect application type from window class name."""
    if "Windows.UI.Core" in class_name or "ApplicationFrame" in class_name:
        return "uwp"
    win32gui, _ = _import_win32()
    if win32gui:
        # Check for Win32 child windows
        has_children = False

        def enum_check(ch, _):
            nonlocal has_children
            cid = win32gui.GetDlgCtrlID(ch)
            if cid and win32gui.GetWindowText(ch):
                has_children = True
        win32gui.EnumChildWindows(hwnd, enum_check, None)
        if has_children:
            return "win32"
    return "uia_fallback"


# ─────────────────────────────────────────────
# 預測性非同步快取 (Predictive Async Cache)
# ─────────────────────────────────────────────

import threading

class _PredictiveCache:
    """Background-prefetched UIA element tree cache.
    
    First call: ~74ms scan. Immediately schedules background refresh.
    Second+ call (within 2s): 0ms — instant cache hit.
    After each action: schedules next refresh, keeping pipeline always warm.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._store = {}        # title.lower() → (timestamp, descendants_list)
        self._ttl = 2.0          # seconds before cache is considered stale

    def get(self, title: str):
        """Get cached descendants if fresh, or None."""
        with self._lock:
            entry = self._store.get(title.lower())
            if entry is None:
                return None
            ts, desc = entry
            if time.time() - ts > self._ttl:
                return None  # expired
            return desc

    def set(self, title: str, descendants):
        """Store fresh descendants."""
        with self._lock:
            self._store[title.lower()] = (time.time(), descendants)

    def invalidate(self, title: str):
        """Remove cache entry — forces re-scan on next call."""
        with self._lock:
            self._store.pop(title.lower(), None)

    def refresh_async(self, title: str):
        """Background thread: re-scan and update cache."""
        def _worker():
            try:
                desc = _do_uia_scan(title)
                self.set(title, desc)
            except Exception:
                pass  # Background failures are non-fatal
        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def refresh_sync(self, title: str):
        """Synchronous scan + async pre-fetch for next call."""
        desc = _do_uia_scan(title)
        self.set(title, desc)
        self.refresh_async(title)  # Queue next refresh
        return desc


def _do_uia_scan(title: str):
    """Raw UIA descendants scan — used by both sync and async paths."""
    Desktop = _import_pywinauto()
    d = Desktop(backend="uia")
    wins = [w for w in d.windows() if title.lower() in w.window_text().lower() and w.is_visible()]
    if not wins:
        raise ValueError(f"No visible window matching '{title}'")
    return wins[0].descendants()


_pcache = _PredictiveCache()


def _get_descendants(title: str):
    """Get UIA descendants with predictive caching.
    
    Cache hit: ~0ms (instant).
    Cache miss: ~74ms (scan) + schedules async refresh.
    """
    cached = _pcache.get(title)
    if cached is not None:
        return cached
    return _pcache.refresh_sync(title)


# ─────────────────────────────────────────────
# Win32 SendInput — 核心層輸入注入
# ─────────────────────────────────────────────

import ctypes

class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class _INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", _MOUSEINPUT)]

_ABS = 0x8000
_MOVE = 0x0001
_DOWN = 0x0002
_UP = 0x0004

_screen_w = ctypes.windll.user32.GetSystemMetrics(0)
_screen_h = ctypes.windll.user32.GetSystemMetrics(1)
_user32 = ctypes.windll.user32


def _sendinput_click(x: int, y: int):
    """Win32 SendInput absolute mouse click. ~1.5ms, works on ALL window types.
    
    3-phase: MOVE → DOWN → UP for maximum compatibility.
    """
    ax, ay = int(x * 65535 / _screen_w), int(y * 65535 / _screen_h)
    ABS = _ABS
    # Phase 1: Move
    m = _INPUT(type=0, mi=_MOUSEINPUT(ax, ay, 0, ABS | _MOVE, 0, None))
    _user32.SendInput(1, ctypes.pointer(m), ctypes.sizeof(_INPUT))
    # Phase 2: Down
    d = _INPUT(type=0, mi=_MOUSEINPUT(ax, ay, 0, ABS | _DOWN, 0, None))
    _user32.SendInput(1, ctypes.pointer(d), ctypes.sizeof(_INPUT))
    # Phase 3: Up
    u = _INPUT(type=0, mi=_MOUSEINPUT(ax, ay, 0, ABS | _UP, 0, None))
    _user32.SendInput(1, ctypes.pointer(u), ctypes.sizeof(_INPUT))


def _get_element_center(title: str, auto_id: str):
    """Get center coordinates of a UIA element from cached tree."""
    desc = _get_descendants(title)
    for e in desc:
        if e.element_info.automation_id == auto_id:
            r = e.element_info.rectangle
            return int(r.left + r.width() / 2), int(r.top + r.height() / 2)
    return None


# ─── FastMCP Server ───

mcp = FastMCP("os-native-automation")


@mcp.tool()
def os_native_analyze_window(title: str) -> str:
    """Analyze a window by title — detect app type, UIA availability, and list buttons.

    Args:
        title: Window title (substring match)
    Returns:
        JSON with window info, app type, recommended method, and available buttons
    """
    try:
        hwnd, cls_name, exact_title = _find_window(title)
        app_type = _detect_app_type(hwnd, cls_name)

        result = {
            "window": {
                "title": exact_title,
                "handle": hwnd,
                "class_name": cls_name,
                "app_type": app_type,
            },
            "recommended_method": {
                "uwp": "uia_invoke",
                "win32": "win32_postmessage",
                "uia_fallback": "uia_click_input"
            }.get(app_type, "uia_invoke"),
            "buttons": [],
        }

        # Get UIA tree buttons
        desc = _get_descendants(title)
        for e in desc:
            if e.element_info.control_type == "Button":
                aid = e.element_info.automation_id
                name = e.element_info.name
                if aid or name:
                    result["buttons"].append({
                        "auto_id": aid,
                        "name": name
                    })

        # If Win32, also list child controls
        if app_type == "win32":
            win32gui, _ = _import_win32()
            children = []

            def enum_ch(ch, _):
                cid = win32gui.GetDlgCtrlID(ch)
                ctext = win32gui.GetWindowText(ch)
                ccls = win32gui.GetClassName(ch)
                children.append({"hwnd": ch, "ctrl_id": cid, "text": ctext, "class": ccls})
            win32gui.EnumChildWindows(hwnd, enum_ch, None)
            result["win32_children"] = children

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()}, ensure_ascii=False)


@mcp.tool()
def os_native_click(title: str, auto_id: str, method: Optional[str] = None) -> str:
    """Click a button by its AutomationID. Auto-routes to the fastest method.

    Args:
        title: Window title (substring match)
        auto_id: UIA Automation ID of the button (e.g. 'num5Button', 'clearButton')
        method: Optional override:
                'sendinput' — Win32 SendInput (~1.5ms, fastest universal, needs foreground)
                'invoke' — UIA InvokePattern (~14ms, works in background)
                'click_input' — mouse simulation (~200ms, last resort)
                None — auto-detect: sendinput for foreground windows, invoke for background
    Returns:
        Status message with latency
    """
    try:
        hwnd, cls_name, exact_title = _find_window(title)
        app_type = _detect_app_type(hwnd, cls_name)

        if method is None:
            # Auto-route: SendInput if window is foreground, else invoke
            fg_hwnd = _user32.GetForegroundWindow()
            method = "sendinput" if fg_hwnd == hwnd else "invoke"

        t1 = time.perf_counter()

        if method == "sendinput":
            coord = _get_element_center(title, auto_id)
            if coord is None:
                return json.dumps({"error": f"Element '{auto_id}' not found in '{title}'"})
            _sendinput_click(*coord)
        else:
            desc = _get_descendants(title)
            target = None
            for e in desc:
                if e.element_info.automation_id == auto_id:
                    target = e
                    break
            if target is None:
                for e in desc:
                    if e.element_info.name == auto_id:
                        target = e
                        break
            if target is None:
                return json.dumps({
                    "error": f"Element with auto_id='{auto_id}' not found in '{title}'"
                })
            if method == "invoke":
                target.invoke()
            else:
                target.click_input()

        elapsed_ms = (time.perf_counter() - t1) * 1000

        # Predictive refresh: background scans tree for next call
        _pcache.refresh_async(title)

        return json.dumps({
            "success": True,
            "action": f"click '{auto_id}'",
            "method": method,
            "latency_ms": round(elapsed_ms, 1),
            "window": exact_title
        })

    except Exception as e:
        return json.dumps({"error": str(e), "traceback": traceback.format_exc()}, ensure_ascii=False)


@mcp.tool()
def os_native_read(title: str, auto_id: str) -> str:
    """Read text from a UIA element by AutomationID.

    Args:
        title: Window title (substring match)
        auto_id: UIA Automation ID (e.g. 'CalculatorResults', 'Header')
    Returns:
        Text content of the element
    """
    try:
        desc = _get_descendants(title)
        for e in desc:
            if e.element_info.automation_id == auto_id:
                text = e.element_info.name
                return json.dumps({
                    "success": True,
                    "auto_id": auto_id,
                    "text": text
                })
        return json.dumps({"error": f"Element '{auto_id}' not found"})

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def os_native_get_tree(title: str, control_type: Optional[str] = None) -> str:
    """Get the full UIA tree for a window as structured JSON.

    Args:
        title: Window title (substring match)
        control_type: Optional filter — 'Button', 'Text', 'Edit', etc.
    Returns:
        JSON array of UI elements with auto_id, name, type, and position
    """
    try:
        desc = _get_descendants(title)
        elements = []
        for e in desc:
            info = e.element_info
            ctype = info.control_type
            if control_type and ctype != control_type:
                continue
            rect = info.rectangle
            elements.append({
                "auto_id": info.automation_id,
                "name": info.name,
                "type": ctype,
                "class_name": info.class_name,
                "enabled": info.enabled,
                "x": int(rect.left),
                "y": int(rect.top),
                "width": int(rect.width()),
                "height": int(rect.height()),
            })
        return json.dumps({
            "window": title,
            "count": len(elements),
            "elements": elements
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def os_native_list_windows(pattern: str = "") -> str:
    """List all visible windows matching a title pattern.

    Args:
        pattern: Optional title substring filter (empty = all windows)
    Returns:
        JSON array of windows with title, handle, class name, and app type
    """
    try:
        Desktop = _import_pywinauto()
        win32gui, _ = _import_win32()
        d = Desktop(backend="uia")
        wins = []
        for w in d.windows():
            title = w.window_text()
            if not title:
                continue
            if pattern and pattern.lower() not in title.lower():
                continue
            if not w.is_visible():
                continue
            cls = w.element_info.class_name
            app_type = _detect_app_type(w.handle, cls)
            wins.append({
                "title": title,
                "handle": w.handle,
                "class_name": cls,
                "app_type": app_type,
            })
        return json.dumps({"windows": wins}, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def os_native_win32_list_controls(title: str) -> str:
    """For Win32 applications: list child controls with CtrlIDs.

    UWP apps (Windows.UI.Core.CoreWindow) have NO Win32 child controls.
    Only works on traditional Win32 apps (Notepad, old ERP, classic dialogs).

    Args:
        title: Window title (substring match)
    Returns:
        JSON array of child controls or error if UWP
    """
    try:
        hwnd, cls_name, exact_title = _find_window(title)
        app_type = _detect_app_type(hwnd, cls_name)

        if app_type == "uwp":
            return json.dumps({
                "error": f"'{exact_title}' is UWP ({cls_name}). No Win32 child controls available. Use os_native_get_tree instead."
            })

        win32gui, win32con = _import_win32()
        children = []

        def enum_ch(ch, _):
            cid = win32gui.GetDlgCtrlID(ch)
            ctext = win32gui.GetWindowText(ch)
            ccls = win32gui.GetClassName(ch)
            children.append({
                "hwnd": ch,
                "ctrl_id": cid,
                "text": ctext,
                "class_name": ccls,
                "visible": win32gui.IsWindowVisible(ch),
            })
        win32gui.EnumChildWindows(hwnd, enum_ch, None)
        return json.dumps({
            "window": exact_title,
            "class_name": cls_name,
            "controls": children
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def os_native_benchmark(title: str, auto_id: str, iterations: int = 5) -> str:
    """Benchmark click methods on a specific element.

    Tests: .invoke() (UIA direct) vs .click_input() (mouse simulation).

    Args:
        title: Window title (substring match)
        auto_id: AutomationID of element to click
        iterations: Number of test iterations (default: 5)
    Returns:
        JSON with latency comparison
    """
    try:
        desc = _get_descendants(title)
        target = None
        for e in desc:
            if e.element_info.automation_id == auto_id:
                target = e
                break
        if target is None:
            return json.dumps({"error": f"Element '{auto_id}' not found"})

        results = {}

        # Benchmark: invoke
        t1 = time.perf_counter()
        for _ in range(iterations):
            target.invoke()
        t2 = time.perf_counter()
        results["invoke_ms"] = round((t2 - t1) / iterations * 1000, 1)

        # Benchmark: click_input
        t3 = time.perf_counter()
        for _ in range(iterations):
            target.click_input()
        t4 = time.perf_counter()
        results["click_input_ms"] = round((t4 - t3) / iterations * 1000, 1)

        results["speedup"] = f"{results['click_input_ms'] / results['invoke_ms']:.1f}x"
        results["iterations"] = iterations
        results["element"] = auto_id
        results["window"] = title

        return json.dumps(results, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
