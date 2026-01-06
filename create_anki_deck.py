#!/usr/bin/env python3
"""
Create an Anki deck with national flags.
Source: https://en.wikipedia.org/wiki/List_of_national_flags_of_sovereign_states
"""

import os
import sys
import re
import requests
from bs4 import BeautifulSoup
import genanki
import random
import time

# Configuration
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_national_flags_of_sovereign_states"
FLAGS_DIR = "flags"
OUTPUT_FILE = "National_Flags.apkg"
REQUEST_DELAY = 0.5  # Delay between requests to be respectful to Wikipedia's servers
MAX_DESCRIPTION_PARAGRAPHS = 2  # Maximum number of paragraphs to include in description
MAX_DESCRIPTION_LENGTH = 500  # Maximum length of description in characters


def get_wikipedia_page():
    """Fetch the Wikipedia page content."""
    print(f"Fetching page: {WIKIPEDIA_URL}")
    headers = {
        'User-Agent': 'AnkiVexillologyBot/1.0 (Educational purposes; creating flashcards)'
    }
    response = requests.get(WIKIPEDIA_URL, headers=headers)
    response.raise_for_status()
    return response.text


def extract_country_flag_info(html_content):
    """Extract country names and basic flag information from the Wikipedia page."""
    soup = BeautifulSoup(html_content, 'html.parser')
    countries_info = []
    
    # Find all tables with class 'wikitable'
    tables = soup.find_all('table', class_='wikitable')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Try to find country name (usually in first or second cell)
                country_name = None
                flag_img = None
                
                # Look for the flag image
                for cell in cells:
                    img = cell.find('img')
                    if img and img.get('src'):
                        width = img.get('width', '0')
                        try:
                            if int(width) >= 100:  # Filter out small icons
                                flag_img = img
                                break
                        except (ValueError, TypeError):
                            if 'Flag_of_' in img.get('src', ''):
                                flag_img = img
                                break
                
                # Look for country name - typically in a cell with a link
                if flag_img:
                    for cell in cells:
                        # Look for country name in links
                        links = cell.find_all('a')
                        for link in links:
                            text = link.get_text().strip()
                            # Skip very short text or common words
                            if len(text) > 3 and not text.lower() in ['flag', 'edit', 'view']:
                                country_name = text
                                break
                        if country_name:
                            break
                    
                    # If we have both country name and flag image, add to list
                    if country_name and flag_img:
                        img_alt = flag_img.get('alt', '')
                        countries_info.append({
                            'country': country_name,
                            'img_alt': img_alt,
                            'flag_img_url': flag_img.get('src', '')
                        })
    
    return countries_info


