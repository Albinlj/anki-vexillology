# anki-vexillology

An Anki flashcard deck for learning national flags (vexillology).

## Download Pre-built Deck

The easiest way to get started is to download a pre-built deck from the [Releases page](../../releases). The deck is automatically generated monthly with the latest flag information from Wikipedia.

1. Go to the [Releases page](../../releases)
2. Download the latest `National_Flags.apkg` file
3. Import it into Anki (File > Import)
4. Start learning!

## Building the Deck Yourself

If you want to build the deck yourself or customize it, follow the instructions below.

### Prerequisites

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
- Flag descriptions and details are automatically scraped from Wikipedia flag pages
- Some countries may not have detailed information available on Wikipedia

## Automated Workflows

This repository includes two GitHub Actions that work together:

### 1. Download Flag Images (runs on the 1st of each month)
- Downloads all flag images from Wikipedia
- Resizes images to optimize storage
- Commits updated flags to the repository

### 2. Create Anki Deck Release (runs on the 2nd of each month)
- Uses the committed flag images from the repository
- Creates the Anki deck with the latest Wikipedia information
- Publishes a new release with the `National_Flags.apkg` file

The workflows run:
- **Download Flags**: Monthly on the 1st at 00:00 UTC
- **Create Release**: Monthly on the 2nd at 00:00 UTC (uses flags from 1st)
- **Manual Triggers**: Both can be triggered manually via the "Actions" tab
- **Version Tags**: Create Release also triggers on version tag pushes (e.g., `v1.0.0`)

To trigger a manual release, you can also push a tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```