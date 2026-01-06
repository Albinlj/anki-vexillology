# anki-vexillology

An Anki flashcard deck for learning national flags (vexillology).

## Downloading Flags

This repository includes a script to download all national flags from Wikipedia.

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Usage

Run the download script:

```bash
python download_flags.py
```

The script will:
1. Fetch the list of national flags from Wikipedia
2. Extract flag image URLs
3. Download all flag images to the `flags/` directory
4. Display a summary of successful and failed downloads

### Output

All downloaded flag images will be saved in the `flags/` directory. Each image is prefixed with a number to maintain order and avoid filename conflicts.

### Notes

- The script includes a delay between requests to be respectful to Wikipedia's servers
- Already downloaded images will be skipped on subsequent runs
- The `flags/` directory is excluded from version control (see `.gitignore`)