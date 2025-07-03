"""
Add/Edit Screen - Clean and user-friendly alarm creation interface.
iOS/Android-style scroll wheel time picker with accurate time selection.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty
from datetime import datetime, timedelta

from models.alarm_model import Alarm, ALARM_TEXT_PRESETS
from controllers.alarm_controller import AlarmController

# Clean colors
COLORS = {
    'primary': '#1976D2',
    'background': '#121212',
    'surface': '#1E1E1E',
    'on_surface': '#FFFFFF',
    'on_surface_variant': '#E0E0E0',
    'success': '#4CAF50',
    'error': '#F44336',
}

class ScrollWheelPicker(BoxLayout):
    """iOS/Android-style scroll wheel time picker with accurate time selection."""
    
    hour = NumericProperty(8)
    minute = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 15
        self.size_hint_y = None
        self.height = 180
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the scroll wheel picker."""
        # Hour wheel
        hour_section = BoxLayout(orientation='vertical', size_hint_x=0.45)
        
        hour_label = Label(
            text="Hour",
            font_size=14,
            color=get_color_from_hex(COLORS['on_surface_variant']),
            size_hint_y=None,
            height=30
        )
        hour_section.add_widget(hour_label)
        
        # Hour scroll wheel with better spacing
        self.hour_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=0,
            scroll_type=['content']
        )
        
        hour_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        hour_layout.bind(minimum_height=hour_layout.setter('height'))
        
        # Add padding for better center alignment
        hour_layout.add_widget(BoxLayout(size_hint_y=None, height=80))
        
        self.hour_buttons = []
        for h in range(24):
            btn = Button(
                text=f"{h:02d}",
                font_size=20,
                bold=True,
                size_hint_y=None,
                height=45,
                background_normal='',
                background_color=(0, 0, 0, 0),
                color=get_color_from_hex(COLORS['on_surface_variant']),
                on_press=lambda x, hour=h: self.set_hour(hour)
            )
            self.hour_buttons.append(btn)
            hour_layout.add_widget(btn)
        
        hour_layout.add_widget(BoxLayout(size_hint_y=None, height=80))
        
        self.hour_scroll.add_widget(hour_layout)
        hour_section.add_widget(self.hour_scroll)
        self.add_widget(hour_section)
        
        # Separator
        separator = Label(
            text=":",
            font_size=32,
            bold=True,
            color=get_color_from_hex(COLORS['on_surface']),
            size_hint_x=0.1
        )
        self.add_widget(separator)
        
        # Minute wheel
        minute_section = BoxLayout(orientation='vertical', size_hint_x=0.45)
        
        minute_label = Label(
            text="Minute",
            font_size=14,
            color=get_color_from_hex(COLORS['on_surface_variant']),
            size_hint_y=None,
            height=30
        )
        minute_section.add_widget(minute_label)
        
        # Minute scroll wheel
        self.minute_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=0,
            scroll_type=['content']
        )
        
        minute_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        minute_layout.bind(minimum_height=minute_layout.setter('height'))
        
        minute_layout.add_widget(BoxLayout(size_hint_y=None, height=80))
        
        self.minute_buttons = []
        for m in range(0, 60):  # All minutes 0-59
            btn = Button(
                text=f"{m:02d}",
                font_size=20,
                bold=True,
                size_hint_y=None,
                height=45,
                background_normal='',
                background_color=(0, 0, 0, 0),
                color=get_color_from_hex(COLORS['on_surface_variant']),
                on_press=lambda x, minute=m: self.set_minute(minute)
            )
            self.minute_buttons.append(btn)
            minute_layout.add_widget(btn)
        
        minute_layout.add_widget(BoxLayout(size_hint_y=None, height=80))
        
        self.minute_scroll.add_widget(minute_layout)
        minute_section.add_widget(self.minute_scroll)
        self.add_widget(minute_section)
        
        # Initial setup
        Clock.schedule_once(self._initial_setup, 0.2)
    
    def _initial_setup(self, dt):
        """Set initial scroll positions."""
        self.set_hour(self.hour)
        self.set_minute(self.minute)
    
    def set_hour(self, hour):
        """Set hour with smooth animation."""
        self.hour = hour
        
        # Calculate correct scroll position
        item_height = 50  # 45 height + 5 spacing
        target_position = hour * item_height
        
        # Get the scrollable height
        content_height = self.hour_scroll.children[0].height
        scroll_height = self.hour_scroll.height
        max_scroll = max(0, content_height - scroll_height)
        
        if max_scroll > 0:
            scroll_y = 1.0 - (target_position / max_scroll)
            scroll_y = max(0.0, min(1.0, scroll_y))
            
            # Smooth animation
            anim = Animation(scroll_y=scroll_y, duration=0.3, transition='out_cubic')
            anim.start(self.hour_scroll)
        
        self._update_hour_display()
    
    def set_minute(self, minute):
        """Set minute with smooth animation."""
        self.minute = minute
        
        # Calculate scroll position for exact minute
        item_height = 50  # 45 height + 5 spacing
        target_position = minute * item_height
        
        content_height = self.minute_scroll.children[0].height
        scroll_height = self.minute_scroll.height
        max_scroll = max(0, content_height - scroll_height)
        
        if max_scroll > 0:
            scroll_y = 1.0 - (target_position / max_scroll)
            scroll_y = max(0.0, min(1.0, scroll_y))
            
            anim = Animation(scroll_y=scroll_y, duration=0.3, transition='out_cubic')
            anim.start(self.minute_scroll)
        
        self._update_minute_display()
    
    def _update_hour_display(self):
        """Update hour button colors and sizes."""
        for i, btn in enumerate(self.hour_buttons):
            if i == self.hour:
                btn.color = get_color_from_hex(COLORS['primary'])
                btn.font_size = 24
                btn.bold = True
            else:
                btn.color = get_color_from_hex(COLORS['on_surface_variant'])
                btn.font_size = 20
                btn.bold = False
    
    def _update_minute_display(self):
        """Update minute button colors and sizes."""
        for i, btn in enumerate(self.minute_buttons):
            if i == self.minute:
                btn.color = get_color_from_hex(COLORS['primary'])
                btn.font_size = 24
                btn.bold = True
            else:
                btn.color = get_color_from_hex(COLORS['on_surface_variant'])
                btn.font_size = 20
                btn.bold = False

