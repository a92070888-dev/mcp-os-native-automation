"""Comprehensive tests for FEOM Open-Core MCP Server."""
import sys, os, ast, json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_server_syntax():
    """Verify server.py has valid Python syntax."""
    with open("server.py") as f:
        ast.parse(f.read())

def test_requirements_complete():
    """Verify all required packages are listed."""
    with open("requirements.txt") as f:
        deps = f.read().lower()
    for pkg in ["pywinauto", "pywin32", "mcp", "pydantic"]:
        assert pkg in deps, f"Missing: {pkg}"

def test_readme_sections():
    """Verify README has all required sections."""
    with open("README.md") as f:
        content = f.read()
    sections = [
        "Front-End Operation Master",
        "Feature Matrix",
        "Hardware Requirements",
        "Deterministic",
        "Commercial",
        "pricing"
    ]
    for s in sections:
        assert s.lower() in content.lower(), f"Missing section: {s}"

def test_mcp_tools_registered():
    """Verify all MCP tools are registered in server.py."""
    with open("server.py") as f:
        content = f.read()
    tools = ["feom_click", "feom_uia_invoke", "feom_launch", "feom_list_windows"]
    for t in tools:
        assert t in content, f"Missing tool: {t}"

def test_no_pro_ip_in_open_core():
    """Verify no Pro IP is accidentally in the open-core code."""
    with open("server.py") as f:
        content = f.read()
    pro_markers = ["AttachThreadInput", "zero.alloc", "ultra_click", "_input_array", "DPI matrix"]
    for m in pro_markers:
        assert m not in content, f"Pro IP leaked: {m}"
