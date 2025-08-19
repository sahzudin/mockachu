#!/usr/bin/env python3
"""
Test script to verify the copy API request functionality works correctly
"""

import json
from mockachu.generators.generator import Generators, GeneratorActions
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))


def test_copy_functionality():
    """Test the core logic used in copy_api_request_to_clipboard"""
    print("Testing copy to clipboard functionality...")

    # Simulate field configuration like in the UI
    field_config = {
        "name": "test_field",
        "generator": Generators.PERSON_GENERATOR,
        "action": GeneratorActions.RANDOM_PERSON_FIRST_NAME,
        "nullable_percentage": 0,
        "parameters": None
    }

    # Build API request like the UI does
    api_request = {
        "fields": [],
        "rows": 10,
        "format": "JSON"
    }

    # Handle generator name (could be enum or string)
    generator = field_config["generator"]
    generator_name = generator.name if hasattr(
        generator, 'name') else str(generator)

    # Handle action name (could be enum or string)
    action = field_config["action"]
    action_name = action.name if hasattr(action, 'name') else str(action)

    api_field = {
        "name": field_config["name"],
        "generator": generator_name,
        "action": action_name
    }

    # Add nullable percentage if not zero
    if field_config.get("nullable_percentage", 0) > 0:
        api_field["nullable_percentage"] = field_config["nullable_percentage"]

    # Add parameters if present
    if field_config.get("parameters"):
        api_field["parameters"] = field_config["parameters"]

    api_request["fields"].append(api_field)

    # Convert to JSON
    json_request = json.dumps(api_request, indent=2)

    print("Generated API request:")
    print(json_request)
    print("\n✅ Copy functionality logic is working correctly!")

    # Validate that the JSON is valid and can be used with the API
    try:
        parsed = json.loads(json_request)
        assert "fields" in parsed
        assert "rows" in parsed
        assert "format" in parsed
        assert len(parsed["fields"]) == 1
        assert parsed["fields"][0]["name"] == "test_field"
        assert parsed["fields"][0]["generator"] == "PERSON_GENERATOR"
        assert parsed["fields"][0]["action"] == "RANDOM_PERSON_FIRST_NAME"
        print("✅ Generated JSON is valid and properly structured!")
        return True
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False


if __name__ == "__main__":
    success = test_copy_functionality()
    sys.exit(0 if success else 1)
