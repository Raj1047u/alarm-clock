"""
Sound Browser Screen - Simple built-in sound selection.
Clean interface for choosing alarm sounds without web downloads.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.metrics import dp

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

class SoundItem(BoxLayout):
    """Simple sound item card."""
    
    def __init__(self, sound_name, sound_path, preview_callback, **kwargs):
        super().__init__(**kwargs)
        self.sound_name = sound_name
        self.sound_path = sound_path
        self.preview_callback = preview_callback
        
        self.orientation = 'horizontal'
        self.spacing = dp(15)
        self.padding = [dp(15), dp(10)]
        self.size_hint_y = None
        self.height = dp(65)
        
        # Simple background
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.12, 0.12, 0.12, 1)  # Dark gray
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self._update_bg, size=self._update_bg)
        
        self._build_content()
    
    def _update_bg(self, instance, value):
        """Update background."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _build_content(self):
        """Build sound item content."""
        # Sound icon and name
        info_section = BoxLayout(orientation='horizontal', spacing=dp(12), size_hint_x=0.7)
        
        # Text icon instead of emoji
        icon_label = Label(
            text="SOUND",
            font_size=dp(12),
            size_hint_x=None,
            width=dp(50),
            color=get_color_from_hex(COLORS['primary'])
        )
        info_section.add_widget(icon_label)
        
        # Sound name
        name_label = Label(
            text=self.sound_name,
            font_size=dp(16),
            color=get_color_from_hex(COLORS['on_surface'])
        )
        info_section.add_widget(name_label)
        
        self.add_widget(info_section)
        
        # Preview button
        preview_btn = Button(
            text="PREVIEW",
            size_hint_x=0.3,
            font_size=dp(12),
            background_color=get_color_from_hex(COLORS['primary']),
            on_press=self._preview_sound
        )
        self.add_widget(preview_btn)
    
    def _preview_sound(self, instance):
        """Preview this sound."""
        self.preview_callback(self.sound_path, self.sound_name)

class SoundBrowserScreen(Screen):
    """Clean sound browser for built-in sounds only."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.available_sounds = []
        self._build_ui()
        self._load_sounds()
    
    def _build_ui(self):
        """Build the clean UI."""
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(20)], spacing=dp(20))
        
        # Header with back button
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
        
        title_label = Label(
            text="Alarm Sounds",
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['on_surface'])
        )
        header.add_widget(title_label)
        
        # Add spacer for balance
        header.add_widget(BoxLayout(size_hint_x=None, width=dp(100)))
        
        main_layout.add_widget(header)
        
        # Info section
        info_label = Label(
            text="Choose from our built-in alarm sounds\nSelect a sound to preview it",
            font_size=dp(14),
            color=get_color_from_hex(COLORS['on_surface_variant']),
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        main_layout.add_widget(info_label)
        
        # Sounds list with enhanced scrolling
        scroll_view = ScrollView(
            effect_cls='ScrollEffect',
            scroll_type=['content', 'bars'],
            bar_width=dp(8),
            bar_color=[0.7, 0.7, 0.7, 0.9]
        )
        self.sounds_layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        self.sounds_layout.bind(minimum_height=self.sounds_layout.setter('height'))
        
        scroll_view.add_widget(self.sounds_layout)
        main_layout.add_widget(scroll_view)
        
        # Controls section
        controls = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(15))
        
        refresh_btn = Button(
            text="REFRESH",
            size_hint_x=0.5,
            font_size=dp(14),
            on_press=self._refresh_sounds
        )
        controls.add_widget(refresh_btn)
        
        stop_btn = Button(
            text="STOP PREVIEW",
            size_hint_x=0.5,
            font_size=dp(14),
            background_color=get_color_from_hex(COLORS['error']),
            on_press=self._stop_preview
        )
        controls.add_widget(stop_btn)
        
        main_layout.add_widget(controls)
        
        self.add_widget(main_layout)
    
    def _load_sounds(self):
        """Load available sounds."""
        try:
            from utils.audio_manager import AudioManager
            audio_manager = AudioManager()
            self.available_sounds = audio_manager.get_available_sounds()
        except Exception as e:
            print(f"Error loading sounds: {e}")
            # Fallback sounds
            self.available_sounds = [
                {'path': 'assets/sounds/default_alarm.wav', 'name': 'Classic Alarm'},
                {'path': 'assets/sounds/beep_alarm.wav', 'name': 'Digital Beep'},
                {'path': 'assets/sounds/bell_alarm.wav', 'name': 'Church Bell'},
                {'path': 'assets/sounds/rooster_alarm.wav', 'name': 'Rooster Call'},
            ]
        
        self._refresh_sounds_display()
    
    def _refresh_sounds_display(self):
        """Refresh the sounds display."""
        # Clear existing items
        self.sounds_layout.clear_widgets()
        
        if not self.available_sounds:
            # No sounds message
            no_sounds_label = Label(
                text="No alarm sounds available\n\nPlease check your sound files",
                font_size=dp(16),
                color=get_color_from_hex(COLORS['on_surface_variant']),
                size_hint_y=None,
                height=dp(80),
                halign='center'
            )
            self.sounds_layout.add_widget(no_sounds_label)
            return
        
        # Add sound items
        for sound in self.available_sounds:
            sound_item = SoundItem(
                sound_name=sound['name'],
                sound_path=sound['path'],
                preview_callback=self._preview_sound
            )
            self.sounds_layout.add_widget(sound_item)
    
    def _preview_sound(self, sound_path, sound_name):
        """Preview a sound."""
        try:
            from utils.audio_manager import AudioManager
            audio_manager = AudioManager()
            audio_manager.preview_sound(sound_path, 3.0)
            
            self._show_success(f"Playing: {sound_name}")
            
        except Exception as e:
            print(f"Error previewing sound: {e}")
            self._show_error("Could not preview sound")
    
    def _refresh_sounds(self, instance):
        """Refresh sounds list."""
        self._load_sounds()
        self._show_success("Sounds refreshed")
    
    def _stop_preview(self, instance):
        """Stop any playing preview."""
        try:
            from utils.audio_manager import AudioManager
            audio_manager = AudioManager()
            audio_manager.stop_alarm_sound()
            
            self._show_success("Preview stopped")
            
        except Exception as e:
            print(f"Error stopping preview: {e}")
    
    def _go_back(self, instance):
        """Go back to previous screen."""
        self.manager.current = 'main'
    
    def _show_success(self, message):
        """Show success message."""
        popup = Popup(
            title="Info",
            content=Label(text=message, font_size=dp(16)),
            size_hint=(0.7, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
    
    def _show_error(self, message):
        """Show error message."""
        popup = Popup(
            title="Error",
            content=Label(text=message, font_size=dp(16)),
            size_hint=(0.7, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
    
    def on_enter(self):
        """Called when screen is entered."""
        self._load_sounds() 