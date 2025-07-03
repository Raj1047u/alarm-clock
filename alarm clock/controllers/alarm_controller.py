"""
Alarm Controller - Simplified alarm management without AI features.
Handles alarm creation, deletion, updating, and triggering.
"""

import json
import os
import threading
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Dict, Any

from models.alarm_model import Alarm
from utils.audio_manager import AudioManager
from utils.notification_manager import NotificationManager

class AlarmController:
    """
    Simple alarm controller without AI features.
    Manages alarm lifecycle and persistence.
    """
    
    def __init__(self):
        """Initialize the alarm controller."""
        self.alarms: Dict[str, Alarm] = {}
        self.audio_manager = AudioManager()
        self.notification_manager = NotificationManager()
        
        # Threading
        self.alarm_check_thread = None
        self.stop_checking = False
        
        # UI Callbacks
        self.on_alarm_triggered: Optional[Callable] = None
        self.on_alarm_stopped: Optional[Callable] = None
        
        # Data persistence
        self.data_file = "alarms.json"
        self.backup_file = "alarms.json.bak"
        
        # Load existing alarms
        self._load_alarms()
        
        # Start alarm monitoring
        self._start_alarm_monitor()
    
    def set_ui_callbacks(self, on_alarm_triggered: Callable = None, on_alarm_stopped: Callable = None):
        """Set UI callbacks for alarm events."""
        self.on_alarm_triggered = on_alarm_triggered
        self.on_alarm_stopped = on_alarm_stopped
    
    def add_alarm(self, time_str: str, label: str = "", repeat_days: List[int] = None,
                  vibrate: bool = True, snooze_duration: int = 5,
                  sound_file: str = None, creation_method: str = "manual") -> Optional[str]:
        """
        Add a new alarm.
        
        Args:
            time_str: Time in HH:MM format
            label: Optional alarm label
            repeat_days: List of weekday indices (0=Monday, 6=Sunday)
            vibrate: Whether to vibrate
            snooze_duration: Snooze duration in minutes
            sound_file: Path to sound file
            creation_method: How the alarm was created
            
        Returns:
            Alarm ID if successful, None otherwise
        """
        try:
            # Validate time format
            datetime.strptime(time_str, "%H:%M")
            
            # Create alarm
            alarm = Alarm(
                time=time_str,
                label=label,
                repeat_days=repeat_days or [],
                vibrate=vibrate,
                snooze_duration=snooze_duration,
                sound_file=sound_file or self.audio_manager.default_sound_file
            )
            
            # Store alarm
            self.alarms[alarm.id] = alarm
            
            # Save to file
            self._save_alarms()
            
            print(f"Added alarm: {time_str} - {label}")
            return alarm.id
            
        except Exception as e:
            print(f"Error adding alarm: {e}")
            return None
    
    def add_alarm_object(self, alarm: Alarm) -> Optional[str]:
        """
        Add an alarm object directly.
        
        Args:
            alarm: Alarm object to add
            
        Returns:
            Alarm ID if successful, None otherwise
        """
        try:
            # Store alarm
            self.alarms[alarm.id] = alarm
            
            # Save to file
            self._save_alarms()
            
            print(f"Added alarm: {alarm.time} - {alarm.get_display_label()}")
            return alarm.id
            
        except Exception as e:
            print(f"Error adding alarm object: {e}")
            return None
    
    def update_alarm(self, alarm_id: str, time: str = None, label: str = None,
                     repeat_days: List[int] = None, vibrate: bool = None,
                     snooze_duration: int = None, sound_file: str = None) -> bool:
        """Update an existing alarm."""
        try:
            if alarm_id not in self.alarms:
                return False
            
            alarm = self.alarms[alarm_id]
            
            # Update fields if provided
            if time is not None:
                datetime.strptime(time, "%H:%M")  # Validate format
                alarm.time = time
            
            if label is not None:
                alarm.label = label
            
            if repeat_days is not None:
                alarm.repeat_days = repeat_days
            
            if vibrate is not None:
                alarm.vibrate = vibrate
            
            if snooze_duration is not None:
                alarm.snooze_duration = snooze_duration
            
            if sound_file is not None:
                alarm.sound_file = sound_file
            
            # Reset snooze if time changed
            if time is not None:
                alarm.snooze_count = 0
                alarm.next_trigger = None
            
            # Save changes
            self._save_alarms()
            
            print(f"Updated alarm: {alarm_id}")
            return True
            
        except Exception as e:
            print(f"Error updating alarm: {e}")
            return False
    
    def delete_alarm(self, alarm_id: str) -> bool:
        """Delete an alarm."""
        try:
            if alarm_id in self.alarms:
                del self.alarms[alarm_id]
                self._save_alarms()
                print(f"Deleted alarm: {alarm_id}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting alarm: {e}")
            return False
    
    def toggle_alarm(self, alarm_id: str) -> bool:
        """Toggle alarm enabled/disabled state."""
        try:
            if alarm_id in self.alarms:
                alarm = self.alarms[alarm_id]
                alarm.enabled = not alarm.enabled
                
                # Reset snooze when disabling
                if not alarm.enabled:
                    alarm.snooze_count = 0
                    alarm.next_trigger = None
                
                self._save_alarms()
                print(f"Toggled alarm {alarm_id}: {'enabled' if alarm.enabled else 'disabled'}")
                return True
            return False
        except Exception as e:
            print(f"Error toggling alarm: {e}")
            return False
    
    def get_all_alarms(self) -> List[Alarm]:
        """Get all alarms."""
        return list(self.alarms.values())
    
    def get_alarm(self, alarm_id: str) -> Optional[Alarm]:
        """Get a specific alarm."""
        return self.alarms.get(alarm_id)
    
    def stop_alarm(self, alarm_id: str):
        """Stop an alarm."""
        try:
            # Stop audio and vibration
            self.audio_manager.stop_alarm_sound()
            self.audio_manager.stop_vibration()
            
            # Clear notification
            self.notification_manager.clear_alarm_notification()
            
            # Reset alarm state
            if alarm_id in self.alarms:
                alarm = self.alarms[alarm_id]
                alarm.snooze_count = 0
                alarm.next_trigger = None
                self._save_alarms()
            
            # Notify UI
            if self.on_alarm_stopped:
                self.on_alarm_stopped(self.alarms.get(alarm_id))
            
            print(f"Stopped alarm: {alarm_id}")
            
        except Exception as e:
            print(f"Error stopping alarm: {e}")
    
    def snooze_alarm(self, alarm_id: str):
        """Snooze an alarm."""
        try:
            if alarm_id not in self.alarms:
                return
            
            alarm = self.alarms[alarm_id]
            
            # Stop current audio/vibration
            self.audio_manager.stop_alarm_sound()
            self.audio_manager.stop_vibration()
            
            # Clear notification
            self.notification_manager.clear_alarm_notification()
            
            # Calculate snooze time
            snooze_minutes = alarm.snooze_duration
            alarm.next_trigger = datetime.now() + timedelta(minutes=snooze_minutes)
            alarm.snooze_count += 1
            
            # Save state
            self._save_alarms()
            
            print(f"Snoozed alarm {alarm_id} for {snooze_minutes} minutes")
            
        except Exception as e:
            print(f"Error snoozing alarm: {e}")
    
    def _load_alarms(self):
        """Load alarms from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                for alarm_data in data.get('alarms', []):
                    alarm = Alarm.from_dict(alarm_data)
                    self.alarms[alarm.id] = alarm
                
                print(f"Loaded {len(self.alarms)} alarms")
            
        except Exception as e:
            print(f"Error loading alarms: {e}")
            # Try backup file
            self._load_backup()
    
    def _load_backup(self):
        """Load from backup file."""
        try:
            if os.path.exists(self.backup_file):
                with open(self.backup_file, 'r') as f:
                    data = json.load(f)
                
                for alarm_data in data.get('alarms', []):
                    alarm = Alarm.from_dict(alarm_data)
                    self.alarms[alarm.id] = alarm
                
                print(f"Loaded {len(self.alarms)} alarms from backup")
            
        except Exception as e:
            print(f"Error loading backup: {e}")
    
    def _save_alarms(self):
        """Save alarms to file."""
        try:
            # Create backup
            if os.path.exists(self.data_file):
                import shutil
                shutil.copy2(self.data_file, self.backup_file)
            
            # Save current data
            data = {
                'alarms': [alarm.to_dict() for alarm in self.alarms.values()],
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print(f"Error saving alarms: {e}")
    
    def _start_alarm_monitor(self):
        """Start the alarm monitoring thread."""
        if self.alarm_check_thread is None or not self.alarm_check_thread.is_alive():
            self.stop_checking = False
            self.alarm_check_thread = threading.Thread(target=self._check_alarms_loop, daemon=True)
            self.alarm_check_thread.start()
            print("Started alarm monitor")
    
    def _check_alarms_loop(self):
        """Main alarm checking loop."""
        while not self.stop_checking:
            try:
                current_time = datetime.now()
                current_weekday = current_time.weekday()
                current_time_str = current_time.strftime("%H:%M")
                
                for alarm in self.alarms.values():
                    if not alarm.enabled:
                        continue
                    
                    should_trigger = False
                    
                    # Check if it's a snoozed alarm
                    if alarm.next_trigger:
                        if current_time >= alarm.next_trigger:
                            should_trigger = True
                            alarm.next_trigger = None  # Clear snooze
                    
                    # Check regular alarm time
                    elif alarm.time == current_time_str:
                        if alarm.repeat_days:
                            # Repeating alarm - check if today is a repeat day
                            if current_weekday in alarm.repeat_days:
                                should_trigger = True
                        else:
                            # One-time alarm - trigger and disable
                            should_trigger = True
                            alarm.enabled = False
                    
                    if should_trigger:
                        self._trigger_alarm(alarm)
                
                # Save any changes (like disabled one-time alarms)
                self._save_alarms()
                
            except Exception as e:
                print(f"Error in alarm check loop: {e}")
            
            # Check every 30 seconds
            threading.Event().wait(30)
    
    def _trigger_alarm(self, alarm: Alarm):
        """Trigger an alarm."""
        try:
            print(f"Triggering alarm: {alarm.time} - {alarm.label}")
            
            # Play alarm sound
            self.audio_manager.play_alarm_sound(alarm.sound_file)
            
            # Start vibration if enabled
            if alarm.vibrate:
                self.audio_manager.start_vibration()
            
            # Show notification
            self.notification_manager.show_alarm_notification(alarm)
            
            # Notify UI
            if self.on_alarm_triggered:
                self.on_alarm_triggered(alarm)
            
        except Exception as e:
            print(f"Error triggering alarm: {e}")
    
    def stop(self):
        """Stop the alarm controller."""
        self.stop_checking = True
        
        # Stop any playing alarms
        self.audio_manager.stop_alarm_sound()
        self.audio_manager.stop_vibration()
        
        # Clear notifications
        self.notification_manager.clear_alarm_notification()
        
        print("Alarm controller stopped") 