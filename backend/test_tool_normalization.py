"""
Test tool_calls normalization for OpenAI format compliance.
"""
import json
from app.agent.runner import AgentRunner


def test_normalize_tool_calls():
    """Test that tool_calls are normalized from database format to OpenAI format."""
    # Create a mock AgentRunner (without OpenAI client)
    runner = AgentRunner(openai_api_key="test-key")

    # Test 1: Database format (from conversation history)
    database_format = [
        {
            "tool_call_id": "call_abc123",
            "tool_name": "add_task",
            "arguments": {
                "user_id": "user_123",
                "title": "Buy groceries",
                "description": "Get milk and eggs"
            },
            "result": {"success": True, "task_id": 42},
            "success": True
        }
    ]

    normalized = runner._normalize_tool_calls(database_format)

    assert len(normalized) == 1
    assert normalized[0]["id"] == "call_abc123"
    assert normalized[0]["type"] == "function"
    assert normalized[0]["function"]["name"] == "add_task"

    # Arguments should be JSON string
    arguments = normalized[0]["function"]["arguments"]
    assert isinstance(arguments, str)

    # Parse to verify it's valid JSON
    parsed_args = json.loads(arguments)
    assert parsed_args["title"] == "Buy groceries"

    print("✅ Test 1 PASSED: Database format normalized correctly")

    # Test 2: OpenAI format (already correct)
    openai_format = [
        {
            "id": "call_xyz789",
            "type": "function",
            "function": {
                "name": "list_tasks",
                "arguments": '{"user_id": "user_123"}'
            }
        }
    ]

    normalized = runner._normalize_tool_calls(openai_format)

    assert len(normalized) == 1
    assert normalized[0]["id"] == "call_xyz789"
    assert normalized[0]["type"] == "function"
    assert normalized[0]["function"]["name"] == "list_tasks"

    print("✅ Test 2 PASSED: OpenAI format preserved correctly")

    # Test 3: Empty tool_calls
    assert runner._normalize_tool_calls([]) == []
    assert runner._normalize_tool_calls(None) == []

    print("✅ Test 3 PASSED: Empty tool_calls handled correctly")

    # Test 4: Single dict (not list)
    single_dict = {
        "tool_call_id": "call_single",
        "tool_name": "delete_task",
        "arguments": {"task_id": 5}
    }

    normalized = runner._normalize_tool_calls(single_dict)

    assert len(normalized) == 1
    assert normalized[0]["id"] == "call_single"
    assert normalized[0]["function"]["name"] == "delete_task"

    print("✅ Test 4 PASSED: Single dict converted to list and normalized")

    # Test 5: Malformed entries skipped
    malformed = [
        {"random": "data"},  # Missing required fields
        {"tool_call_id": "call_abc", "tool_name": "test"},  # Valid
        "not a dict",  # Invalid type
    ]

    normalized = runner._normalize_tool_calls(malformed)

    assert len(normalized) == 1  # Only the valid one
    assert normalized[0]["id"] == "call_abc"

    print("✅ Test 5 PASSED: Malformed entries skipped gracefully")

    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED - Tool normalization working correctly!")
    print("="*60)


if __name__ == "__main__":
    test_normalize_tool_calls()
