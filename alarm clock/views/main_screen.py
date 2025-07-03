"""
Main Screen - Material Design alarm clock interface with animations and swipe navigation.
Enhanced with KivyMD components, elevation, and smooth transitions.
"""

from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from datetime import datetime

# KivyMD imports for Material Design
try:
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivymd.uix.button import MDIconButton, MDRaisedButton
    from kivymd.uix.switch import MDSwitch
    KIVYMD_AVAILABLE = True
except ImportError:
    KIVYMD_AVAILABLE = False
    print("KivyMD not available, using standard Kivy components")

from controllers.alarm_controller import AlarmController
from models.alarm_model import Alarm

# Material Design color schemes
LIGHT_THEME = {
    'primary': '#1976D2',
    'background': '#FAFAFA',
    'surface': '#FFFFFF',
    'on_surface': '#212121',
    'on_surface_variant': '#757575',
    'success': '#4CAF50',
    'error': '#F44336',
    'card_enabled': (0.2, 0.6, 1, 0.1),
    'card_disabled': (0.8, 0.1, 0.1, 0.05),
}

DARK_THEME = {
    'primary': '#2196F3',
    'background': '#121212',
    'surface': '#1E1E1E',
    'on_surface': '#FFFFFF',
    'on_surface_variant': '#E0E0E0',
    'success': '#4CAF50',
    'error': '#F44336',
    'card_enabled': (0.2, 0.6, 1, 0.15),
    'card_disabled': (0.8, 0.1, 0.1, 0.1),
}

