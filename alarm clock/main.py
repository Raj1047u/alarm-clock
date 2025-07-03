#!/usr/bin/env python3
"""
Alarm Clock App - Main Entry Point
A Material Design alarm clock application with animations and theme support.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import platform

# Try to import KivyMD for Material Design
try:
    from kivymd.app import MDApp
    KIVYMD_AVAILABLE = True
except ImportError:
    KIVYMD_AVAILABLE = False
    print("KivyMD not available, using standard Kivy App")

# Import our custom modules
from views.main_screen import MainScreen
from views.add_edit_screen import AddEditScreen
from views.sound_browser_screen import SoundBrowserScreen
from controllers.alarm_controller import AlarmController

class AlarmClockApp(App):
    """
    Main application class for the Alarm Clock app.
    Material Design with theme support and smooth animations.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Alarm Clock"
        self.icon = "assets/icon.png"
        
        # Theme management
        self.theme = "dark"  # Default theme
        
        # KivyMD theme setup if available
        if KIVYMD_AVAILABLE and hasattr(self, 'theme_cls'):
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.accent_palette = "Amber"
        
        # Initialize controller (which handles all dependencies)
        self.alarm_controller = AlarmController()
        
        # Screen manager
        self.screen_manager = None
        
        # Request permissions for Android
        if platform == 'android':
            self._request_android_permissions()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme = "light" if self.theme == "dark" else "dark"
        
        # Apply KivyMD theme if available
        if KIVYMD_AVAILABLE and hasattr(self, 'theme_cls'):
            self.theme_cls.theme_style = "Light" if self.theme == "light" else "Dark"
        
        # Notify main screen to update theme
        if self.screen_manager:
            main_screen = self.screen_manager.get_screen('main')
            if hasattr(main_screen, 'update_theme'):
                main_screen.update_theme(self.theme)
        
        print(f"Theme switched to: {self.theme}")
    
    def _request_android_permissions(self):
        """Request necessary Android permissions."""
        try:
            # Dynamic import of Android modules
            android_permissions = __import__('android.permissions', fromlist=['request_permissions', 'Permission'])
            request_permissions = android_permissions.request_permissions
            Permission = android_permissions.Permission
            
            permissions = [
                Permission.VIBRATE,
                Permission.WAKE_LOCK,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ]
            
            # Add notification permission for Android 13+
            try:
                notifications_permission = getattr(Permission, "POST_NOTIFICATIONS", None)
                if notifications_permission:
                    permissions.append(notifications_permission)
            except:
                pass
                
            request_permissions(permissions)
            
        except ImportError:
            # Not on Android or android.permissions not available
            pass
            
    def build(self):
        """Build the application UI with Material Design."""
        # Set window size for desktop testing
        if platform == 'desktop' or platform == 'win':
            Window.size = (400, 700)
        
        # Create screen manager
        self.screen_manager = ScreenManager()
        
        # Create and add screens
        main_screen = MainScreen(name='main', alarm_controller=self.alarm_controller)
        add_edit_screen = AddEditScreen(name='add_edit', alarm_controller=self.alarm_controller)
        sound_browser_screen = SoundBrowserScreen(name='sound_browser')
        
        self.screen_manager.add_widget(main_screen)
        self.screen_manager.add_widget(add_edit_screen)
        self.screen_manager.add_widget(sound_browser_screen)
        
        # Set up theme connection and initialize theme
        main_screen.app = self
        main_screen.update_theme(self.theme)
        
        return self.screen_manager
    
    def on_stop(self):
        """Called when the app is closing."""
        # Stop the alarm controller
        if hasattr(self, 'alarm_controller'):
            self.alarm_controller.stop()
    
    def on_pause(self):
        """Handle app pause (important for mobile)."""
        return True
    
    def on_resume(self):
        """Handle app resume."""
        pass

if __name__ == '__main__':
    AlarmClockApp().run() 