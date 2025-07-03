"""
Notification Manager - Handles system notifications for alarms.
Provides cross-platform notification capabilities with foreground service support for Android.
"""

from typing import Optional, Dict, Callable
from kivy.utils import platform
from models.alarm_model import Alarm

class NotificationManager:
    """
    Manages system notifications for alarm events.
    Handles cross-platform notification capabilities.
    """
    
    def __init__(self):
        """Initialize the notification manager."""
        self.notification_id = 1
        self.foreground_service_running = False
        self.active_notifications: Dict[str, int] = {}  # alarm_id -> notification_id
        
        # Action callbacks (to be set by controller)
        self.on_notification_dismiss: Optional[Callable[[str], None]] = None
        self.on_notification_snooze: Optional[Callable[[str], None]] = None
        
        # Request permissions on init
        self.request_permissions()
    
    def show_alarm_notification(self, alarm: Alarm):
        """
        Show a notification for an alarm.
        
        Args:
            alarm: The alarm that triggered
        """
        title = "Alarm"
        message = f"{alarm.time} - {alarm.label}" if alarm.label else f"Alarm at {alarm.time}"
        
        if platform == 'android':
            notification_id = self._show_android_notification(title, message, alarm.id)
            self.active_notifications[alarm.id] = notification_id
            self._start_foreground_service(notification_id, title, message)
        elif platform == 'ios':
            self._show_ios_notification(title, message, alarm.id)
        else:
            # Desktop fallback
            print(f"ALARM: {title} - {message}")
    
    def show_snooze_notification(self, alarm: Alarm, snooze_time: str):
        """
        Show a notification for snoozed alarm.
        
        Args:
            alarm: The snoozed alarm
            snooze_time: When the alarm will ring again
        """
        title = "Alarm Snoozed"
        message = f"Alarm snoozed until {snooze_time}"
        
        if platform == 'android':
            notification_id = self._show_android_notification(title, message, f"{alarm.id}_snooze")
            self.active_notifications[f"{alarm.id}_snooze"] = notification_id
        elif platform == 'ios':
            self._show_ios_notification(title, message, f"{alarm.id}_snooze")
        else:
            print(f"SNOOZE: {title} - {message}")
    
    def cancel_notification(self, notification_id: str):
        """
        Cancel a notification.
        
        Args:
            notification_id: ID of the notification to cancel
        """
        if platform == 'android':
            if notification_id in self.active_notifications:
                self._cancel_android_notification(self.active_notifications[notification_id])
                del self.active_notifications[notification_id]
        elif platform == 'ios':
            self._cancel_ios_notification(notification_id)
    
    def clear_alarm_notification(self):
        """Clear the alarm notification."""
        self.cancel_all_notifications()
    
    def cancel_all_notifications(self):
        """Cancel all active notifications."""
        if platform == 'android':
            try:
                from jnius import autoclass
                
                Context = autoclass('android.content.Context')
                NotificationManager = autoclass('android.app.NotificationManager')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                
                notification_manager = activity.getSystemService(Context.NOTIFICATION_SERVICE)
                notification_manager.cancelAll()
                
                self.active_notifications.clear()
                self._stop_foreground_service()
                
            except Exception as e:
                print(f"Error canceling all notifications: {e}")
    
    def _show_android_notification(self, title: str, message: str, alarm_id: str) -> int:
        """
        Show notification on Android with action buttons.
        
        Args:
            title: Notification title
            message: Notification message
            alarm_id: Unique identifier for the notification
            
        Returns:
            Notification ID used for the Android system
        """
        try:
            from jnius import autoclass
            
            # Android notification classes
            Context = autoclass('android.content.Context')
            NotificationManager = autoclass('android.app.NotificationManager')
            Notification = autoclass('android.app.Notification')
            NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
            PendingIntent = autoclass('android.app.PendingIntent')
            Intent = autoclass('android.content.Intent')
            
            # Get current activity
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            # Get notification manager
            notification_manager = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            
            # Create notification channel (required for Android 8.0+)
            if hasattr(NotificationManager, 'createNotificationChannel'):
                channel_id = "alarm_channel"
                channel_name = "Alarm Notifications"
                channel_description = "Notifications for alarm events"
                importance = NotificationManager.IMPORTANCE_HIGH
                
                # Create channel with high importance, sound, vibration and lights
                channel = autoclass('android.app.NotificationChannel')(
                    channel_id, channel_name, importance
                )
                channel.setDescription(channel_description)
                channel.enableVibration(True)
                channel.enableLights(True)
                channel.setLightColor(0xFF0000FF)  # Blue
                channel.setSound(None, None)  # We handle sound separately
                notification_manager.createNotificationChannel(channel)
            
            # Create intent for when notification is tapped
            intent = Intent(activity, activity.getClass())
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK)
            intent.putExtra("alarm_id", alarm_id)  # Pass alarm ID to the activity
            
            pending_intent = PendingIntent.getActivity(
                activity, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Create dismiss action
            dismiss_intent = Intent(activity, activity.getClass())
            dismiss_intent.setAction("DISMISS_ALARM")
            dismiss_intent.putExtra("alarm_id", alarm_id)
            dismiss_pending_intent = PendingIntent.getActivity(
                activity, 1, dismiss_intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Create snooze action
            snooze_intent = Intent(activity, activity.getClass())
            snooze_intent.setAction("SNOOZE_ALARM")
            snooze_intent.putExtra("alarm_id", alarm_id)
            snooze_pending_intent = PendingIntent.getActivity(
                activity, 2, snooze_intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Build notification with actions
            builder = NotificationCompat.Builder(activity, "alarm_channel")
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(autoclass('android.R.drawable').ic_dialog_alert)
            builder.setPriority(NotificationCompat.PRIORITY_MAX)
            builder.setCategory(NotificationCompat.CATEGORY_ALARM)
            builder.setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            builder.setContentIntent(pending_intent)
            builder.setOngoing(True)  # User cannot dismiss by swiping
            builder.setAutoCancel(False)
            
            # Add action buttons
            builder.addAction(0, "Dismiss", dismiss_pending_intent)
            builder.addAction(0, "Snooze", snooze_pending_intent)
            
            # Use full-screen intent to show on lock screen
            builder.setFullScreenIntent(pending_intent, True)
            
            # Show notification
            notification = builder.build()
            notification_id = self.notification_id
            notification_manager.notify(notification_id, notification)
            self.notification_id += 1
            
            return notification_id
            
        except Exception as e:
            print(f"Error showing Android notification: {e}")
            return 0
    
    def _start_foreground_service(self, notification_id: int, title: str, message: str):
        """Start a foreground service to keep the alarm active."""
        if platform != 'android' or self.foreground_service_running:
            return
        
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            
            # Get Android service classes
            PythonService = autoclass('org.kivy.android.PythonService')
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            
            # Create intent for the service
            service_intent = Intent(PythonActivity.mActivity, PythonService.class_)
            service_intent.setAction("org.kivy.android.ALARM_SERVICE")
            service_intent.putExtra("title", title)
            service_intent.putExtra("message", message)
            service_intent.putExtra("notification_id", notification_id)
            
            # Start the foreground service
            activity = PythonActivity.mActivity
            activity.startForegroundService(service_intent)
            
            self.foreground_service_running = True
        except Exception as e:
            print(f"Error starting foreground service: {e}")
    
    def _stop_foreground_service(self):
        """Stop the foreground service."""
        if platform != 'android' or not self.foreground_service_running:
            return
        
        try:
            from jnius import autoclass
            
            # Get Android service classes
            PythonService = autoclass('org.kivy.android.PythonService')
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            # Create intent to stop the service
            service_intent = Intent(PythonActivity.mActivity, PythonService.class_)
            service_intent.setAction("org.kivy.android.STOP_SERVICE")
            
            # Stop the service
            activity = PythonActivity.mActivity
            activity.stopService(service_intent)
            
            self.foreground_service_running = False
        except Exception as e:
            print(f"Error stopping foreground service: {e}")
    
    def handle_notification_action(self, action: str, alarm_id: str):
        """
        Handle a notification action triggered by the user.
        
        Args:
            action: The action type ('dismiss' or 'snooze')
            alarm_id: The ID of the alarm
        """
        if action == 'dismiss' and self.on_notification_dismiss:
            self.on_notification_dismiss(alarm_id)
        elif action == 'snooze' and self.on_notification_snooze:
            self.on_notification_snooze(alarm_id)
    
    def _show_ios_notification(self, title: str, message: str, alarm_id: str):
        """
        Show notification on iOS.
        
        Args:
            title: Notification title
            message: Notification message
            alarm_id: Unique identifier for the notification
        """
        try:
            # iOS notifications would require additional setup with pyobjus
            # For now, just print to console
            print(f"iOS Notification: {title} - {message}")
        except Exception as e:
            print(f"Error showing iOS notification: {e}")
    
    def _cancel_android_notification(self, notification_id: str):
        """
        Cancel notification on Android.
        
        Args:
            notification_id: ID of the notification to cancel
        """
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            NotificationManager = autoclass('android.app.NotificationManager')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            notification_manager = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            notification_manager.cancel(self.notification_id - 1)
            
        except Exception as e:
            print(f"Error canceling Android notification: {e}")
    
    def _cancel_ios_notification(self, notification_id: str):
        """
        Cancel notification on iOS.
        
        Args:
            notification_id: ID of the notification to cancel
        """
        try:
            # iOS notification cancellation would require pyobjus
            print(f"iOS notification canceled: {notification_id}")
        except Exception as e:
            print(f"Error canceling iOS notification: {e}")
    
    def request_permissions(self):
        """
        Request notification permissions (Android 13+).
        """
        if platform == 'android':
            try:
                from jnius import autoclass
                
                Context = autoclass('android.content.Context')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                
                # Check if permission is needed (Android 13+)
                if hasattr(autoclass('android.Manifest$permission'), 'POST_NOTIFICATIONS'):
                    permission = autoclass('android.Manifest$permission').POST_NOTIFICATIONS
                    
                    # Request permission if not granted
                    if activity.checkSelfPermission(permission) != Context.PERMISSION_GRANTED:
                        activity.requestPermissions([permission], 1)
                        
            except Exception as e:
                print(f"Error requesting notification permissions: {e}")
    
    def has_permission(self) -> bool:
        """
        Check if notification permission is granted.
        
        Returns:
            True if permission granted, False otherwise
        """
        if platform == 'android':
            try:
                from jnius import autoclass
                
                Context = autoclass('android.content.Context')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                
                if hasattr(autoclass('android.Manifest$permission'), 'POST_NOTIFICATIONS'):
                    permission = autoclass('android.Manifest$permission').POST_NOTIFICATIONS
                    return activity.checkSelfPermission(permission) == Context.PERMISSION_GRANTED
                
                return True  # Pre-Android 13 doesn't need explicit permission
                
            except Exception as e:
                print(f"Error checking notification permission: {e}")
                return False
        
        return True  # Desktop/iOS assume permission granted 