class MaterialAlarmCard(MDCard if KIVYMD_AVAILABLE else BoxLayout):
    """Material Design alarm card with elevation and icons."""
    
    def __init__(self, alarm: Alarm, delete_callback, edit_callback, toggle_callback, theme_colors, **kwargs):
        super().__init__(**kwargs)
        self.alarm = alarm
        self.delete_callback = delete_callback
        self.edit_callback = edit_callback
        self.toggle_callback = toggle_callback
        self.theme_colors = theme_colors
        
        if KIVYMD_AVAILABLE:
            # KivyMD Card properties
            self.orientation = 'horizontal'
            self.elevation = 6 if alarm.enabled else 2
            self.radius = [20, 20, 20, 20]
            self.size_hint_y = None
            self.height = dp(90)
            self.padding = [dp(15), dp(10)]
            self.spacing = dp(8)
            self.md_bg_color = theme_colors['surface']
        else:
            # Fallback to custom BoxLayout with rounded rectangle
            self.orientation = 'horizontal'
            self.size_hint_y = None
            self.height = dp(90)
            self.padding = [dp(15), dp(10)]
            self.spacing = dp(8)
            
            # Custom rounded rectangle background
            with self.canvas.before:
                self.bg_color = Color(*theme_colors['card_enabled'] if alarm.enabled else theme_colors['card_disabled'])
                self.bg_rect = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[15, 15, 15, 15]
                )
                self.bind(pos=self._update_bg, size=self._update_bg)
        
        self._build_content()
        
        # Add entrance animation
        self.opacity = 0
        self.scale = 0.8
        Clock.schedule_once(self._animate_entrance, 0.1)
    
    def _update_bg(self, instance, value):
        """Update background rectangle for non-KivyMD version."""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def _animate_entrance(self, dt):
        """Animate card entrance with smooth scale and fade."""
        anim = Animation(opacity=1, scale=1, duration=0.4, transition='out_back')
        anim.start(self)
    
    def _build_content(self):
        """Build Material Design card content."""
        # Time section with text icon
        time_section = BoxLayout(orientation='horizontal', size_hint_x=0.35, spacing=dp(8))
        
        if KIVYMD_AVAILABLE:
            # Use Material Design icon
            time_icon = MDIconButton(
                icon="alarm" if self.alarm.enabled else "alarm-off",
                theme_icon_color="Primary" if self.alarm.enabled else "Hint",
                size_hint_x=None,
                width=dp(40)
            )
            time_section.add_widget(time_icon)
            
            time_label = MDLabel(
                text=self.alarm.time,
                font_style="H5",
                theme_text_color="Primary" if self.alarm.enabled else "Hint",
                bold=True
            )
        else:
            # Text icon instead of emoji
            time_icon = Label(
                text="ALARM" if self.alarm.enabled else "OFF",
                font_size=dp(8),
                size_hint_x=None,
                width=dp(40),
                color=get_color_from_hex(self.theme_colors['primary']) if self.alarm.enabled else get_color_from_hex(self.theme_colors['on_surface_variant'])
            )
            time_section.add_widget(time_icon)
            
            time_label = Label(
                text=self.alarm.time,
                font_size=dp(20),
                bold=True,
                color=get_color_from_hex(self.theme_colors['on_surface']) if self.alarm.enabled else get_color_from_hex(self.theme_colors['on_surface_variant'])
            )
        
        time_section.add_widget(time_label)
        self.add_widget(time_section)
        
        # Label section
        label_section = BoxLayout(orientation='vertical', size_hint_x=0.3)
        
        if KIVYMD_AVAILABLE:
            alarm_label = MDLabel(
                text=self.alarm.get_display_label(),
                font_style="Subtitle1",
                theme_text_color="Primary" if self.alarm.enabled else "Hint"
            )
            
            # Repeat info with proper spacing
            if self.alarm.repeat_days:
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                repeat_text = ', '.join([days[i] for i in self.alarm.repeat_days])
            else:
                repeat_text = "Once"
            
            repeat_label = MDLabel(
                text=repeat_text,
                font_style="Caption",
                theme_text_color="Hint"
            )
        else:
            alarm_label = Label(
                text=self.alarm.get_display_label(),
                font_size=dp(14),
                color=get_color_from_hex(self.theme_colors['on_surface']) if self.alarm.enabled else get_color_from_hex(self.theme_colors['on_surface_variant'])
            )
            
            if self.alarm.repeat_days:
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                repeat_text = ', '.join([days[i] for i in self.alarm.repeat_days])
            else:
                repeat_text = "Once"
            
            repeat_label = Label(
                text=repeat_text,
                font_size=dp(11),
                color=get_color_from_hex(self.theme_colors['on_surface_variant'])
            )
        
        label_section.add_widget(alarm_label)
        label_section.add_widget(repeat_label)
        self.add_widget(label_section)
        
        # Controls section with added delete button
        controls_section = BoxLayout(orientation='horizontal', size_hint_x=0.35, spacing=dp(5))
        
        if KIVYMD_AVAILABLE:
            # Material Design switch
            toggle = MDSwitch(
                active=self.alarm.enabled,
                size_hint_x=0.4
            )
            toggle.bind(active=self._on_toggle)
            
            # Edit button with icon
            edit_btn = MDIconButton(
                icon="pencil",
                theme_icon_color="Primary",
                size_hint_x=0.3,
                on_press=lambda x: self._animate_edit()
            )
            
            # Delete button
            delete_btn = MDIconButton(
                icon="delete",
                theme_icon_color="Error",
                size_hint_x=0.3,
                on_press=lambda x: self._animate_delete()
            )
        else:
            toggle = Switch(
                active=self.alarm.enabled,
                size_hint_x=0.4
            )
            toggle.bind(active=self._on_toggle)
            
            edit_btn = Button(
                text="EDIT",
                font_size=dp(10),
                size_hint_x=0.3,
                background_color=get_color_from_hex(self.theme_colors['primary']),
                on_press=lambda x: self._animate_edit()
            )
            
            delete_btn = Button(
                text="DEL",
                font_size=dp(10),
                size_hint_x=0.3,
                background_color=get_color_from_hex(self.theme_colors['error']),
                on_press=lambda x: self._animate_delete()
            )
        
        controls_section.add_widget(toggle)
        controls_section.add_widget(edit_btn)
        controls_section.add_widget(delete_btn)
        self.add_widget(controls_section)
    
    def _on_toggle(self, instance, value):
        """Handle toggle with animation."""
        self.toggle_callback(self.alarm.id, value)
        
        # Animate elevation change for KivyMD
        if KIVYMD_AVAILABLE:
            new_elevation = 6 if value else 2
            anim = Animation(elevation=new_elevation, duration=0.3)
            anim.start(self)
        
        # Pulse animation
        pulse = Animation(scale=1.05, duration=0.1) + Animation(scale=1, duration=0.1)
        pulse.start(self)
    
    def _animate_edit(self):
        """Animate edit button press."""
        # Scale animation
        anim = Animation(scale=0.95, duration=0.1) + Animation(scale=1, duration=0.1)
        anim.bind(on_complete=lambda *args: self.edit_callback(self.alarm))
        anim.start(self)
    
    def _animate_delete(self):
        """Animate delete button press."""
        # Scale animation
        anim = Animation(scale=0.95, duration=0.1) + Animation(scale=1, duration=0.1)
        anim.bind(on_complete=lambda *args: self.delete_callback(self.alarm.id))
        anim.start(self)

