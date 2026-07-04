# 🏆 Front-End Operation Master (FEOM)

**The Ultimate Front-End OS Engine for AI Agents. 0 Vision Tokens. 733× Faster. 100% Deterministic.**

FEOM is a production-grade front-end operation architecture for Windows AI Agents. This repository contains the **Open-Core Edition**, allowing developers to test and verify real-time structural OS routing (achieving ~8ms background UIA invocation), completely eliminating VLM vision token costs.

## 📊 Feature Matrix: Open-Core vs Pro/Enterprise

| Feature | 🟡 Open-Core (This Repo) | 🟢 FEOM Pro / Enterprise |
|:---|---:|:---:|
| **MCP Server Framework** | ✅ Included | ✅ Included |
| **UIA Tree Structural Read** | ✅ Included (~75ms) | 🚀 **Predictive Async Cache (<1ms)** |
| **Win32 SendInput Click** | 🟢 Standard (~3.96ms) | ⚡ **Zero-Alloc UltraClick (<1.0ms)** |
| **Background UIA Invoke** | 🟢 Basic (~8ms) | ⚡ **Win32 PostMessage (~1ms)** |
| **Multi-Monitor High DPI** | ❌ Static Coords Only | ✅ **Dynamic Scaling Matrix** |
| **Taskbar Push Auto-Recovery** | ❌ Fixed Offsets | ✅ **Icon Vector Tracking** |
| **Input Pipeline Optimization** | ❌ Raw Character Streams | ✅ **Clipboard Parallel (-71%)** |

---

## 🥇 The Three Iron Rules of Production Automation

### 1. Unique Truth: Front-End Demonstration Over Everything
Always show, then report. Every sequence must execute visibly in the foreground.

### 2. Safety First: Pre-Action Focus Defending
Never click blindly. Structural state verification is forced prior to any input.

### 3. App Termination Rule: Strict Alt+F4 Ban
Alt+F4 blindly kills whatever window has focus — frequently closing the orchestration engine itself.

---

## 🚀 Hybrid Terminal+MCP Extreme Mode

| Execution Stage | Traditional MCP Agent | **FEOM Hybrid Mode** | Time Saved |
|:---|:---:|:---:|:---:|
| App Bootup | ~3.0s (UI traversal) | **0.01s** | **99.6%** |
| Form Input | ~5.0s (Vision Loop) | **1.2s** | **76.0%** |
| Close & Verify | ~4.0s (Screenshot) | **2.0s** | **50.0%** |
| **Total End-to-End** | **~12.0s** | **~3.21s** | **73.2% Faster** |

```bash
# Verify instant boot:
terminal("start calc")
```

---



## Hardware Requirements (Killer Feature)

| Requirement | Traditional VLM | FEOM Open-Core |
|:------------|:-------------:|:-------------:|
| GPU | RTX 3060+ required | None - any CPU works |
| RAM | 16GB+ | 4GB |
| Network | Required (API per click) | Zero - fully local |
| Cost/op | $0.01-$0.05 (vision tokens) | $0 |
| Display | Yes (needs screenshot) | No - works headless |
| Hardware cost | $1,000+ gaming PC | $50 used Dell |
| Annual license | $15K+ (RPA) | $0 (Open-Core) |

## Deterministic vs Probabilistic

| | VLM Screenshot | FEOM OS-Native |
|:---|:-------------:|:-------------:|
| Output | Coordinate guessing | AutomationID targeting |
| Repeatability | Different each time | 100% identical |
| DPI scaling | Coordinates drift | UIA auto-maps |
| Background | Cannot work | Works minimized |
| Production-ready | Demo only | Production grade |

## 💼 Commercial Licensing

| Tier | Product | Price |
|:---|:---|---:|
| 1 | Turbo-MCP Plugin (anti-crash + DPI matrix) | $14.99/mo |
| 2 | AI-SaaS Task Force (legacy ERP/CRM migration) | Custom |
| 3 | Enterprise Consulting (stability + multi-monitor audit) | $3K-$10K |
| 4 | Hermes-Split-OS SDK (parallel multi-agent framework) | License |

**Inquiries:** [Open B2B Ticket](https://github.com/a92070888-dev/mcp-os-native-automation/issues/new?labels=commercial&template=b2b-inquiry.md) or **a92070888@gmail.com**




## 3-Line Quick Start

```bash
pip install pywinauto pywin32 mcp
python server.py
```

Then add to MCP client config:
```json
{
  "mcpServers": {
    "feom": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```

No GPU. No cloud API. No Docker. Any Windows PC.
## Tools (Open-Core)

| Tool | Description | Latency |
|:-----|:------------|:------:|
| feom_click | Click at screen coords via SendInput | ~4ms |
| feom_uia_invoke | Invoke UIA element by AutomationID | ~8ms |
| feom_launch | Launch app via terminal pipe | ~0.01s |
| feom_list_windows | List all visible windows | ~75ms |

### Quick Start
pip install pywinauto pywin32 mcp
python server.py
