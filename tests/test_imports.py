"""Basic import and smoke tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-os-native-upload'))

def test_import_server():
    from mcp_os_native import server
    assert hasattr(server, 'mcp')

def test_import_ultraclick():
    import os_native_ultraclick
    assert hasattr(os_native_ultraclick, 'fast_click')

def test_requirements_readable():
    p = os.path.join(os.path.dirname(__file__), '..', 'mcp-os-native-upload', 'requirements.txt')
    with open(p) as f:
        lines = f.read().strip().split('\n')
    assert len(lines) >= 3
    assert any('pywinauto' in l for l in lines)