def get_flag_details(country_name):
    """Fetch detailed flag information from the country's flag page."""
    # Try to fetch the flag page
    flag_page_url = f"https://en.wikipedia.org/wiki/Flag_of_{country_name.replace(' ', '_')}"
    
    try:
        headers = {
            'User-Agent': 'AnkiVexillologyBot/1.0 (Educational purposes; creating flashcards)'
        }
        response = requests.get(flag_page_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract adoption date from infobox
        adoption_date = None
        infobox = soup.find('table', class_='infobox')
        if infobox:
            rows = infobox.find_all('tr')
            for row in rows:
                header = row.find('th')
                if header:
                    header_text = header.get_text().strip().lower()
                    if 'adopt' in header_text or 'design' in header_text:
                        data = row.find('td')
                        if data:
                            adoption_date = data.get_text().strip()
                            # Clean up the date text
                            adoption_date = re.sub(r'\[.*?\]', '', adoption_date)  # Remove citations
                            adoption_date = adoption_date.strip()
                            break
        
        # Extract description from the first few paragraphs
        description_parts = []
        content = soup.find('div', class_='mw-parser-output')
        if content:
            # Get first few paragraphs after infobox
            paragraphs = content.find_all('p', recursive=False)
            for p in paragraphs[:5]:  # Look at first 5 paragraphs
                text = p.get_text().strip()
                # Skip short paragraphs or those without substance
                if len(text) > 50 and not text.startswith('Coordinates:'):
                    # Clean up the text
                    text = re.sub(r'\[.*?\]', '', text)  # Remove citations
                    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                    description_parts.append(text)
                    if len(' '.join(description_parts)) > 300:  # Get enough context
                        break
        
        description = ' '.join(description_parts[:MAX_DESCRIPTION_PARAGRAPHS]) if description_parts else None
        
        # Truncate description if too long
        if description and len(description) > MAX_DESCRIPTION_LENGTH:
            # Try to cut at sentence boundary
            sentences = description[:MAX_DESCRIPTION_LENGTH].split('. ')
            if len(sentences) > 1:
                description = '. '.join(sentences[:-1]) + '.'
            else:
                description = description[:MAX_DESCRIPTION_LENGTH] + '...'
        
        return {
            'adoption_date': adoption_date,
            'description': description
        }
    
    except Exception as e:
        print(f"  Warning: Could not fetch details for {country_name}: {e}")
        return None


def find_flag_image_file(country_info, flags_dir):
    """Find the corresponding flag image file for a country."""
    country_name = country_info['country']
    img_alt = country_info['img_alt']
    
    if not os.path.exists(flags_dir):
        return None
    
    # List all files in flags directory
    flag_files = os.listdir(flags_dir)
    
    # Try to match by country name or alt text
    for flag_file in flag_files:
        # Check if country name or cleaned version is in filename
        if country_name.lower().replace(' ', '_') in flag_file.lower():
            return os.path.join(flags_dir, flag_file)
        if img_alt and img_alt.lower().replace(' ', '_') in flag_file.lower():
            return os.path.join(flags_dir, flag_file)
    
    # Try partial match
    for flag_file in flag_files:
        # Check if main word from country name is in filename
        main_words = [w for w in country_name.split() if len(w) > 3]
        for word in main_words:
            if word.lower() in flag_file.lower():
                return os.path.join(flags_dir, flag_file)
    
    return None


def create_anki_deck(countries_data):
    """Create an Anki deck with flag flashcards."""
    
    # Create a unique model ID
    model_id = random.randrange(1 << 30, 1 << 31)
    
    # Define the note model
    flag_model = genanki.Model(
        model_id,
        'Flag Model',
        fields=[
            {'name': 'Country'},
            {'name': 'FlagImage'},
            {'name': 'Description'},
            {'name': 'AdoptionDate'},
        ],
        templates=[
            {
                'name': 'Flag Recognition',
                'qfmt': '<div style="text-align: center; font-size: 24px; margin: 20px;">{{FlagImage}}</div>',
                'afmt': '''<div style="text-align: center; font-size: 24px; margin: 20px;">{{FlagImage}}</div>
<hr id="answer">
<div style="text-align: center; font-size: 36px; font-weight: bold; color: #2c3e50; margin: 20px;">{{Country}}</div>
{{#Description}}
<div style="text-align: left; font-size: 18px; line-height: 1.6; margin: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db;">
  {{Description}}
</div>
{{/Description}}
{{#AdoptionDate}}
<div style="text-align: center; font-size: 16px; color: #7f8c8d; margin: 15px;">
  <strong>Adopted:</strong> {{AdoptionDate}}
</div>
{{/AdoptionDate}}''',
            },
        ],
        css='''
.card {
  font-family: Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  background-color: #ffffff;
}
img {
  max-width: 400px;
  max-height: 300px;
  border: 2px solid #34495e;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
'''
    )
    
    # Create a deck
    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, 'National Flags of Sovereign States')
    
    # Collect media files
    media_files = []
    
    # Add notes for each country
    notes_added = 0
    notes_skipped = 0
    
    for country_data in countries_data:
        country_name = country_data['country']
        flag_image_path = country_data.get('flag_image_path')
        
        if not flag_image_path or not os.path.exists(flag_image_path):
            print(f"  Skipping {country_name}: No flag image found")
            notes_skipped += 1
            continue
        
        # Get the filename for embedding in the note
        flag_filename = os.path.basename(flag_image_path)
        
        # Create the note
        description = country_data.get('description', '')
        adoption_date = country_data.get('adoption_date', '')
        
        note = genanki.Note(
            model=flag_model,
            fields=[
                country_name,
                f'<img src="{flag_filename}">',
                description,
                adoption_date,
            ]
        )
        
        deck.add_note(note)
        media_files.append(flag_image_path)
        notes_added += 1
        print(f"  Added: {country_name}")
    
    return deck, media_files, notes_added, notes_skipped


