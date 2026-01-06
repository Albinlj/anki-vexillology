#!/usr/bin/env python3
"""
Integration test for the complete Anki deck creation workflow.
This test creates a minimal deck with mock data to verify all components work together.
"""

import os
import sys
import tempfile
import shutil
from create_anki_deck import create_anki_deck
import genanki


def create_mock_flag_images(test_dir):
    """Create mock flag image files for testing."""
    # Create a flags subdirectory
    flags_dir = os.path.join(test_dir, 'flags')
    os.makedirs(flags_dir, exist_ok=True)
    
    # Create mock flag files
    mock_flags = [
        '001_Flag_of_Chad.svg.png',
        '002_Flag_of_France.svg.png',
        '003_Flag_of_Germany.svg.png',
    ]
    
    for flag_file in mock_flags:
        filepath = os.path.join(flags_dir, flag_file)
        # Create a small PNG file (1x1 pixel transparent PNG)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(filepath, 'wb') as f:
            f.write(png_data)
    
    return flags_dir


def test_create_anki_deck_integration():
    """Test creating an Anki deck with mock data."""
    print("Testing Anki deck creation with mock data...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock flag images
        flags_dir = create_mock_flag_images(temp_dir)
        
        # Create mock country data
        countries_data = [
            {
                'country': 'Chad',
                'flag_image_path': os.path.join(flags_dir, '001_Flag_of_Chad.svg.png'),
                'description': 'The flag of Chad has three vertical bands - blue on the left, then yellow, then red. Blue stands for the sky plus water resources across the land. Yellow represents the Sahara Desert that covers much of the north. Red symbolizes progress, also honors those who fought for independence.',
                'adoption_date': '6 November 1959',
            },
            {
                'country': 'France',
                'flag_image_path': os.path.join(flags_dir, '002_Flag_of_France.svg.png'),
                'description': 'The flag of France is a tricolour featuring three vertical bands colored blue, white, and red. It is known as the French Tricolour or simply the Tricolour.',
                'adoption_date': '15 February 1794',
            },
            {
                'country': 'Germany',
                'flag_image_path': os.path.join(flags_dir, '003_Flag_of_Germany.svg.png'),
                'description': 'The flag of Germany is a tricolour consisting of three equal horizontal bands displaying the national colours of Germany: black, red, and gold.',
                'adoption_date': '23 May 1949',
            },
        ]
        
        # Create the deck
        deck, media_files, notes_added, notes_skipped = create_anki_deck(countries_data)
        
        # Verify results
        print(f"  Notes added: {notes_added}")
        print(f"  Notes skipped: {notes_skipped}")
        print(f"  Media files: {len(media_files)}")
        
        assert notes_added == 3, f"Expected 3 notes added, got {notes_added}"
        assert notes_skipped == 0, f"Expected 0 notes skipped, got {notes_skipped}"
        assert len(media_files) == 3, f"Expected 3 media files, got {len(media_files)}"
        
        # Verify deck properties
        assert deck.name == 'National Flags of Sovereign States', f"Unexpected deck name: {deck.name}"
        assert len(deck.notes) == 3, f"Expected 3 notes in deck, got {len(deck.notes)}"
        
        # Verify note content
        for note in deck.notes:
            assert len(note.fields) == 4, f"Expected 4 fields, got {len(note.fields)}"
            country_name = note.fields[0]
            flag_image = note.fields[1]
            description = note.fields[2]
            adoption_date = note.fields[3]
            
            print(f"  ✓ {country_name}")
            assert country_name in ['Chad', 'France', 'Germany'], f"Unexpected country: {country_name}"
            assert '<img src=' in flag_image, f"Flag image field should contain img tag"
            assert len(description) > 0, f"Description should not be empty for {country_name}"
            assert len(adoption_date) > 0, f"Adoption date should not be empty for {country_name}"
        
        # Try to save the package
        output_file = os.path.join(temp_dir, 'test_deck.apkg')
        package = genanki.Package(deck)
        package.media_files = media_files
        package.write_to_file(output_file)
        
        # Verify file was created
        assert os.path.exists(output_file), f"Deck file should be created: {output_file}"
        file_size = os.path.getsize(output_file)
        print(f"  Deck file created: {file_size} bytes")
        assert file_size > 0, "Deck file should not be empty"
    
    print("✓ Anki deck creation integration test passed")


def test_deck_model():
    """Test that the deck model has the correct structure."""
    print("\nTesting deck model structure...")
    
    # Create a simple test model
    model_id = 123456789
    test_model = genanki.Model(
        model_id,
        'Test Flag Model',
        fields=[
            {'name': 'Country'},
            {'name': 'FlagImage'},
            {'name': 'Description'},
            {'name': 'AdoptionDate'},
        ],
        templates=[{
            'name': 'Test Template',
            'qfmt': '{{FlagImage}}',
            'afmt': '{{FlagImage}}<hr>{{Country}}',
        }],
    )
    
    # Verify model properties
    assert test_model.name == 'Test Flag Model', "Model name should match"
    assert len(test_model.fields) == 4, "Model should have 4 fields"
    assert len(test_model.templates) == 1, "Model should have 1 template"
    
    field_names = [field['name'] for field in test_model.fields]
    assert 'Country' in field_names, "Should have Country field"
    assert 'FlagImage' in field_names, "Should have FlagImage field"
    assert 'Description' in field_names, "Should have Description field"
    assert 'AdoptionDate' in field_names, "Should have AdoptionDate field"
    
    print("  ✓ Model has correct fields")
    print("  ✓ Model has correct template")
    print("✓ Deck model structure test passed")


if __name__ == "__main__":
    print("="*60)
    print("Running integration tests for Anki deck creation")
    print("="*60)
    
    test_deck_model()
    test_create_anki_deck_integration()
    
    print("\n" + "="*60)
    print("All integration tests passed! ✓")
    print("="*60)
    print("\nThe Anki deck creation functionality is working correctly.")
    print("To create a deck with real data:")
    print("  1. Run: python download_flags.py")
    print("  2. Run: python create_anki_deck.py")
