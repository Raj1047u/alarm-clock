"""
Audio Manager - Handles sound playback and vibration functionality.
Provides cross-platform audio capabilities for the alarm clock app.
"""

import os
import shutil
from typing import Optional, List
from kivy.core.audio import SoundLoader
from kivy.utils import platform
from kivy.clock import Clock

class AudioManager:
    """
    Manages audio playback and vibration for alarm sounds.
    Handles cross-platform audio capabilities.
    """
    
    def __init__(self):
        """Initialize the audio manager."""
        self.current_sound: Optional[SoundLoader] = None
        self.vibration_active = False
        
        # Default sound file paths
        self.app_sounds_dir = "assets/sounds"
        self.default_sound_file = f"{self.app_sounds_dir}/default_alarm.wav"
        
        self._ensure_directories()
        self._ensure_default_sound()
    
    def play_alarm_sound(self, sound_file: str = None):
        """
        Play alarm sound.
        
        Args:
            sound_file: Path to sound file (uses default if None)
        """
        if sound_file is None:
            sound_file = self.default_sound_file
        
        # Stop any currently playing sound
        self.stop_alarm_sound()
        
        # Check if file exists
        if not os.path.exists(sound_file):
            print(f"Sound file not found: {sound_file}")
            sound_file = self.default_sound_file
        
        try:
            # Load and play sound
            self.current_sound = SoundLoader.load(sound_file)
            if self.current_sound:
                self.current_sound.loop = True  # Loop until stopped
                self.current_sound.play()
            else:
                print(f"Failed to load sound file: {sound_file}")
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def stop_alarm_sound(self):
        """Stop currently playing alarm sound."""
        if self.current_sound:
            try:
                self.current_sound.stop()
                self.current_sound.unload()
            except Exception as e:
                print(f"Error stopping sound: {e}")
            finally:
                self.current_sound = None
    
    def start_vibration(self):
        """Start vibration (Android only)."""
        if platform != 'android':
            return
        
        try:
            # Import Android-specific modules
            from jnius import autoclass
            
            # Get Android vibration service
            Context = autoclass('android.content.Context')
            Vibrator = autoclass('android.os.Vibrator')
            
            # Get current activity
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            # Start vibration
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            if vibrator and vibrator.hasVibrator():
                # Vibrate pattern: wait 0ms, vibrate 1000ms, wait 500ms, vibrate 1000ms
                pattern = [0, 1000, 500, 1000]
                vibrator.vibrate(pattern, 0)  # 0 = repeat indefinitely
                self.vibration_active = True
        except Exception as e:
            print(f"Error starting vibration: {e}")
    
    def stop_vibration(self):
        """Stop vibration (Android only)."""
        if platform != 'android' or not self.vibration_active:
            return
        
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            Vibrator = autoclass('android.os.Vibrator')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            if vibrator:
                vibrator.cancel()
                self.vibration_active = False
        except Exception as e:
            print(f"Error stopping vibration: {e}")
    
    def set_volume(self, volume: float):
        """
        Set volume for alarm sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.current_sound:
            self.current_sound.volume = max(0.0, min(1.0, volume))
    
    def get_volume(self) -> float:
        """
        Get current volume level.
        
        Returns:
            Current volume (0.0 to 1.0)
        """
        if self.current_sound:
            return self.current_sound.volume
        return 1.0
    
    def is_playing(self) -> bool:
        """
        Check if sound is currently playing.
        
        Returns:
            True if sound is playing, False otherwise
        """
        return self.current_sound is not None and self.current_sound.state == 'play'
    
    def _ensure_default_sound(self):
        """Ensure default sound file exists."""
        if not os.path.exists(self.default_sound_file):
            # Create assets directory if it doesn't exist
            os.makedirs(os.path.dirname(self.default_sound_file), exist_ok=True)
            
            # Create a simple beep sound (this is a placeholder)
            # In a real app, you'd include an actual sound file
            try:
                self._create_default_sound()
            except Exception as e:
                print(f"Could not create default sound: {e}")
    
    def _create_default_sound(self):
        """
        Create a simple default alarm sound.
        This is a basic implementation - in production, use a proper sound file.
        """
        # This is a placeholder - in a real app, you'd include an actual .wav file
        # For now, we'll just create an empty file to prevent errors
        with open(self.default_sound_file, 'w') as f:
            f.write("# Placeholder for default alarm sound")
        
        print(f"Created placeholder sound file: {self.default_sound_file}")
        print("Please replace with an actual .wav file for proper alarm sounds.")
    
    def get_available_sounds(self) -> List[dict]:
        """
        Get list of available alarm sounds.
        
        Returns:
            List of dicts with 'path' and 'name' keys
        """
        sounds = []
        
        # Add built-in sounds (these would be actual audio files in production)
        built_in_sounds = [
            {'path': 'assets/sounds/default_alarm.wav', 'name': 'Classic Alarm'},
            {'path': 'assets/sounds/beep_alarm.wav', 'name': 'Digital Beep'},
            {'path': 'assets/sounds/bell_alarm.wav', 'name': 'Church Bell'},
            {'path': 'assets/sounds/rooster_alarm.wav', 'name': 'Rooster Call'},
            {'path': 'assets/sounds/local_classic_alarm.wav', 'name': 'Vintage Bell'},
            {'path': 'assets/sounds/local_digital_beep.wav', 'name': 'Electronic Beep'},
            {'path': 'assets/sounds/local_gentle_wake.wav', 'name': 'Gentle Wake'},
            {'path': 'assets/sounds/Classic_Alarm_fallback_0.wav', 'name': 'Traditional Alarm'},
        ]
        
        # Add built-in sounds that exist
        for sound in built_in_sounds:
            if os.path.exists(sound['path']) or sound['path'] in ['assets/sounds/default_alarm.wav']:
                sounds.append(sound)
        
        # Add any additional custom sounds from app directory
        if os.path.exists(self.app_sounds_dir):
            for filename in os.listdir(self.app_sounds_dir):
                if filename.lower().endswith(('.wav', '.mp3', '.ogg')):
                    filepath = os.path.join(self.app_sounds_dir, filename)
                    # Check if not already in built-in sounds
                    if not any(s['path'] == filepath for s in sounds):
                        name = os.path.splitext(filename)[0].replace('_', ' ').title()
                        sounds.append({
                            'path': filepath,
                            'name': name
                        })
        
        return sounds
    
    def add_custom_sound(self, source_path: str, new_name: str = None) -> str:
        """
        Add a custom sound file to the app's sounds directory.
        
        Args:
            source_path: Path to the source sound file
            new_name: Optional new name for the file (without extension)
            
        Returns:
            Path to the copied sound file or None on failure
        """
        try:
            # Get file extension and create destination path
            _, ext = os.path.splitext(source_path)
            if not new_name:
                new_name = os.path.basename(source_path)
            else:
                new_name = f"{new_name}{ext}"
                
            # Make sure directory exists
            os.makedirs(self.app_sounds_dir, exist_ok=True)
            
            # Copy file to app's sounds directory
            dest_path = os.path.join(self.app_sounds_dir, new_name)
            shutil.copy2(source_path, dest_path)
            
            return dest_path
        except Exception as e:
            print(f"Error adding custom sound: {e}")
            return None
    
    def delete_custom_sound(self, sound_path: str) -> bool:
        """
        Delete a custom sound file.
        
        Args:
            sound_path: Path to the sound file to delete
            
        Returns:
            True if successfully deleted, False otherwise
        """
        # Don't allow deleting default sound
        if sound_path == self.default_sound_file:
            return False
            
        try:
            if os.path.exists(sound_path):
                os.remove(sound_path)
                return True
        except Exception as e:
            print(f"Error deleting sound file: {e}")
        
        return False
    
    def preview_sound(self, sound_path: str, duration: float = 3.0):
        """
        Preview a sound file for a short duration.
        
        Args:
            sound_path: Path to the sound file
            duration: Duration in seconds to play the preview
        """
        # Stop any currently playing sound
        self.stop_alarm_sound()
        
        # Check if file exists
        if not os.path.exists(sound_path):
            print(f"Sound file not found: {sound_path}")
            return
            
        try:
            # Load and play sound
            sound = SoundLoader.load(sound_path)
            if sound:
                sound.play()
                
                # Schedule stop after duration
                Clock.schedule_once(lambda dt: self._stop_preview(sound), duration)
            else:
                print(f"Failed to load sound file: {sound_path}")
        except Exception as e:
            print(f"Error previewing sound: {e}")
    
    def _stop_preview(self, sound):
        """Stop a preview sound."""
        if sound:
            try:
                sound.stop()
                sound.unload()
            except Exception as e:
                print(f"Error stopping preview: {e}")
    
    def _ensure_directories(self):
        """Ensure necessary directories exist."""
        os.makedirs(self.app_sounds_dir, exist_ok=True) 