"""
Sound Browser - Handles downloading alarm sounds from the internet.
Provides access to free sound libraries and manages downloads.
"""

import os
import requests
import json
from typing import List, Dict, Optional
from kivy.clock import Clock
from kivy.utils import platform
from threading import Thread

class SoundBrowser:
    """
    Browser for finding and downloading alarm sounds from the internet.
    Uses free sound APIs to provide a variety of alarm sounds.
    """
    
    def __init__(self, download_dir: str = "assets/sounds"):
        """
        Initialize the sound browser.
        
        Args:
            download_dir: Directory to save downloaded sounds
        """
        self.download_dir = download_dir
        self.api_base_url = "https://freesound.org/apiv2"
        self.api_key = None  # Freesound API key (optional)
        
        # Ensure download directory exists
        os.makedirs(download_dir, exist_ok=True)
        
        # Fallback sounds if API is not available
        self.fallback_sounds = [
            {
                "name": "Classic Alarm",
                "url": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
                "description": "Traditional alarm bell sound"
            },
            {
                "name": "Digital Beep",
                "url": "https://www.soundjay.com/misc/sounds/digital-beep-1.wav", 
                "description": "Modern digital alarm tone"
            },
            {
                "name": "Gentle Wake",
                "url": "https://www.soundjay.com/misc/sounds/chime-1.wav",
                "description": "Soft chime for gentle waking"
            },
            {
                "name": "Temple Bell",
                "url": "https://cdn.pixabay.com/audio/2022/07/26/audio_124bfae3e2.mp3",
                "description": "Temple bell sound for spiritual wake-up"
            },
            {
                "name": "Rain Ambience",
                "url": "https://cdn.pixabay.com/audio/2022/08/14/audio_9039abf978.mp3",
                "description": "Relaxing rain ambience for gentle waking"
            },
            {
                "name": "Nature Wake",
                "url": "https://www.zapsplat.com/wp-content/uploads/2015/sound-effects-84570/zapsplat_nature_birds_singing_morning_84570.mp3",
                "description": "Peaceful birds singing"
            },
            {
                "name": "Ocean Waves",
                "url": "https://www.zapsplat.com/wp-content/uploads/2015/sound-effects-84571/zapsplat_nature_ocean_waves_gentle_84571.mp3",
                "description": "Calming ocean waves"
            }
        ]
        
        # Create local fallback sounds if they don't exist
        self._create_local_fallback_sounds()
    
    def _create_local_fallback_sounds(self):
        """Create simple local fallback sounds if network is unavailable."""
        try:
            import wave
            import struct
            import math
            
            # Create a simple beep sound
            def create_beep_sound(filename, frequency=800, duration=2.0, sample_rate=44100):
                """Create a simple beep sound file."""
                filepath = os.path.join(self.download_dir, filename)
                if os.path.exists(filepath):
                    return filepath
                
                # Generate audio data
                num_samples = int(sample_rate * duration)
                audio_data = []
                
                for i in range(num_samples):
                    # Simple sine wave
                    value = math.sin(2 * math.pi * frequency * i / sample_rate)
                    # Convert to 16-bit integer
                    audio_data.append(int(value * 32767))
                
                # Write WAV file
                with wave.open(filepath, 'w') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    
                    # Pack audio data
                    packed_data = struct.pack('<%dh' % len(audio_data), *audio_data)
                    wav_file.writeframes(packed_data)
                
                return filepath
            
            # Create different types of alarm sounds
            create_beep_sound("local_classic_alarm.wav", frequency=600, duration=2.0)
            create_beep_sound("local_digital_beep.wav", frequency=1000, duration=1.5)
            create_beep_sound("local_gentle_wake.wav", frequency=400, duration=3.0)
            
        except Exception as e:
            print(f"Error creating local fallback sounds: {e}")
    
    def _get_local_fallback_sounds(self) -> List[Dict]:
        """Get local fallback sounds when network is unavailable."""
        sounds = []
        
        local_sounds = [
            {
                "name": "Local Classic Alarm",
                "path": os.path.join(self.download_dir, "local_classic_alarm.wav"),
                "description": "Local classic alarm sound"
            },
            {
                "name": "Local Digital Beep", 
                "path": os.path.join(self.download_dir, "local_digital_beep.wav"),
                "description": "Local digital beep sound"
            },
            {
                "name": "Local Gentle Wake",
                "path": os.path.join(self.download_dir, "local_gentle_wake.wav"),
                "description": "Local gentle wake sound"
            }
        ]
        
        for sound in local_sounds:
            if os.path.exists(sound["path"]):
                sounds.append({
                    'id': f"local_{len(sounds)}",
                    'name': sound['name'],
                    'url': sound['path'],  # Use local path as URL
                    'description': sound['description'],
                    'source': 'local'
                })
        
        return sounds
    
    def search_sounds(self, query: str = "alarm", limit: int = 10) -> List[Dict]:
        """
        Search for sounds using the Freesound API.
        
        Args:
            query: Search term
            limit: Maximum number of results
            
        Returns:
            List of sound dictionaries
        """
        try:
            # Try Freesound API first
            if self.api_key:
                results = self._search_freesound(query, limit)
                if results:
                    return results
            
            # Try fallback sounds from internet
            results = self._get_fallback_sounds(query)
            if results:
                return results
            
            # If no internet sounds available, return local sounds
            return self._get_local_fallback_sounds()
            
        except Exception as e:
            print(f"Error searching sounds: {e}")
            # Return local sounds as final fallback
            return self._get_local_fallback_sounds()
    
    def _search_freesound(self, query: str, limit: int) -> List[Dict]:
        """Search Freesound API for alarm sounds."""
        try:
            url = f"{self.api_base_url}/search/text/"
            params = {
                'query': f"{query} alarm wake",
                'filter': 'duration:[1 TO 30]',  # 1-30 second sounds
                'fields': 'id,name,url,preview,description',
                'page_size': limit
            }
            
            if self.api_key:
                params['token'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            sounds = []
            
            for result in data.get('results', []):
                sound = {
                    'id': result.get('id'),
                    'name': result.get('name', 'Unknown'),
                    'url': result.get('preview', ''),
                    'description': result.get('description', ''),
                    'source': 'freesound'
                }
                sounds.append(sound)
            
            return sounds
            
        except Exception as e:
            print(f"Freesound API error: {e}")
            return []
    
    def _get_fallback_sounds(self, query: str) -> List[Dict]:
        """Get fallback sounds when API is not available."""
        # Filter fallback sounds based on query
        filtered_sounds = []
        query_lower = query.lower()
        
        # Try internet fallback sounds first
        for sound in self.fallback_sounds:
            if (query_lower in sound['name'].lower() or 
                query_lower in sound['description'].lower()):
                filtered_sounds.append({
                    'id': f"fallback_{len(filtered_sounds)}",
                    'name': sound['name'],
                    'url': sound['url'],
                    'description': sound['description'],
                    'source': 'fallback'
                })
        
        # If no internet sounds found or available, add local sounds
        if not filtered_sounds:
            local_sounds = self._get_local_fallback_sounds()
            filtered_sounds.extend(local_sounds)
        
        return filtered_sounds if filtered_sounds else self._get_local_fallback_sounds()
    
    def download_sound(self, sound_info: Dict, callback: Optional[callable] = None) -> Optional[str]:
        """
        Download a sound file from the internet.
        
        Args:
            sound_info: Dictionary containing sound information
            callback: Optional callback function for progress updates
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            url = sound_info.get('url')
            if not url:
                return None
            
            # Use the file extension from the URL
            ext = os.path.splitext(url)[1]
            if not ext:
                ext = '.mp3' # Default to mp3 as it's common
            filename = f"{sound_info['name'].replace(' ', '_')}_{sound_info['id']}{ext}"
            filepath = os.path.join(self.download_dir, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                if callback:
                    callback(100, "File already exists")
                return filepath
            
            # Download file
            if callback:
                callback(0, "Starting download...")
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, stream=True, timeout=30, headers=headers)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if callback and total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            callback(progress, f"Downloading... {progress}%")
            
            if callback:
                callback(100, f"Downloaded: {os.path.basename(filepath)}")
            
            return filepath
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {e}"
            print(f"Error downloading sound: {error_msg}")
            if callback:
                callback(0, error_msg)
            return None
        except Exception as e:
            error_msg = f"Download failed: {e}"
            print(f"Error downloading sound: {error_msg}")
            if callback:
                callback(0, error_msg)
            return None
    
    def download_sound_async(self, sound_info: Dict, callback: Optional[callable] = None):
        """
        Download a sound file asynchronously.
        
        Args:
            sound_info: Dictionary containing sound information
            callback: Optional callback function for progress updates
        """
        def download_thread():
            self.download_sound(sound_info, callback)
        
        thread = Thread(target=download_thread)
        thread.daemon = True
        thread.start()
    
    def get_downloaded_sounds(self) -> List[Dict]:
        """
        Get list of downloaded sounds.
        
        Returns:
            List of downloaded sound information
        """
        sounds = []
        
        if not os.path.exists(self.download_dir):
            return sounds
        
        for filename in os.listdir(self.download_dir):
            if filename.lower().endswith(('.wav', '.mp3', '.ogg')):
                filepath = os.path.join(self.download_dir, filename)
                name = os.path.splitext(filename)[0].replace('_', ' ')
                
                sounds.append({
                    'name': name,
                    'path': filepath,
                    'source': 'downloaded'
                })
        
        return sounds
    
    def delete_downloaded_sound(self, filepath: str) -> bool:
        """
        Delete a downloaded sound file.
        
        Args:
            filepath: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(filepath) and filepath.startswith(self.download_dir):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting sound file: {e}")
        
        return False
    
    def set_api_key(self, api_key: str):
        """
        Set Freesound API key for better search results.
        
        Args:
            api_key: Freesound API key
        """
        self.api_key = api_key 