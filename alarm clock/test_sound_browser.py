#!/usr/bin/env python3
"""
Test script for the Sound Browser functionality.
"""

import os
import sys
from utils.sound_browser import SoundBrowser

def test_sound_browser():
    """Test the sound browser functionality."""
    print("Testing Sound Browser...")
    
    # Initialize sound browser
    browser = SoundBrowser()
    
    # Test search functionality
    print("\n1. Testing sound search...")
    results = browser.search_sounds("alarm", limit=5)
    print(f"Found {len(results)} sounds:")
    for i, sound in enumerate(results, 1):
        print(f"  {i}. {sound['name']} - {sound['description']}")
    
    # Test getting downloaded sounds
    print("\n2. Testing downloaded sounds list...")
    downloaded = browser.get_downloaded_sounds()
    print(f"Found {len(downloaded)} downloaded sounds:")
    for sound in downloaded:
        print(f"  - {sound['name']} ({sound['path']})")
    
    # Test download functionality (first result if available)
    if results:
        print(f"\n3. Testing download of '{results[0]['name']}'...")
        
        def progress_callback(progress, message):
            print(f"  Progress: {progress}% - {message}")
        
        result = browser.download_sound(results[0], progress_callback)
        if result:
            print(f"  Download successful: {result}")
        else:
            print("  Download failed")
    
    print("\nSound Browser test completed!")

if __name__ == "__main__":
    test_sound_browser() 