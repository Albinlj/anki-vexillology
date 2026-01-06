#!/usr/bin/env python3
"""
Test script to verify the Anki deck creation functionality with mock data.
"""

from create_anki_deck import extract_country_flag_info, find_flag_image_file
import os
import tempfile

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
    <td><a href="/wiki/Afghanistan">Afghanistan</a></td>
    <td><img src="//upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Afghanistan.svg/125px-Flag_of_Afghanistan.svg.png" 
         alt="Flag of Afghanistan" width="125" height="83" /></td>
  </tr>
  <tr>
    <td><a href="/wiki/Albania">Albania</a></td>
    <td><img src="//upload.wikimedia.org/wikipedia/commons/thumb/3/36/Flag_of_Albania.svg/140px-Flag_of_Albania.svg.png" 
         alt="Flag of Albania" width="140" height="100" /></td>
  </tr>
  <tr>
    <td><a href="/wiki/Algeria">Algeria</a></td>
    <td><img src="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/150px-Flag_of_Algeria.svg.png" 
         alt="Flag of Algeria" width="150" height="100" /></td>
  </tr>
</table>
</body>
</html>
"""


def test_extract_country_flag_info():
    """Test country and flag information extraction from HTML."""
    print("Testing country and flag information extraction...")
    countries_info = extract_country_flag_info(MOCK_HTML)
    
    print(f"Found {len(countries_info)} countries")
    assert len(countries_info) >= 3, f"Expected at least 3 countries, found {len(countries_info)}"
    
    # Check that we have the expected fields
    for country in countries_info:
        print(f"  - {country['country']}: {country['img_alt']}")
        assert 'country' in country, "Should have country field"
        assert 'img_alt' in country, "Should have img_alt field"
        assert 'flag_img_url' in country, "Should have flag_img_url field"
        assert len(country['country']) > 0, "Country name should not be empty"
    
    print("✓ Country and flag information extraction test passed")


def test_find_flag_image_file():
    """Test finding flag image files."""
    print("\nTesting flag image file matching...")
    
    # Create a temporary directory with mock flag files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock flag files
        test_files = [
            "001_Flag_of_Afghanistan.png",
            "002_Flag_of_Albania.svg.png",
            "003_Flag_of_Algeria.svg.png",
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("mock image data")
        
        # Test matching
        test_cases = [
            {'country': 'Afghanistan', 'img_alt': 'Flag of Afghanistan', 'flag_img_url': ''},
            {'country': 'Albania', 'img_alt': 'Flag of Albania', 'flag_img_url': ''},
            {'country': 'Algeria', 'img_alt': 'Flag of Algeria', 'flag_img_url': ''},
        ]
        
        for country_info in test_cases:
            result = find_flag_image_file(country_info, temp_dir)
            print(f"  {country_info['country']} -> {os.path.basename(result) if result else 'Not found'}")
            assert result is not None, f"Should find image for {country_info['country']}"
            assert os.path.exists(result), f"Image file should exist: {result}"
    
    print("✓ Flag image file matching test passed")


def test_imports():
    """Test that all required modules can be imported."""
    print("\nTesting module imports...")
    
    try:
        import genanki
        print("  ✓ genanki imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import genanki: {e}")
        raise
    
    try:
        import requests
        print("  ✓ requests imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import requests: {e}")
        raise
    
    try:
        from bs4 import BeautifulSoup
        print("  ✓ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import BeautifulSoup: {e}")
        raise
    
    print("✓ All imports successful")


if __name__ == "__main__":
    print("="*60)
    print("Running tests for Anki deck creation functionality")
    print("="*60)
    
    test_imports()
    test_extract_country_flag_info()
    test_find_flag_image_file()
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    print("\nNote: This test uses mock HTML data.")
    print("To create an actual Anki deck, run: python create_anki_deck.py")
    print("(Requires downloaded flags and internet connection)")