def main():
    """Main function to orchestrate the Anki deck creation."""
    print("="*60)
    print("Creating Anki deck for national flags...")
    print("="*60)
    
    # Check if flags directory exists
    if not os.path.exists(FLAGS_DIR):
        print(f"\nError: Flags directory '{FLAGS_DIR}' not found!")
        print("Please run 'python download_flags.py' first to download flag images.")
        sys.exit(1)
    
    # Count available flags
    flag_files = [f for f in os.listdir(FLAGS_DIR) if os.path.isfile(os.path.join(FLAGS_DIR, f))]
    print(f"Found {len(flag_files)} flag images in {FLAGS_DIR}/")
    
    if len(flag_files) == 0:
        print(f"\nError: No flag images found in '{FLAGS_DIR}'!")
        print("Please run 'python download_flags.py' first to download flag images.")
        sys.exit(1)
    
    # Fetch Wikipedia page
    print("\nFetching country information from Wikipedia...")
    try:
        html_content = get_wikipedia_page()
    except Exception as e:
        print(f"Error fetching Wikipedia page: {e}")
        sys.exit(1)
    
    # Extract country information
    print("Extracting country and flag information...")
    countries_info = extract_country_flag_info(html_content)
    print(f"Found {len(countries_info)} countries")
    
    if not countries_info:
        print("No countries found. Exiting.")
        sys.exit(1)
    
    # Match countries with flag images and fetch details
    print("\nMatching countries with flag images and fetching details...")
    countries_data = []
    
    for i, country_info in enumerate(countries_info, 1):
        country_name = country_info['country']
        print(f"[{i}/{len(countries_info)}] Processing {country_name}...")
        
        # Find the flag image file
        flag_image_path = find_flag_image_file(country_info, FLAGS_DIR)
        
        if flag_image_path:
            # Fetch detailed information
            details = get_flag_details(country_name)
            
            country_data = {
                'country': country_name,
                'flag_image_path': flag_image_path,
                'description': details.get('description', '') if details else '',
                'adoption_date': details.get('adoption_date', '') if details else '',
            }
            
            countries_data.append(country_data)
            
            # Be respectful to Wikipedia's servers
            time.sleep(REQUEST_DELAY)
        else:
            print(f"  Warning: Could not find flag image for {country_name}")
    
    print(f"\nSuccessfully processed {len(countries_data)} countries with flag images")
    
    # Create the Anki deck
    print("\nCreating Anki deck...")
    deck, media_files, notes_added, notes_skipped = create_anki_deck(countries_data)
    
    # Save the deck to a file
    print(f"\nSaving deck to {OUTPUT_FILE}...")
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(OUTPUT_FILE)
    
    # Summary
    print("\n" + "="*60)
    print("Anki deck creation complete!")
    print(f"Deck file: {OUTPUT_FILE}")
    print(f"Cards added: {notes_added}")
    print(f"Cards skipped: {notes_skipped}")
    print("="*60)
    print("\nTo use the deck:")
    print(f"1. Open Anki")
    print(f"2. File > Import")
    print(f"3. Select {OUTPUT_FILE}")
    print("="*60)


if __name__ == "__main__":
    main()
