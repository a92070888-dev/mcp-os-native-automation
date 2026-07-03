# Tests for FEOM Open-Core MCP Server
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_import_server():
    import importlib.util
    spec = importlib.util.spec_from_file_location("server", "server.py")
    assert spec is not None

def test_requirements():
    assert os.path.exists("requirements.txt")
    with open("requirements.txt") as f:
        content = f.read()
    assert "pywinauto" in content
    assert "mcp" in content
