"""
AI Learning Module - Smart alarm pattern recognition and suggestions.
Uses machine learning to analyze user behavior and provide intelligent alarm recommendations.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Try to import ML libraries
try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import pandas as pd
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

class SmartAlarmLearner:
    """AI-powered alarm learning system that analyzes user patterns."""
    
    def __init__(self, data_file: str = "user_alarm_data.json"):
        self.data_file = data_file
        self.user_data = self._load_user_data()
        
        # Initialize ML components if available
        if ML_AVAILABLE:
            self.scaler = StandardScaler()
            self.kmeans = KMeans(n_clusters=5, random_state=42)
        
        self.logger = logging.getLogger(__name__)
    
    def _load_user_data(self) -> Dict:
        """Load existing user data or create new structure."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load user data: {e}")
        
        return {
            'alarm_history': [],
            'usage_patterns': {},
            'preferences': {},
            'snooze_patterns': {},
            'wake_times': [],
            'sleep_patterns': {},
            'location_patterns': {},
            'created_date': datetime.now().isoformat()
        }
    
    def _save_user_data(self):
        """Save user data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save user data: {e}")
    
    def record_alarm_creation(self, alarm_time: str, label: str, repeat_days: List[int], 
                            creation_method: str = "manual"):
        """Record when user creates an alarm."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'alarm_time': alarm_time,
            'label': label,
            'repeat_days': repeat_days,
            'creation_method': creation_method,  # manual, voice, suggestion
            'day_of_week': datetime.now().weekday(),
            'hour_of_creation': datetime.now().hour
        }
        
        self.user_data['alarm_history'].append(record)
        self._save_user_data()
    
    def record_alarm_interaction(self, alarm_id: str, action: str, timestamp: str = None):
        """Record user interactions with alarms (dismiss, snooze, etc.)."""
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        interaction = {
            'alarm_id': alarm_id,
            'action': action,  # dismiss, snooze, disable
            'timestamp': timestamp,
            'day_of_week': datetime.now().weekday(),
            'time_of_day': datetime.now().hour
        }
        
        if 'interactions' not in self.user_data:
            self.user_data['interactions'] = []
        
        self.user_data['interactions'].append(interaction)
        self._save_user_data()
    
    def record_snooze_behavior(self, alarm_id: str, snooze_count: int, final_wake_time: str):
        """Record snooze patterns for adaptive snooze suggestions."""
        snooze_record = {
            'alarm_id': alarm_id,
            'snooze_count': snooze_count,
            'final_wake_time': final_wake_time,
            'date': datetime.now().date().isoformat(),
            'day_of_week': datetime.now().weekday()
        }
        
        if alarm_id not in self.user_data['snooze_patterns']:
            self.user_data['snooze_patterns'][alarm_id] = []
        
        self.user_data['snooze_patterns'][alarm_id].append(snooze_record)
        self._save_user_data()
    
    def get_smart_time_suggestions(self, context: str = "") -> List[Tuple[str, str, float]]:
        """Get AI-powered time suggestions based on user patterns."""
        suggestions = []
        
        if not ML_AVAILABLE:
            return self._get_rule_based_suggestions(context)
        
        try:
            # Analyze historical data
            df = pd.DataFrame(self.user_data['alarm_history'])
            
            if len(df) < 5:
                return self._get_rule_based_suggestions(context)
            
            # Extract features
            df['hour'] = df['alarm_time'].apply(lambda x: int(x.split(':')[0]))
            df['minute'] = df['alarm_time'].apply(lambda x: int(x.split(':')[1]))
            df['creation_hour'] = df['hour_of_creation']
            df['day_of_week'] = df['day_of_week']
            
            # Cluster similar alarm patterns
            features = ['hour', 'minute', 'day_of_week', 'creation_hour']
            X = df[features].values
            
            if len(X) >= 5:
                X_scaled = self.scaler.fit_transform(X)
                clusters = self.kmeans.fit_predict(X_scaled)
                
                # Find most common patterns
                cluster_centers = self.kmeans.cluster_centers_
                cluster_centers_original = self.scaler.inverse_transform(cluster_centers)
                
                for i, center in enumerate(cluster_centers_original):
                    hour, minute, day_of_week, creation_hour = center
                    time_str = f"{int(hour):02d}:{int(minute):02d}"
                    
                    # Calculate confidence based on cluster size
                    cluster_size = np.sum(clusters == i)
                    confidence = min(cluster_size / len(X), 1.0)
                    
                    # Generate context-aware label
                    label = self._generate_smart_label(hour, day_of_week, context)
                    
                    suggestions.append((time_str, label, confidence))
            
        except Exception as e:
            self.logger.warning(f"ML analysis failed: {e}")
            return self._get_rule_based_suggestions(context)
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return suggestions[:4]
    
    def _get_rule_based_suggestions(self, context: str) -> List[Tuple[str, str, float]]:
        """Fallback rule-based suggestions when ML is not available."""
        suggestions = []
        
        # Analyze most common times from history
        if self.user_data['alarm_history']:
            time_counts = {}
            for record in self.user_data['alarm_history']:
                time_str = record['alarm_time']
                time_counts[time_str] = time_counts.get(time_str, 0) + 1
            
            # Get top 3 most used times
            sorted_times = sorted(time_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for time_str, count in sorted_times:
                confidence = min(count / len(self.user_data['alarm_history']), 1.0)
                label = f"Your usual time"
                suggestions.append((time_str, label, confidence))
        
        # Add context-based suggestions
        context_suggestions = self._get_context_suggestions(context)
        suggestions.extend(context_suggestions)
        
        return suggestions[:4]
    
    def _get_context_suggestions(self, context: str) -> List[Tuple[str, str, float]]:
        """Get suggestions based on context keywords."""
        context_lower = context.lower()
        suggestions = []
        
        if 'work' in context_lower or 'office' in context_lower:
            suggestions.append(("07:00", "Work Start", 0.8))
            suggestions.append(("06:30", "Early Work", 0.6))
        
        if 'gym' in context_lower or 'workout' in context_lower:
            suggestions.append(("06:00", "Morning Workout", 0.8))
            suggestions.append(("17:30", "Evening Workout", 0.6))
        
        if 'weekend' in context_lower:
            suggestions.append(("09:00", "Weekend Relaxed", 0.7))
            suggestions.append(("10:30", "Late Weekend", 0.5))
        
        if 'medicine' in context_lower or 'pills' in context_lower:
            suggestions.append(("08:00", "Morning Medicine", 0.8))
            suggestions.append(("22:00", "Evening Medicine", 0.8))
        
        return suggestions
    
    def _generate_smart_label(self, hour: float, day_of_week: float, context: str) -> str:
        """Generate intelligent labels based on time and context."""
        hour_int = int(hour)
        
        # Time-based patterns
        if 5 <= hour_int <= 7:
            if 'gym' in context.lower():
                return "Early Workout"
            elif day_of_week < 5:  # Weekdays
                return "Early Work"
            else:
                return "Early Weekend"
        
        elif 7 <= hour_int <= 9:
            if day_of_week < 5:
                return "Work/School"
            else:
                return "Weekend Morning"
        
        elif 9 <= hour_int <= 11:
            return "Late Morning"
        
        elif 18 <= hour_int <= 20:
            return "Evening Activity"
        
        elif 21 <= hour_int <= 23:
            return "Bedtime Routine"
        
        else:
            return "Custom Time"
    
    def get_adaptive_snooze_duration(self, alarm_id: str) -> int:
        """Calculate optimal snooze duration based on user patterns."""
        if alarm_id not in self.user_data['snooze_patterns']:
            return 5  # Default 5 minutes
        
        snooze_history = self.user_data['snooze_patterns'][alarm_id]
        
        if not snooze_history:
            return 5
        
        # Calculate average snooze count
        avg_snooze_count = sum(record['snooze_count'] for record in snooze_history) / len(snooze_history)
        
        # Adaptive logic
        if avg_snooze_count <= 1:
            return 5  # User rarely snoozes, keep short
        elif avg_snooze_count <= 2:
            return 7  # Moderate snoozing
        elif avg_snooze_count <= 3:
            return 10  # Heavy snoozing, give longer intervals
        else:
            return 15  # Very heavy snoozing, longer intervals
    
    def get_sleep_quality_insights(self) -> Dict:
        """Analyze sleep patterns and provide insights."""
        insights = {
            'quality_score': 0.7,  # Default
            'recommendations': [],
            'patterns': {}
        }
        
        interactions = self.user_data.get('interactions', [])
        if not interactions:
            insights['recommendations'].append("Not enough data yet. Keep using alarms to get insights!")
            return insights
        
        # Analyze snooze patterns
        total_interactions = len(interactions)
        snooze_interactions = sum(1 for i in interactions if i['action'] == 'snooze')
        
        if snooze_interactions / total_interactions > 0.5:
            insights['recommendations'].append("🛌 You snooze frequently. Try going to bed 30 minutes earlier.")
            insights['quality_score'] -= 0.2
        
        # Analyze consistency
        alarm_times = [record['alarm_time'] for record in self.user_data['alarm_history']]
        if len(set(alarm_times)) <= 2:
            insights['recommendations'].append("✅ Great! You have consistent wake times.")
            insights['quality_score'] += 0.1
        else:
            insights['recommendations'].append("📅 Try maintaining more consistent wake times for better sleep.")
        
        # Weekend vs weekday analysis
        weekday_alarms = [r for r in self.user_data['alarm_history'] if r['day_of_week'] < 5]
        weekend_alarms = [r for r in self.user_data['alarm_history'] if r['day_of_week'] >= 5]
        
        if len(weekday_alarms) > 0 and len(weekend_alarms) > 0:
            weekday_avg_hour = sum(int(r['alarm_time'].split(':')[0]) for r in weekday_alarms) / len(weekday_alarms)
            weekend_avg_hour = sum(int(r['alarm_time'].split(':')[0]) for r in weekend_alarms) / len(weekend_alarms)
            
            time_diff = weekend_avg_hour - weekday_avg_hour
            if time_diff > 2:
                insights['recommendations'].append("⏰ Large difference between weekday/weekend wake times. Consider gradual adjustment.")
        
        return insights
    
    def get_personalized_alarm_suggestion(self, requested_time: str = None, 
                                        context: str = "") -> Dict:
        """Get a complete personalized alarm suggestion."""
        suggestion = {
            'recommended_time': requested_time or "07:00",
            'confidence': 0.5,
            'reason': "Default suggestion",
            'repeat_days': [],
            'label': "Alarm",
            'snooze_duration': 5,
            'alternative_times': []
        }
        
        # Get smart time suggestions
        time_suggestions = self.get_smart_time_suggestions(context)
        
        if time_suggestions:
            suggestion['recommended_time'] = time_suggestions[0][0]
            suggestion['label'] = time_suggestions[0][1]
            suggestion['confidence'] = time_suggestions[0][2]
            suggestion['reason'] = f"Based on your usage patterns (confidence: {suggestion['confidence']:.0%})"
            
            # Add alternative times
            suggestion['alternative_times'] = [
                {'time': t[0], 'label': t[1], 'confidence': t[2]} 
                for t in time_suggestions[1:3]
            ]
        
        # Smart repeat day suggestions
        if 'work' in context.lower() or 'office' in context.lower():
            suggestion['repeat_days'] = [0, 1, 2, 3, 4]  # Weekdays
        elif 'weekend' in context.lower():
            suggestion['repeat_days'] = [5, 6]  # Weekends
        elif 'daily' in context.lower() or 'every day' in context.lower():
            suggestion['repeat_days'] = list(range(7))
        
        return suggestion

class SleepPatternAnalyzer:
    """Analyzes sleep patterns for smart wake recommendations."""
    
    def __init__(self):
        self.sleep_data = []
    
    def analyze_optimal_wake_time(self, target_time: str, sleep_cycle_minutes: int = 90) -> str:
        """Calculate optimal wake time based on sleep cycles."""
        # Convert target time to minutes
        hour, minute = map(int, target_time.split(':'))
        target_minutes = hour * 60 + minute
        
        # Calculate sleep cycles (90 minutes each)
        # Wake up at the end of a complete cycle for better feeling
        cycle_start_times = []
        
        for cycles in range(4, 8):  # 6-12 hours of sleep
            sleep_duration = cycles * sleep_cycle_minutes
            optimal_wake = target_minutes
            optimal_sleep_time = optimal_wake - sleep_duration
            
            if optimal_sleep_time < 0:
                optimal_sleep_time += 24 * 60  # Next day
            
            sleep_hour = optimal_sleep_time // 60
            sleep_minute = optimal_sleep_time % 60
            
            cycle_start_times.append({
                'bedtime': f"{sleep_hour:02d}:{sleep_minute:02d}",
                'wake_time': target_time,
                'cycles': cycles,
                'quality_score': self._calculate_quality_score(cycles, sleep_hour)
            })
        
        # Return the best option
        best_option = max(cycle_start_times, key=lambda x: x['quality_score'])
        return best_option['bedtime']
    
    def _calculate_quality_score(self, cycles: int, sleep_hour: int) -> float:
        """Calculate sleep quality score based on cycles and bedtime."""
        score = 0.5
        
        # Optimal cycle count (7-8 hours)
        if 5 <= cycles <= 6:  # 7.5-9 hours
            score += 0.3
        elif cycles == 4 or cycles == 7:  # 6 or 10.5 hours
            score += 0.1
        
        # Optimal bedtime (10 PM - 12 AM)
        if 22 <= sleep_hour <= 24 or sleep_hour == 0:
            score += 0.2
        elif 21 <= sleep_hour <= 1:
            score += 0.1
        
        return min(score, 1.0)

# Global instance for easy access
smart_learner = SmartAlarmLearner()
sleep_analyzer = SleepPatternAnalyzer() 