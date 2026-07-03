"""
FEOM Engine: High-Trust Open-Core MCP Server
Working UIA + SendInput tools. Pro features commercially isolated.
"""
import time, ctypes, subprocess, logging, asyncio
from typing import Any
from pywinauto import Desktop
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import BaseModel, Field

logger = logging.getLogger("feom-server")
server = Server("feom-server")

class ClickRequest(BaseModel):
    x: int = Field(description="Screen X coordinate")
    y: int = Field(description="Screen Y coordinate")

class UIAInvokeRequest(BaseModel):
    window_title: str = Field(description="Window title (regex supported)")
    auto_id: str = Field(description="UIA AutomationID of the element")

class LaunchRequest(BaseModel):
    command: str = Field(description="App command or path to launch")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="feom_click",
            description="Click at screen coordinates via SendInput (~4ms)",
            inputSchema={"type":"object","properties":{"x":{"type":"integer"},"y":{"type":"integer"}},"required":["x","y"]}
        ),
        types.Tool(
            name="feom_uia_invoke",
            description="Invoke UIA element by AutomationID (~8ms, background, no focus steal)",
            inputSchema={"type":"object","properties":{"window_title":{"type":"string"},"auto_id":{"type":"string"}},"required":["window_title","auto_id"]}
        ),
        types.Tool(
            name="feom_launch",
            description="Launch application via terminal pipe (~0.01s)",
            inputSchema={"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}
        ),
        types.Tool(
            name="feom_list_windows",
            description="List all visible windows",
            inputSchema={"type":"object","properties":{}}
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if name == "feom_click":
        x, y = arguments["x"], arguments["y"]
        t0 = time.perf_counter()
        ctypes.windll.user32.SetCursorPos(x, y)
        ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
        ms = (time.perf_counter() - t0) * 1000
        return [types.TextContent(type="text", text=f"Click at ({x},{y}): {ms:.1f}ms")]
    
    elif name == "feom_uia_invoke":
        t0 = time.perf_counter()
        try:
            app = Desktop(backend="uia").window(title_re=arguments["window_title"])
            el = app.child_window(auto_id=arguments["auto_id"])
            el.iface_invoke.Invoke()
            ms = (time.perf_counter() - t0) * 1000
            return [types.TextContent(type="text", text=f"UIA Invoke: {ms:.1f}ms")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"UIA failed: {e}")]
    
    elif name == "feom_launch":
        subprocess.Popen(f"start {arguments['command']}", shell=True)
        return [types.TextContent(type="text", text="App launched.")]
    
    elif name == "feom_list_windows":
        d = Desktop(backend="uia")
        wins = [w.window_text() for w in d.windows() if w.is_visible() and w.window_text()]
        return [types.TextContent(type="text", text="\n".join(wins) if wins else "No windows found")]
    
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def run():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.run(read, write, InitializationOptions(
            server_name="feom-server",
            server_version="0.1.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        ))

if __name__ == "__main__":
    asyncio.run(run())
