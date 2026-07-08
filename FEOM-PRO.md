# FEOM Pro Edition

> Commercial add-ons for the FEOM Open-Core MCP Server.

## Overview

FEOM follows an **Open-Core** model:

| Edition | Price | What You Get |
|:--------|:-----:|:-------------|
| 🟡 **Open-Core** (this repo) | **Free** | 4 core MCP tools: click, UIA invoke, launch, list windows. MIT license. |
| 🟢 **Pro Plugin** | **$14.99/mo** | UltraClick zero-alloc engine, anti-crash focus defense, DPI compensation matrix |
| 🟢 **SDK License** | **$499/yr** | Full source access, unlimited developers, priority support |
| 🔵 **Enterprise** | **$3K-$10K** | Custom audit, runbook, training, multi-monitor stabilization |

## Pro Features (Not in Open-Core)

| Feature | Open-Core | Pro |
|:--------|:---------:|:---:|
| feom_click (SendInput) | ✅ Standard ~4ms | ⚡ Zero-alloc UltraClick <1ms |
| feom_uia_invoke | ✅ Basic ~8ms | ⚡ Win32 PostMessage ~1ms |
| feom_launch | ✅ | ✅ |
| feom_list_windows | ✅ Basic ~75ms | 🚀 Predictive cache <1ms |
| Multi-monitor DPI | ❌ Static coords | ✅ Dynamic scaling matrix |
| Taskbar auto-recovery | ❌ Fixed offsets | ✅ Icon vector tracking |
| Input pipeline optimization | ❌ Raw streams | ✅ Clipboard parallel (-71%) |
| Anti-crash focus defense | ❌ | ✅ |
| AttachThreadInput | ❌ Pro only | ✅ |

## Quick Start (Pro)

```bash
pip install feom-pro
# or download from releases
python server-pro.py
```

## License

Open-Core: MIT
Pro: Commercial license (see EULA)
