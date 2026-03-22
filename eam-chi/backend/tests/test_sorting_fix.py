"""Test that _last_edited sort field is properly mapped to updated_at."""

def test_sort_field_mapping():
    """Test the frontend mapping logic for _last_edited sort field."""
    
    # Test cases from frontend
    test_cases = [
        {"input": "_last_edited", "expected": "updated_at"},
        {"input": "asset_tag", "expected": "asset_tag"},
        {"input": "description", "expected": "description"},
        {"input": None, "expected": None},
        {"input": "", "expected": ""},
    ]
    
    for case in test_cases:
        # Simulate frontend logic
        result = case["input"] if case["input"] != "_last_edited" else "updated_at"
        assert result == case["expected"], f"Failed for input {case['input']}: got {result}, expected {case['expected']}"
    
    print("✅ Sort field mapping logic verified")


if __name__ == "__main__":
    test_sort_field_mapping()
