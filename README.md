# anki-vexillology

An Anki flashcard deck for learning national flags (vexillology).

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Download Flag Images

Run the download script to fetch all national flag images from Wikipedia:

```bash
python download_flags.py
```

The script will:
1. Fetch the list of national flags from Wikipedia
2. Extract flag image URLs
3. Download all flag images to the `flags/` directory
4. Display a summary of successful and failed downloads

All downloaded flag images will be saved in the `flags/` directory. Each image is prefixed with a number to maintain order and avoid filename conflicts.

### Step 2: Create the Anki Deck

After downloading the flags, create the Anki flashcard deck:

```bash
python create_anki_deck.py
```

The script will:
1. Fetch country information from Wikipedia
2. Match countries with downloaded flag images
3. Scrape detailed flag information (descriptions, symbolism, adoption dates)
4. Generate an Anki deck file (`National_Flags.apkg`)

The generated deck contains flashcards with:
- **Front**: Flag image
- **Back**: Country name, flag image, description (including symbolism and meaning), and adoption date

### Step 3: Import into Anki

1. Open Anki
2. Go to File > Import
3. Select the `National_Flags.apkg` file
4. Start learning!

## Testing

Run the test suite to verify functionality:

```bash
python test_download.py    # Test flag download functionality
python test_anki_deck.py   # Test Anki deck creation functionality
```

## Notes

- The scripts include delays between requests to be respectful to Wikipedia's servers
- Already downloaded images will be skipped on subsequent runs
- The `flags/` directory is excluded from version control (see `.gitignore`)
- Flag descriptions and details are automatically scraped from Wikipedia flag pages
- Some countries may not have detailed information available on Wikipedia