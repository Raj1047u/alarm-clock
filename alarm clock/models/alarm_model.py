"""
Alarm Model - Simplified data layer for alarm management.
Clean data structures without unnecessary complexity.
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class Alarm:
    """
    Simple alarm data class.
    
    Attributes:
        id: Unique identifier for the alarm
        time: Time when alarm should trigger (HH:MM)
        label: User-defined label for the alarm
        enabled: Whether the alarm is active
        repeat_days: List of days to repeat (0=Monday, 6=Sunday)
        sound_file: Path to the sound file to play
        snooze_duration: Snooze duration in minutes
        vibrate: Whether to vibrate when alarm triggers
        snooze_count: Number of times snoozed
        next_trigger: Next trigger time for snoozed alarms
    """
    time: str  # Format: "HH:MM"
    label: str = ""
    enabled: bool = True
    repeat_days: List[int] = None
    sound_file: str = "assets/sounds/default_alarm.wav"
    snooze_duration: int = 5
    vibrate: bool = True
    snooze_count: int = 0
    next_trigger: Optional[datetime] = None
    id: str = ""
    
    def __post_init__(self):
        if self.repeat_days is None:
            self.repeat_days = []
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def get_display_label(self) -> str:
        """Get the display label with auto-generated label if empty."""
        # Generate default label if empty
        if not self.label.strip():
            return self._generate_default_label()
        else:
            return self.label
    
    def _generate_default_label(self) -> str:
        """Generate a default label based on alarm time."""
        try:
            hour = int(self.time.split(':')[0])
            
            # Generate label based on time of day
            if 5 <= hour < 9:
                return "Morning Alarm"
            elif 9 <= hour < 12:
                return "Late Morning"
            elif 12 <= hour < 14:
                return "Lunch Time"
            elif 14 <= hour < 17:
                return "Afternoon"
            elif 17 <= hour < 20:
                return "Evening"
            elif 20 <= hour < 23:
                return "Night"
            else:  # 23-4 (late night/early morning)
                return "Late Night"
        except (ValueError, IndexError):
            return "Alarm"
    
    def to_dict(self) -> Dict:
        """Convert alarm to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime to string for JSON serialization
        if self.next_trigger:
            data['next_trigger'] = self.next_trigger.isoformat()
        else:
            data['next_trigger'] = None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alarm':
        """Create alarm from dictionary."""
        # Convert datetime string back to datetime object
        if data.get('next_trigger'):
            try:
                data['next_trigger'] = datetime.fromisoformat(data['next_trigger'])
            except (ValueError, TypeError):
                data['next_trigger'] = None
        
        # Remove emoji field for backward compatibility
        if 'emoji' in data:
            del data['emoji']
        
        return cls(**data)

# Common text presets for different alarm types
ALARM_TEXT_PRESETS = {
    "Morning": "Morning",
    "Work": "Work", 
    "Gym": "Gym",
    "Medicine": "Medicine",
    "Meeting": "Meeting",
    "Lunch": "Lunch",
    "Sleep": "Sleep",
    "Exercise": "Exercise",
    "Study": "Study",
    "Weekend": "Weekend",
    "Wake Up": "Wake Up",
    "Reminder": "Reminder",
    "Coffee": "Coffee",
    "Dinner": "Dinner",
    "Relax": "Relax"
}