class MainScreen(Screen):
    """Material Design main screen with swipe navigation and animations."""
    
    def __init__(self, alarm_controller: AlarmController, **kwargs):
        super().__init__(**kwargs)
        self.alarm_controller = alarm_controller
        self.theme = "dark"  # Default theme
        self.current_colors = DARK_THEME
        self.app = None  # Will be set when screen is added to manager
        
        # UI components
        self.time_label = None
        self.date_label = None
        self.alarm_list = None
        self.no_alarms_label = None
        self.theme_toggle = None
        
        # Touch tracking for swipe detection
        self.touch_start_x = 0
        self.swipe_threshold = dp(100)
        
        self._build_ui()
        
        # Update time every second
        Clock.schedule_interval(self._update_time, 1)
    
    def on_pre_enter(self):
        """Called before screen is displayed."""
        # Get reference to the app
        from kivy.app import App
        self.app = App.get_running_app()
        
        # Sync theme with app
        if self.app and hasattr(self.app, 'theme'):
            self.update_theme(self.app.theme)
    
    def _build_ui(self):
        """Build the Material Design main UI with theme toggle."""
        main_layout = BoxLayout(orientation='vertical', padding=[dp(15), dp(15)], spacing=dp(15))
        
        # Header with time and theme toggle
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(5))
        
        # Top row with theme toggle
        top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        # Spacer on left
        top_row.add_widget(BoxLayout())
        
        # Theme toggle button with text instead of emoji
        self.theme_toggle = ToggleButton(
            text="LIGHT" if self.theme == "dark" else "DARK",
            size_hint=(None, None),
            size=(dp(70), dp(40)),
            on_press=self.toggle_theme
        )
        top_row.add_widget(self.theme_toggle)
        
        header.add_widget(top_row)
        
        # Time display
        self.time_label = Label(
            text="00:00",
            font_size=dp(40),
            bold=True,
            color=get_color_from_hex(self.current_colors['on_surface']),
            size_hint_y=None,
            height=dp(50)
        )
        header.add_widget(self.time_label)
        
        self.date_label = Label(
            text="Today",
            font_size=dp(14),
            color=get_color_from_hex(self.current_colors['on_surface_variant']),
            size_hint_y=None,
            height=dp(25)
        )
        header.add_widget(self.date_label)
        
        main_layout.add_widget(header)
        
        # Section header with FAB-style add button
        section_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(15))
        
        alarms_title = Label(
            text="Your Alarms",
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(self.current_colors['on_surface']),
            size_hint_x=0.65
        )
        section_header.add_widget(alarms_title)
        
        if KIVYMD_AVAILABLE:
            add_btn = MDRaisedButton(
                text="ADD ALARM",
                size_hint_x=0.35,
                on_press=self._animate_add_alarm
            )
        else:
            add_btn = Button(
                text="ADD ALARM",
                size_hint_x=0.35,
                font_size=dp(13),
                bold=True,
                background_color=get_color_from_hex(self.current_colors['primary']),
                on_press=self._animate_add_alarm
            )
        
        section_header.add_widget(add_btn)
        main_layout.add_widget(section_header)
        
        # Alarms list with smooth scrolling
        self.alarm_scroll = ScrollView(
            effect_cls='ScrollEffect',
            scroll_type=['content', 'bars'],
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            bar_inactive_color=[0.7, 0.7, 0.7, 0.5]
        )
        self.alarm_list = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=[0, dp(10)]
        )
        self.alarm_list.bind(minimum_height=self.alarm_list.setter('height'))
        
        # No alarms message
        self.no_alarms_label = Label(
            text="No alarms set\n\nTap 'ADD ALARM' to create an alarm",
            font_size=dp(15),
            color=get_color_from_hex(self.current_colors['on_surface_variant']),
            size_hint_y=None,
            height=dp(80)
        )
        
        self.alarm_scroll.add_widget(self.alarm_list)
        main_layout.add_widget(self.alarm_scroll)
        
        # Settings button
        if KIVYMD_AVAILABLE:
            settings_btn = MDRaisedButton(
                text="SOUND SETTINGS",
                size_hint_y=None,
                height=dp(45),
                on_press=self._animate_sound_settings
            )
        else:
            settings_btn = Button(
                text="SOUND SETTINGS",
                size_hint_y=None,
                height=dp(45),
                font_size=dp(14),
                on_press=self._animate_sound_settings
            )
        
        main_layout.add_widget(settings_btn)
        self.add_widget(main_layout)
        
        # Initial setup
        self._update_time()
        self._refresh_alarms()
    
    def toggle_theme(self, instance=None):
        """Toggle between light and dark themes by calling app's method."""
        if self.app and hasattr(self.app, 'toggle_theme'):
            self.app.toggle_theme()
        else:
            # Fallback - toggle locally if app not available
            self.theme = "light" if self.theme == "dark" else "dark"
            self.update_theme(self.theme)
    
    def update_theme(self, new_theme):
        """Update theme from app or other source."""
        self.theme = new_theme
        self.current_colors = LIGHT_THEME if self.theme == "light" else DARK_THEME
        
        # Update window background color
        bg_color = get_color_from_hex(self.current_colors['background'])
        Window.clearcolor = (*bg_color[:3], 1.0)  # Convert to RGBA with alpha=1
        
        # Update theme toggle button text
        if self.theme_toggle:
            self.theme_toggle.text = "LIGHT" if self.theme == "dark" else "DARK"
        
        # Animate theme change
        if hasattr(self, '_animate_theme_change'):
            anim = Animation(opacity=0.7, duration=0.2) + Animation(opacity=1, duration=0.2)
            anim.start(self)
        
        # Apply new colors to existing widgets
        self._apply_theme_colors()
        
        # Refresh alarms to apply new theme
        self._refresh_alarms()
        
        print(f"MainScreen theme updated to: {self.theme}")
    
    def _apply_theme_colors(self):
        """Apply theme colors to widgets."""
        if not hasattr(self, 'time_label') or not self.time_label:
            return
            
        # Update main UI elements
        self.time_label.color = get_color_from_hex(self.current_colors['on_surface'])
        self.date_label.color = get_color_from_hex(self.current_colors['on_surface_variant'])
        self.no_alarms_label.color = get_color_from_hex(self.current_colors['on_surface_variant'])
        
        # Update section title and buttons
        # Find and update the "Your Alarms" title
        main_layout = self.children[0]  # The main BoxLayout
        if hasattr(main_layout, 'children') and len(main_layout.children) >= 3:
            section_header = main_layout.children[-3]  # Section header is third from bottom
            if hasattr(section_header, 'children') and len(section_header.children) >= 2:
                # Update "Your Alarms" title
                alarms_title = section_header.children[1]  # Second child (right to left)
                if hasattr(alarms_title, 'color'):
                    alarms_title.color = get_color_from_hex(self.current_colors['on_surface'])
                
                # Update ADD ALARM button (if not using KivyMD)
                add_btn = section_header.children[0]  # First child (rightmost)
                if hasattr(add_btn, 'background_color') and not KIVYMD_AVAILABLE:
                    add_btn.background_color = get_color_from_hex(self.current_colors['primary'])
            
            # Update SOUND SETTINGS button (if not using KivyMD)
            settings_btn = main_layout.children[0]  # Bottom-most child
            if hasattr(settings_btn, 'background_color') and not KIVYMD_AVAILABLE:
                settings_btn.background_color = get_color_from_hex(self.current_colors['primary'])
        
        print(f"Applied {self.theme} theme colors to UI elements")
    
    def on_touch_down(self, touch):
        """Track touch start for swipe detection."""
        self.touch_start_x = touch.x
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """Detect swipe gestures for navigation."""
        if hasattr(self, 'touch_start_x'):
            swipe_distance = touch.x - self.touch_start_x
            
            if abs(swipe_distance) > self.swipe_threshold:
                if swipe_distance > 0:  # Swipe right
                    self._swipe_right()
                else:  # Swipe left
                    self._swipe_left()
        
        return super().on_touch_up(touch)
    
    def _swipe_left(self):
        """Handle swipe left gesture - go to add alarm."""
        self.manager.transition = SlideTransition(direction='left')
        add_edit_screen = self.manager.get_screen('add_edit')
        add_edit_screen.add_new_alarm()
        self.manager.current = 'add_edit'
    
    def _swipe_right(self):
        """Handle swipe right gesture - go to sound browser."""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'sound_browser'
    
    def _update_time(self, dt=None):
        """Update current time display."""
        now = datetime.now()
        self.time_label.text = now.strftime("%H:%M")
        self.date_label.text = now.strftime("%A, %B %d")
    
    def _refresh_alarms(self):
        """Refresh the alarms list with animations."""
        # Clear existing alarms
        self.alarm_list.clear_widgets()
        
        # Get alarms
        alarms = self.alarm_controller.get_all_alarms()
        
        if not alarms:
            # Show no alarms message
            self.alarm_list.add_widget(self.no_alarms_label)
        else:
            # Add alarm cards with staggered animations
            for i, alarm in enumerate(alarms):
                card = MaterialAlarmCard(
                    alarm=alarm,
                    delete_callback=self._delete_alarm,
                    edit_callback=self._edit_alarm,
                    toggle_callback=self._toggle_alarm,
                    theme_colors=self.current_colors
                )
                self.alarm_list.add_widget(card)
                
                # Stagger the animations slightly
                Clock.schedule_once(lambda dt, c=card: c._animate_entrance(dt), i * 0.05)
    
    def _animate_add_alarm(self, instance):
        """Animate add alarm button press."""
        # Use opacity animation instead of scale for regular buttons
        anim = Animation(opacity=0.7, duration=0.1) + Animation(opacity=1, duration=0.1)
        anim.bind(on_complete=lambda *args: self._add_alarm())
        anim.start(instance)
    
    def _add_alarm(self):
        """Add new alarm with slide transition."""
        self.manager.transition = SlideTransition(direction='left')
        add_edit_screen = self.manager.get_screen('add_edit')
        add_edit_screen.add_new_alarm()
        self.manager.current = 'add_edit'
    
    def _edit_alarm(self, alarm: Alarm):
        """Edit existing alarm."""
        self.manager.transition = SlideTransition(direction='left')
        add_edit_screen = self.manager.get_screen('add_edit')
        add_edit_screen.edit_alarm(alarm)
        self.manager.current = 'add_edit'
    
    def _toggle_alarm(self, alarm_id: str, enabled: bool):
        """Toggle alarm on/off."""
        success = self.alarm_controller.toggle_alarm(alarm_id)
        if success:
            status = "enabled" if enabled else "disabled"
            self._show_success(f"Alarm {status}")
        else:
            self._show_error("Failed to toggle alarm")
    
    def _delete_alarm(self, alarm_id: str):
        """Delete alarm with animation."""
        # Find the card to animate out
        for card in self.alarm_list.children:
            if hasattr(card, 'alarm') and card.alarm.id == alarm_id:
                # Animate card out
                anim = Animation(opacity=0, scale=0.8, duration=0.3)
                anim.bind(on_complete=lambda *args: self._complete_delete(alarm_id))
                anim.start(card)
                return
        
        # Fallback if card not found
        self._complete_delete(alarm_id)
    
    def _complete_delete(self, alarm_id: str):
        """Complete alarm deletion."""
        success = self.alarm_controller.delete_alarm(alarm_id)
        if success:
            self._show_success("Alarm deleted")
            self._refresh_alarms()
        else:
            self._show_error("Failed to delete alarm")
    
    def _animate_sound_settings(self, instance):
        """Animate sound settings button press."""
        # Use opacity animation instead of scale for regular buttons
        anim = Animation(opacity=0.7, duration=0.1) + Animation(opacity=1, duration=0.1)
        anim.bind(on_complete=lambda *args: self._open_sound_settings())
        anim.start(instance)
    
    def _open_sound_settings(self):
        """Open sound browser."""
        self.manager.transition = SlideTransition(direction='up')
        self.manager.current = 'sound_browser'
    
    def _show_success(self, message):
        """Show success message with fade animation."""
        popup = Popup(
            title="Success",
            content=Label(text=message, font_size=dp(16)),
            size_hint=(0.7, 0.3)
        )
        
        # Animate popup entrance
        popup.opacity = 0
        popup.open()
        anim = Animation(opacity=1, duration=0.3)
        anim.start(popup)
        
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
        self._refresh_alarms() 