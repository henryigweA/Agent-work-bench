import pytest
from agent_workbench.tools import calculate, run_tool

def test_calculate_operator_precedence():
    assert calculate("2 + 3 * 4")["result"] == 14

def test_calculate_parentheses():
    assert calculate("(10 + 5) * 2")["result"] == 30

def test_calculate_rejects_code_execution():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('echo unsafe')")

def test_unknown_tool_is_rejected():
    result = run_tool("run_shell_command", {})
    assert result["ok"] is False