class AddEditScreen(Screen):
    """Clean and user-friendly alarm creation screen with text presets."""
    
    def __init__(self, alarm_controller: AlarmController, **kwargs):
        super().__init__(**kwargs)
        self.alarm_controller = alarm_controller
        self.current_alarm = None
        
        # Initialize UI components
        self.title_label = None
        self.time_picker = None
        self.label_input = None
        self.preset_buttons = []
        self.selected_preset = ""
        self.day_checkboxes = []
        self.vibrate_checkbox = None
        self.snooze_spinner = None
        self.sound_spinner = None
        self.available_sounds = []
        self.default_sound_file = "assets/sounds/default_alarm.wav"
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the clean and user-friendly UI with text presets."""
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(15)], spacing=dp(20))
        
        # Header with proper back arrow (Fixed height: 50)
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        back_btn = Button(
            text="<- BACK",
            size_hint_x=None,
            width=dp(100),
            font_size=dp(16),
            background_color=get_color_from_hex(COLORS['primary']),
            on_press=self._go_back
        )
        header.add_widget(back_btn)
        
        self.title_label = Label(
            text="Add alarm",
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['on_surface'])
        )
        header.add_widget(self.title_label)
        
        # Add spacer for balance
        header.add_widget(BoxLayout(size_hint_x=None, width=dp(100)))
        
        main_layout.add_widget(header)
        
        # Scrollable content (Flexible height)
        scroll_view = ScrollView(
            effect_cls='ScrollEffect',
            scroll_type=['content', 'bars'],
            bar_width=dp(8),
            bar_color=[0.7, 0.7, 0.7, 0.9]
        )
        content_layout = BoxLayout(orientation='vertical', spacing=dp(25), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Time section with scroll wheel (Fixed height: 220)
        content_layout.add_widget(self._create_time_section())
        
        # Label section with text presets (Fixed height: 140)
        content_layout.add_widget(self._create_label_section())
        
        # Repeat section (Fixed height: 160)
        content_layout.add_widget(self._create_repeat_section())
        
        # Options section (Fixed height: 220)
        content_layout.add_widget(self._create_options_section())
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        
        # Save button (Fixed height: 50)
        save_btn = Button(
            text="SAVE ALARM",
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            bold=True,
            background_color=get_color_from_hex(COLORS['primary']),
            on_press=self._save_alarm
        )
        main_layout.add_widget(save_btn)
        
        self.add_widget(main_layout)
    
    def _create_time_section(self):
        """Create the time picker section with fixed height."""
        section = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(220))
        
        title = Label(
            text="Set Time",
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['on_surface']),
            size_hint_y=None,
            height=dp(30)
        )
        section.add_widget(title)
        
        # iOS/Android-style scroll wheel (180px as defined in class)
        self.time_picker = ScrollWheelPicker()
        section.add_widget(self.time_picker)
        
        # Small spacer
        section.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))
        
        return section
    
    def _create_label_section(self):
        """Create label input section with text presets."""
        section = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(140))
        
        title = Label(
            text="Alarm Name & Preset",
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['on_surface']),
            size_hint_y=None,
            height=dp(25)
        )
        section.add_widget(title)
        
        # Label input
        self.label_input = TextInput(
            hint_text="Enter alarm name (auto-generated if empty)",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            padding=[dp(10), dp(8)]
        )
        section.add_widget(self.label_input)
        
        # Text presets
        preset_label = Label(
            text="Quick Presets:",
            font_size=dp(12),
            color=get_color_from_hex(COLORS['on_surface_variant']),
            size_hint_y=None,
            height=dp(20)
        )
        section.add_widget(preset_label)
        
        # Preset buttons row
        preset_row = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(35))
        
        # Common presets for quick selection
        common_presets = ["Morning", "Work", "Gym", "Medicine", "Coffee", "Lunch", "Sleep", "Reminder"]
        self.preset_buttons = []
        
        for preset in common_presets:
            btn = Button(
                text=preset,
                font_size=dp(9),
                size_hint_x=None,
                width=dp(60),
                background_color=(0.2, 0.2, 0.2, 1),
                on_press=lambda x, p=preset: self._select_preset(p)
            )
            self.preset_buttons.append(btn)
            preset_row.add_widget(btn)
        
        # Clear preset button
        clear_btn = Button(
            text="CLEAR",
            font_size=dp(9),
            size_hint_x=None,
            width=dp(50),
            background_color=get_color_from_hex(COLORS['error']),
            on_press=lambda x: self._select_preset("")
        )
        preset_row.add_widget(clear_btn)
        
        section.add_widget(preset_row)
        
        # Small spacer
        section.add_widget(BoxLayout(size_hint_y=None, height=dp(12)))
        
        return section
    
    def _select_preset(self, preset):
        """Select a text preset for the alarm."""
        self.selected_preset = preset
        if preset:
            self.label_input.text = preset
        
        # Update button colors to show selection
        for btn in self.preset_buttons:
            if btn.text == preset and preset:
                btn.background_color = get_color_from_hex(COLORS['primary'])
            else:
                btn.background_color = (0.2, 0.2, 0.2, 1)
    
    def _create_repeat_section(self):
        """Create repeat days section with fixed height."""
        section = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(160))
        
        title = Label(
            text="Repeat Days",
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['on_surface']),
            size_hint_y=None,
            height=dp(30)
        )
        section.add_widget(title)
        
        # Quick presets (Fixed height: 40)
        preset_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        presets = [
            ("Once", self._set_never),
            ("Weekdays", self._set_weekdays),
            ("Weekends", self._set_weekends),
            ("Every day", self._set_everyday)
        ]
        
        for preset_name, preset_func in presets:
            btn = Button(
                text=preset_name,
                font_size=dp(11),
                size_hint_x=0.25,
                on_press=preset_func
            )
            preset_layout.add_widget(btn)
        
        section.add_widget(preset_layout)
        
        # Day checkboxes (Fixed height: 70)
        days_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(70))
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        self.day_checkboxes = []
        for i, day_name in enumerate(day_names):
            day_box = BoxLayout(orientation='vertical', spacing=dp(2))
            
            checkbox = CheckBox(active=False, size_hint_y=0.6)
            self.day_checkboxes.append(checkbox)
            day_box.add_widget(checkbox)
            
            day_label = Label(text=day_name, font_size=dp(12), size_hint_y=0.4)
            day_box.add_widget(day_label)
            
            days_layout.add_widget(day_box)
        
        section.add_widget(days_layout)
        
        # Small spacer
        section.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        
        return section
    
    def _create_options_section(self):
        """Create options section with fixed height to prevent overlap."""
        section = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(220))
        
        title = Label(
            text="Options",
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['on_surface']),
            size_hint_y=None,
            height=dp(30)
        )
        section.add_widget(title)
        
        # Sound selection (Fixed height: 90)
        sound_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(90))
        
        sound_label = Label(
            text="Alarm Sound",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(22)
        )
        sound_layout.add_widget(sound_label)
        
        sound_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(35))
        
        # Get available sounds
        self.available_sounds = []
        try:
            from utils.audio_manager import AudioManager
            audio_manager = AudioManager()
            self.available_sounds = audio_manager.get_available_sounds()
        except Exception as e:
            print(f"Error getting available sounds: {e}")
            self.available_sounds = [{'path': 'assets/sounds/default_alarm.wav', 'name': 'Classic Alarm'}]
        
        sound_values = [sound['name'] for sound in self.available_sounds]
        
        self.sound_spinner = Spinner(
            text=sound_values[0] if sound_values else "Classic Alarm",
            values=sound_values,
            size_hint_x=0.7,
            font_size=dp(13)
        )
        sound_row.add_widget(self.sound_spinner)
        
        preview_btn = Button(
            text="PREVIEW",
            size_hint_x=0.3,
            font_size=dp(11),
            on_press=self._preview_sound
        )
        sound_row.add_widget(preview_btn)
        
        sound_layout.add_widget(sound_row)
        
        browse_btn = Button(
            text="MORE SOUNDS",
            size_hint_y=None,
            height=dp(28),
            font_size=dp(11),
            on_press=self._open_sound_browser
        )
        sound_layout.add_widget(browse_btn)
        
        section.add_widget(sound_layout)
        
        # Vibration toggle (Fixed height: 40)
        vibration_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        vibration_label = Label(
            text="Vibrate",
            font_size=dp(16),
            size_hint_x=0.8
        )
        vibration_layout.add_widget(vibration_label)
        
        self.vibrate_checkbox = CheckBox(active=True, size_hint_x=0.2)
        vibration_layout.add_widget(self.vibrate_checkbox)
        
        section.add_widget(vibration_layout)
        
        # Snooze duration (Fixed height: 40)
        snooze_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        snooze_label = Label(
            text="Snooze Duration",
            font_size=dp(16),
            size_hint_x=0.5
        )
        snooze_layout.add_widget(snooze_label)
        
        self.snooze_spinner = Spinner(
            text='5 minutes',
            values=['1 minute', '5 minutes', '10 minutes', '15 minutes', '30 minutes'],
            size_hint_x=0.5,
            font_size=dp(13)
        )
        snooze_layout.add_widget(self.snooze_spinner)
        
        section.add_widget(snooze_layout)
        
        # Bottom spacer
        section.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        
        return section
    
    def _set_never(self, instance):
        """Set no repeat days."""
        for checkbox in self.day_checkboxes:
            checkbox.active = False
    
    def _set_weekdays(self, instance):
        """Set weekdays."""
        for i, checkbox in enumerate(self.day_checkboxes):
            checkbox.active = i < 5
    
    def _set_weekends(self, instance):
        """Set weekends."""
        for i, checkbox in enumerate(self.day_checkboxes):
            checkbox.active = i >= 5
    
    def _set_everyday(self, instance):
        """Set every day."""
        for checkbox in self.day_checkboxes:
            checkbox.active = True
    
    def _save_alarm(self, instance):
        """Save the alarm without emoji support."""
        # Get values from scroll wheel picker
        time_str = f"{self.time_picker.hour:02d}:{self.time_picker.minute:02d}"
        label = self.label_input.text.strip()
        repeat_days = [i for i, cb in enumerate(self.day_checkboxes) if cb.active]
        vibrate = self.vibrate_checkbox.active
        
        # Parse snooze duration
        snooze_text = self.snooze_spinner.text
        snooze_duration = int(snooze_text.split()[0])
        
        # Get sound file
        sound_file = self.default_sound_file
        selected_name = self.sound_spinner.text
        for sound in self.available_sounds:
            if sound['name'] == selected_name:
                sound_file = sound['path']
                break
        
        success = False
        if self.current_alarm:
            # Update existing alarm
            success = self.alarm_controller.update_alarm(
                self.current_alarm.id,
                time=time_str,
                label=label,
                repeat_days=repeat_days,
                vibrate=vibrate,
                snooze_duration=snooze_duration,
                sound_file=sound_file
            )
        else:
            # Create new alarm
            alarm = Alarm(
                time=time_str,
                label=label,
                repeat_days=repeat_days,
                vibrate=vibrate,
                snooze_duration=snooze_duration,
                sound_file=sound_file
            )
            
            alarm_id = self.alarm_controller.add_alarm_object(alarm)
            success = alarm_id is not None
        
        if success:
            self._show_success("Alarm saved successfully!")
            Clock.schedule_once(lambda dt: self._go_back(), 1.5)
        else:
            self._show_error("Failed to save alarm")
    
    def _go_back(self, instance=None):
        """Go back to main screen."""
        self.manager.current = 'main'
    
    def edit_alarm(self, alarm: Alarm):
        """Load alarm for editing."""
        self.current_alarm = alarm
        self.title_label.text = "Edit alarm"
        
        # Set time using scroll wheel with delay for proper initialization
        hour, minute = alarm.time.split(':')
        Clock.schedule_once(lambda dt: self.time_picker.set_hour(int(hour)), 0.3)
        Clock.schedule_once(lambda dt: self.time_picker.set_minute(int(minute)), 0.4)
        
        # Set other fields
        self.label_input.text = alarm.label or ""
        
        # Clear preset selection
        self._select_preset("")
        
        for i, checkbox in enumerate(self.day_checkboxes):
            checkbox.active = i in alarm.repeat_days
        
        self.vibrate_checkbox.active = alarm.vibrate
        
        # Set snooze duration
        self.snooze_spinner.text = f'{alarm.snooze_duration} minutes'
        
        # Set sound
        for sound in self.available_sounds:
            if sound['path'] == alarm.sound_file:
                self.sound_spinner.text = sound['name']
                break
    
    def add_new_alarm(self):
        """Prepare for new alarm."""
        self.current_alarm = None
        self.title_label.text = "Add alarm"
        
        # Reset fields with proper timing
        Clock.schedule_once(lambda dt: self.time_picker.set_hour(8), 0.2)
        Clock.schedule_once(lambda dt: self.time_picker.set_minute(0), 0.3)
        self.label_input.text = ""
        
        # Clear preset selection
        self._select_preset("")
        
        for checkbox in self.day_checkboxes:
            checkbox.active = False
        
        self.vibrate_checkbox.active = True
        self.snooze_spinner.text = '5 minutes'
    
    def _preview_sound(self, instance):
        """Preview sound."""
        selected_name = self.sound_spinner.text
        selected_path = None
        
        for sound in self.available_sounds:
            if sound['name'] == selected_name:
                selected_path = sound['path']
                break
        
        if not selected_path:
            return
            
        try:
            from utils.audio_manager import AudioManager
            audio_manager = AudioManager()
            audio_manager.preview_sound(selected_path, 3.0)
            
            # Show feedback
            self._show_success("Playing preview...")
        except Exception as e:
            print(f"Error previewing sound: {e}")
    
    def _open_sound_browser(self, instance):
        """Open sound browser."""
        self.manager.current = 'sound_browser'
    
    def _show_success(self, message):
        """Show success message."""
        popup = Popup(
            title="Success",
            content=Label(text=message, font_size=dp(16)),
            size_hint=(0.7, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
    
    def _show_error(self, message):
        """Show error message."""
        popup = Popup(
            title="Error",
            content=Label(text=message, font_size=dp(16)),
            size_hint=(0.7, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
    
    def on_enter(self):
        """Called when screen is entered."""
        self._refresh_sound_list()
        
    def _refresh_sound_list(self):
        """Refresh sound list."""
        try:
            from utils.audio_manager import AudioManager
            audio_manager = AudioManager()
            self.available_sounds = audio_manager.get_available_sounds()
            
            sound_values = [sound['name'] for sound in self.available_sounds]
            if sound_values:
                self.sound_spinner.values = sound_values
                if self.sound_spinner.text not in sound_values:
                    self.sound_spinner.text = sound_values[0]
        except Exception as e:
            print(f"Error refreshing sound list: {e}") 