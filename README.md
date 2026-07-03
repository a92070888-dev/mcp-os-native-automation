# MCP OS-Native Automation

**Sub-2ms Windows GUI automation — zero vision model tokens, zero latency, all app types.**

A production-grade MCP server that automates Windows applications using OS-native structural control instead of expensive vision-language models. Achieves **1.5ms per click** with **0 image tokens** — 733× faster and infinitely cheaper than screenshot-based approaches.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│                  MCP Client (Hermes)                │
│         calls mcp_os_native_* tools                │
└────────────────────┬───────────────────────────────┘
                     │ stdio
┌────────────────────▼───────────────────────────────┐
│              OS-Native MCP Server                   │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Tier 0.5    │  │  Tier 1     │  │  Tier 2     │ │
│  │ Win32       │  │  UIA        │  │  Win32      │ │
│  │ SendInput   │  │  Invoke     │  │  PostMessage│ │
│  │ ~1.5ms      │  │  ~8ms      │  │  ~1ms       │ │
│  │ All apps    │  │  UWP/WinUI  │  │  Win32 only │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         └────────────────┼────────────────┘        │
│                    ┌─────▼─────┐                    │
│                    │ Auto-Route │                    │
│                    │ Detection  │                    │
│                    └───────────┘                    │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Predictive Async Cache (5,116× speedup)     │   │
│  │  Cold: 146ms → Hot: 0.029ms (29 µs)         │   │
│  └──────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

## Benchmark

| Method | Latency/click | Token cost | Position Stable | App types |
|--------|:------------:|:----------:|:---------------:|:---------:|
| MCP Screenshot + click | ~1,100ms | Very high | Fragile | All |
| UIA click_input | ~200ms | Near-zero | Stable | All UIA |
| **Win32 SendInput (foreground)** | **~1.5ms** | **Zero** | **100%** | **All** |
| UIA invoke + cache hit | **~8ms** | Near-zero | 100% | UWP/WinUI |
| Win32 PostMessage | **~1ms** | Zero | 100% | Win32 only |
| COM automation (Office) | **~0.1ms** | **Zero** | **100%** | Office apps |

## Features

### 🚀 Zero-Allocation SendInput (~1.5ms)
Win32 SendInput with pre-allocated buffer, single kernel call for all 3 events. Works on **all** window types.

### 🎯 UIA InvokePattern (~8ms)
Direct COM invocation via UI Automation tree. Works on background/minimized windows.

### ⚡ Predictive Async Cache (5,116×)
Cold: 146ms → Hot: 0.029ms (29 µs). Eliminates the descendants() scan.

### 🏢 COM Automation (Office)
Native COM for PowerPoint, Word, Excel at ~0.1ms. Hybrid: COM for content, UIA+SendInput for ribbon.

## Quick Start

```bash
pip install pywinauto pywin32
git clone https://github.com/a92070888-dev/mcp-os-native-automation.git
cd mcp-os-native-automation
pip install -r requirements.txt
```

Add to Hermes config (`~/.hermes/config.yaml`):
```yaml
mcp_servers:
  os-native:
    command: "C:\\Users\\<USER>\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe"
    args: ["C:\\path\\to\\mcp-os-native-automation\\server.py"]
```

## Available Tools

| Tool | Description |
|------|-------------|
| `os_native_list_windows` | List all visible windows by title pattern |
| `os_native_analyze_window` | Full analysis: app type, buttons, recommended method |
| `os_native_click` | Click button by AutomationID (auto-routes invoke/click) |
| `os_native_read` | Read text from UIA element |
| `os_native_get_tree` | Full UIA tree as structured JSON |
| `os_native_win32_list_controls` | Win32 child controls with CtrlIDs |
| `os_native_benchmark` | Speed test `.invoke()` vs `.click_input()` |

## License

MIT

---

**Part of the [Hermes Agent](https://hermes-agent.nousresearch.com) ecosystem.**


---

## 💼 Commercial Use

Need custom automation for your enterprise ERP, healthcare, or RPA systems? We offer:
- Custom MCP tool development
- Legacy system integration (Win32, Delphi, PowerBuilder, Java)
- Private licensing and support

**Contact:** [Open a B2B inquiry](https://github.com/a92070888-dev/mcp-os-native-automation/issues/new?labels=commercial&template=b2b-inquiry.md) or email a92070888@gmail.com