class AlarmModel:
    """
    Model class for managing alarm data.
    Handles CRUD operations and data persistence.
    """
    
    def __init__(self, storage_file: str = "alarms.json"):
        """
        Initialize the alarm model.
        
        Args:
            storage_file: Path to JSON file for data persistence
        """
        self.storage_file = storage_file
        self.alarms: List[Alarm] = []
        self.load_alarms()
    
    def add_alarm(self, alarm: Alarm) -> str:
        """
        Add a new alarm.
        
        Args:
            alarm: Alarm object to add
            
        Returns:
            The ID of the added alarm
        """
        if not alarm.id:
            alarm.id = self._generate_id()
        
        self.alarms.append(alarm)
        self.save_alarms()
        return alarm.id
    
    def update_alarm(self, alarm_id: str, updated_alarm: Alarm) -> bool:
        """
        Update an existing alarm.
        
        Args:
            alarm_id: ID of the alarm to update
            updated_alarm: Updated alarm object
            
        Returns:
            True if update successful, False if alarm not found
        """
        for i, alarm in enumerate(self.alarms):
            if alarm.id == alarm_id:
                updated_alarm.id = alarm_id  # Ensure ID doesn't change
                self.alarms[i] = updated_alarm
                self.save_alarms()
                return True
        return False
    
    def delete_alarm(self, alarm_id: str) -> bool:
        """
        Delete an alarm.
        
        Args:
            alarm_id: ID of the alarm to delete
            
        Returns:
            True if deletion successful, False if alarm not found
        """
        for i, alarm in enumerate(self.alarms):
            if alarm.id == alarm_id:
                del self.alarms[i]
                self.save_alarms()
                return True
        return False
    
    def get_alarm(self, alarm_id: str) -> Optional[Alarm]:
        """
        Get an alarm by ID.
        
        Args:
            alarm_id: ID of the alarm to retrieve
            
        Returns:
            Alarm object if found, None otherwise
        """
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                return alarm
        return None
    
    def get_all_alarms(self) -> List[Alarm]:
        """
        Get all alarms.
        
        Returns:
            List of all alarm objects
        """
        return sorted(self.alarms, key=lambda x: x.time)
    
    def toggle_alarm(self, alarm_id: str) -> bool:
        """
        Toggle alarm enabled/disabled state.
        
        Args:
            alarm_id: ID of the alarm to toggle
            
        Returns:
            True if toggle successful, False if alarm not found
        """
        alarm = self.get_alarm(alarm_id)
        if alarm:
            alarm.enabled = not alarm.enabled
            self.save_alarms()
            return True
        return False
    
    def get_alarms_for_time(self, current_time: datetime) -> List[Alarm]:
        """
        Get all alarms that should trigger at the given time.
        
        Args:
            current_time: Current time to check
            
        Returns:
            List of alarms that should trigger
        """
        triggering_alarms = []
        for alarm in self.alarms:
            if alarm.should_trigger_today(current_time):
                triggering_alarms.append(alarm)
        return triggering_alarms
    
    def mark_alarm_triggered(self, alarm_id: str):
        """
        Mark an alarm as triggered.
        
        Args:
            alarm_id: ID of the alarm to mark as triggered
        """
        alarm = self.get_alarm(alarm_id)
        if alarm:
            alarm.last_triggered = datetime.now()
            self.save_alarms()
    
    def _generate_id(self) -> str:
        """Generate a unique ID for an alarm."""
        return str(uuid.uuid4())
    
    def save_alarms(self):
        """
        Save alarms to JSON file.
        Includes error handling and backup management.
        """
        try:
            # Create directory if it doesn't exist
            storage_dir = os.path.dirname(self.storage_file)
            if storage_dir and not os.path.exists(storage_dir):
                os.makedirs(storage_dir, exist_ok=True)
            
            # Create a backup of existing file
            if os.path.exists(self.storage_file):
                backup_file = f"{self.storage_file}.bak"
                try:
                    shutil.copy2(self.storage_file, backup_file)
                except Exception as e:
                    print(f"Warning: Could not create backup file: {e}")
            
            # Save to file
            data = [alarm.to_dict() for alarm in self.alarms]
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"Successfully saved {len(self.alarms)} alarms to {self.storage_file}")
        except Exception as e:
            print(f"Error saving alarms: {e}")
            self._restore_from_backup()
    
    def load_alarms(self):
        """
        Load alarms from JSON file.
        Handles missing, corrupted, or empty files with proper fallbacks.
        """
        self.alarms = []  # Reset alarms list
        
        # Check if file exists
        if not os.path.exists(self.storage_file):
            print(f"Alarm storage file not found: {self.storage_file}")
            return
        
        # Check if backup exists but main file is empty
        if os.path.getsize(self.storage_file) == 0 and os.path.exists(f"{self.storage_file}.bak"):
            print("Empty alarm file found, attempting to restore from backup...")
            self._restore_from_backup()
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                
            # Validate data structure
            if not isinstance(data, list):
                raise ValueError("Alarm data is not a list")
                
            valid_alarms = []
            for alarm_data in data:
                try:
                    alarm = Alarm.from_dict(alarm_data)
                    valid_alarms.append(alarm)
                except Exception as e:
                    print(f"Skipped invalid alarm data: {e}")
            
            self.alarms = valid_alarms
            print(f"Successfully loaded {len(self.alarms)} alarms")
            
        except json.JSONDecodeError:
            print(f"Error parsing alarm data: Invalid JSON format")
            self._restore_from_backup()
        except Exception as e:
            print(f"Error loading alarms: {e}")
            self._restore_from_backup()
            
    def _restore_from_backup(self):
        """Attempt to restore alarms from backup file."""
        backup_file = f"{self.storage_file}.bak"
        if not os.path.exists(backup_file):
            print("No backup file found, creating empty alarms list")
            self.alarms = []
            return
        
        try:
            print(f"Attempting to restore from backup: {backup_file}")
            with open(backup_file, 'r') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise ValueError("Backup data is not a list")
                
            self.alarms = [Alarm.from_dict(alarm_data) for alarm_data in data]
            print(f"Successfully restored {len(self.alarms)} alarms from backup")
            
            # Save the restored data to main file
            with open(self.storage_file, 'w') as f:
                json.dump([alarm.to_dict() for alarm in self.alarms], f, indent=2)
                
        except Exception as e:
            print(f"Failed to restore from backup: {e}")
            self.alarms = [] 