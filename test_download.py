#!/usr/bin/env python3
"""
Test script to verify the flag download functionality with mock data.
"""

from download_flags import extract_flag_images, sanitize_filename
import os

# Mock HTML content that simulates the Wikipedia page structure
MOCK_HTML = """
<html>
<body>
<table class="wikitable">
  <tr>
    <th>Country</th>
    <th>Flag</th>
  </tr>
  <tr>
    <td>Afghanistan</td>
    <td><img src="//upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Afghanistan.svg/125px-Flag_of_Afghanistan.svg.png" 
         alt="Flag of Afghanistan" width="125" height="83" /></td>
  </tr>
  <tr>
    <td>Albania</td>
    <td><img src="//upload.wikimedia.org/wikipedia/commons/thumb/3/36/Flag_of_Albania.svg/140px-Flag_of_Albania.svg.png" 
         alt="Flag of Albania" width="140" height="100" /></td>
  </tr>
  <tr>
    <td>Algeria</td>
    <td><img src="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/150px-Flag_of_Algeria.svg.png" 
         alt="Flag of Algeria" width="150" height="100" /></td>
  </tr>
</table>
</body>
</html>
"""


def test_extract_flag_images():
    """Test flag image extraction from HTML."""
    print("Testing flag image extraction...")
    flag_images = extract_flag_images(MOCK_HTML)
    
    print(f"Found {len(flag_images)} flag images")
    assert len(flag_images) == 3, f"Expected 3 images, found {len(flag_images)}"
    
    # Check that URLs are properly formatted
    for img in flag_images:
        print(f"  - {img['alt']}: {img['url']}")
        assert img['url'].startswith('https://'), f"URL should start with https://"
        assert 'Flag' in img['url'], f"URL should contain 'Flag'"
    
    print("✓ Flag image extraction test passed")


def test_sanitize_filename():
    """Test filename sanitization."""
    print("\nTesting filename sanitization...")
    
    test_cases = [
        ("Flag of Afghanistan", "Flag of Afghanistan"),
        ("Flag: Test/Name", "Flag_ Test_Name"),
        ('Flag "with" quotes', "Flag _with_ quotes"),
        ("Flag<>Test", "Flag__Test"),
    ]
    
    for input_name, expected_start in test_cases:
        result = sanitize_filename(input_name)
        print(f"  '{input_name}' -> '{result}'")
        assert '/' not in result, "Should not contain /"
        assert ':' not in result, "Should not contain :"
        assert '<' not in result, "Should not contain <"
        assert '>' not in result, "Should not contain >"
    
    print("✓ Filename sanitization test passed")


if __name__ == "__main__":
    print("="*60)
    print("Running tests for flag download functionality")
    print("="*60)
    
    test_extract_flag_images()
    test_sanitize_filename()
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    print("\nNote: This test uses mock HTML data.")
    print("To download actual flags, run: python download_flags.py")
    print("(Requires internet connection)")
