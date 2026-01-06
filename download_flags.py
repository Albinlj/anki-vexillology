#!/usr/bin/env python3
"""
Download national flags from Wikipedia.
Source: https://en.wikipedia.org/wiki/List_of_national_flags_of_sovereign_states
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Configuration
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_national_flags_of_sovereign_states"
OUTPUT_DIR = "flags"
REQUEST_DELAY = 0.5  # Delay between requests to be respectful to Wikipedia's servers


def create_output_directory():
    """Create the output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")


def get_wikipedia_page():
    """Fetch the Wikipedia page content."""
    print(f"Fetching page: {WIKIPEDIA_URL}")
    headers = {
        'User-Agent': 'AnkiVexillologyBot/1.0 (Educational purposes; downloading flag images)'
    }
    response = requests.get(WIKIPEDIA_URL, headers=headers)
    response.raise_for_status()
    return response.text


def extract_flag_images(html_content):
    """Extract flag image URLs from the Wikipedia page."""
    soup = BeautifulSoup(html_content, 'html.parser')
    flag_images = []
    
    # Find all tables with class 'wikitable'
    tables = soup.find_all('table', class_='wikitable')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            # Find images in the row
            images = row.find_all('img')
            for img in images:
                if img.get('src'):
                    # Convert relative URLs to absolute URLs
                    img_url = urljoin('https:', img['src'])
                    # Get the alt text for the filename
                    alt_text = img.get('alt', '')
                    
                    # Only include images that look like flags (larger than icons)
                    width = img.get('width', '0')
                    try:
                        if int(width) >= 100:  # Filter out small icons
                            flag_images.append({
                                'url': img_url,
                                'alt': alt_text,
                                'width': width
                            })
                    except (ValueError, TypeError):
                        # If width is not a number, check if it's a flag image
                        # Be more restrictive: require 'Flag_of_' in URL or 'flag of' in alt text
                        if 'Flag_of_' in img_url or 'flag of' in alt_text.lower():
                            flag_images.append({
                                'url': img_url,
                                'alt': alt_text,
                                'width': width
                            })
    
    return flag_images


def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def download_image(img_data, index):
    """Download a single flag image."""
    url = img_data['url']
    alt_text = img_data['alt']
    
    # Create filename from alt text or URL
    if alt_text and alt_text.strip():
        base_name = sanitize_filename(alt_text)
    else:
        # Extract filename from URL
        parsed_url = urlparse(url)
        base_name = os.path.basename(parsed_url.path)
    
    # Get file extension from URL
    ext = os.path.splitext(urlparse(url).path)[1]
    if not ext:
        ext = '.png'  # Default extension
    
    # Ensure the filename has an extension
    if not base_name.endswith(ext):
        filename = f"{base_name}{ext}"
    else:
        filename = base_name
    
    # Add index prefix to avoid duplicates
    filename = f"{index:03d}_{filename}"
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"  Skipping (already exists): {filename}")
        return True
    
    try:
        print(f"  Downloading: {filename}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"  Error downloading {filename}: {e}")
        return False


def main():
    """Main function to orchestrate the download process."""
    print("Starting flag download process...")
    
    # Create output directory
    create_output_directory()
    
    # Fetch Wikipedia page
    try:
        html_content = get_wikipedia_page()
    except Exception as e:
        print(f"Error fetching Wikipedia page: {e}")
        sys.exit(1)
    
    # Extract flag images
    print("Extracting flag image URLs...")
    flag_images = extract_flag_images(html_content)
    print(f"Found {len(flag_images)} flag images")
    
    if not flag_images:
        print("No flag images found. Exiting.")
        sys.exit(1)
    
    # Download images
    print(f"\nDownloading {len(flag_images)} flag images...")
    success_count = 0
    fail_count = 0
    
    for index, img_data in enumerate(flag_images, start=1):
        if download_image(img_data, index):
            success_count += 1
        else:
            fail_count += 1
        
        # Be respectful to Wikipedia's servers
        time.sleep(REQUEST_DELAY)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Download complete!")
    print(f"Successfully downloaded: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {len(flag_images)}")
    print(f"Images saved to: {OUTPUT_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
