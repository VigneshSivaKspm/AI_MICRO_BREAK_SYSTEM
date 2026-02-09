"""
Module 5: Personalization and Learning Module
Learns user patterns and adapts the system to individual preferences
"""

import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import pickle
import os
from config.config import PERSONALIZATION_CONFIG, ML_CONFIG

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """Learns and adapts to user patterns"""
    
    def __init__(self):
        self.user_profiles = {}
        self.learning_window = PERSONALIZATION_CONFIG['learning_window']
        self.min_data_points = PERSONALIZATION_CONFIG['min_data_points']
        self.update_frequency = PERSONALIZATION_CONFIG['update_frequency']
        self.preferred_break_types = PERSONALIZATION_CONFIG['preferred_break_types']
        self.activity_patterns = defaultdict(list)
        self.fatigue_patterns = defaultdict(list)
        self.break_compliance_data = defaultdict(list)
        
    def create_user_profile(self, user_id: int, initial_preferences: Dict = None) -> Dict:
        """Create a new user profile"""
        profile = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'preferred_break_types': initial_preferences.get('preferred_break_types', 
                                                            self.preferred_break_types) if initial_preferences else self.preferred_break_types,
            'optimal_break_time': initial_preferences.get('optimal_break_time', '10:00-18:00') if initial_preferences else '10:00-18:00',
            'fatigue_threshold': initial_preferences.get('fatigue_threshold', 0.7) if initial_preferences else 0.7,
            'peak_productivity_hours': [],
            'break_preferences': initial_preferences.get('break_preferences', {}) if initial_preferences else {},
            'activity_pattern': {},
            'break_compliance_rate': 0.0,
            'average_fatigue_level': 0.0,
            'learning_phase': True,
            'data_points_collected': 0,
            'last_updated': datetime.now().isoformat(),
            'personalization_level': 'beginner'  # beginner, intermediate, expert
        }
        
        self.user_profiles[user_id] = profile
        logger.info(f"User profile created for user {user_id}")
        return profile
    
    def record_activity_pattern(self, user_id: int, activity_data: Dict):
        """Record user activity pattern"""
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
        
        self.activity_patterns[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'data': activity_data
        })
        
        # Keep only recent data
        retention_days = self.learning_window
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        self.activity_patterns[user_id] = [
            p for p in self.activity_patterns[user_id]
            if datetime.fromisoformat(p['timestamp']) > cutoff_time
        ]
    
    def record_fatigue_pattern(self, user_id: int, fatigue_data: Dict):
        """Record user fatigue pattern"""
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
        
        self.fatigue_patterns[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'data': fatigue_data
        })
        
        # Keep only recent data
        retention_days = self.learning_window
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        self.fatigue_patterns[user_id] = [
            p for p in self.fatigue_patterns[user_id]
            if datetime.fromisoformat(p['timestamp']) > cutoff_time
        ]
    
    def record_break_compliance(self, user_id: int, break_data: Dict):
        """Record break compliance data"""
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
        
        self.break_compliance_data[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'data': break_data
        })
        
        # Update compliance rate
        self._update_compliance_rate(user_id)
    
    def _update_compliance_rate(self, user_id: int):
        """Update break compliance rate"""
        if user_id not in self.break_compliance_data:
            return
        
        compliance_data = self.break_compliance_data[user_id]
        if not compliance_data:
            return
        
        # Count complied breaks
        complied = sum(1 for d in compliance_data if d['data'].get('complied', False))
        compliance_rate = complied / len(compliance_data) if compliance_data else 0
        
        self.user_profiles[user_id]['break_compliance_rate'] = compliance_rate
    
    def analyze_patterns(self, user_id: int) -> Dict:
        """Analyze collected patterns for a user"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        
        # Check if enough data collected
        if len(self.activity_patterns[user_id]) < self.min_data_points:
            logger.info(f"Not enough data for user {user_id}. Skipping analysis.")
            return {}
        
        analysis = {
            'user_id': user_id,
            'analysis_time': datetime.now().isoformat(),
            'activity_analysis': self._analyze_activity(user_id),
            'fatigue_analysis': self._analyze_fatigue(user_id),
            'break_patterns': self._analyze_break_patterns(user_id),
            'recommendations': []
        }
        
        # Generate personalization recommendations
        analysis['recommendations'] = self._generate_recommendations(user_id, analysis)
        
        return analysis
    
    def _analyze_activity(self, user_id: int) -> Dict:
        """Analyze activity patterns"""
        if user_id not in self.activity_patterns:
            return {}
        
        patterns = self.activity_patterns[user_id]
        if not patterns:
            return {}
        
        # Extract activity levels by hour
        hourly_activity = defaultdict(list)
        for pattern in patterns:
            timestamp = datetime.fromisoformat(pattern['timestamp'])
            hour = timestamp.hour
            activity_level = pattern['data'].get('activity_level', 0)
            hourly_activity[hour].append(activity_level)
        
        # Calculate average activity by hour
        avg_hourly_activity = {
            hour: np.mean(activities) 
            for hour, activities in hourly_activity.items()
        }
        
        # Find peak activity hours
        if avg_hourly_activity:
            peak_hours = sorted(avg_hourly_activity.items(), 
                              key=lambda x: x[1], reverse=True)[:3]
        else:
            peak_hours = []
        
        return {
            'hourly_averages': dict(avg_hourly_activity),
            'peak_hours': [h[0] for h in peak_hours],
            'average_activity_level': np.mean([p['data'].get('activity_level', 0) 
                                              for p in patterns]) if patterns else 0
        }
    
    def _analyze_fatigue(self, user_id: int) -> Dict:
        """Analyze fatigue patterns"""
        if user_id not in self.fatigue_patterns:
            return {}
        
        patterns = self.fatigue_patterns[user_id]
        if not patterns:
            return {}
        
        fatigue_scores = [p['data'].get('fatigue_score', 0) for p in patterns]
        
        return {
            'average_fatigue': np.mean(fatigue_scores),
            'max_fatigue': np.max(fatigue_scores),
            'min_fatigue': np.min(fatigue_scores),
            'fatigue_std': np.std(fatigue_scores),
            'high_fatigue_periods': self._find_high_fatigue_periods(user_id)
        }
    
    def _find_high_fatigue_periods(self, user_id: int) -> List[Dict]:
        """Find periods of high fatigue"""
        if user_id not in self.fatigue_patterns:
            return []
        
        patterns = self.fatigue_patterns[user_id]
        high_fatigue = [p for p in patterns 
                       if p['data'].get('fatigue_score', 0) > 0.7]
        
        # Extract time periods
        periods = []
        for pattern in high_fatigue:
            timestamp = datetime.fromisoformat(pattern['timestamp'])
            hour = timestamp.hour
            if not periods or periods[-1]['hour'] != hour:
                periods.append({'hour': hour, 'count': 1})
            else:
                periods[-1]['count'] += 1
        
        return periods
    
    def _analyze_break_patterns(self, user_id: int) -> Dict:
        """Analyze break patterns"""
        if user_id not in self.break_compliance_data:
            return {}
        
        compliance_data = self.break_compliance_data[user_id]
        if not compliance_data:
            return {}
        
        break_types = defaultdict(int)
        for data in compliance_data:
            break_type = data['data'].get('break_type', 'unknown')
            break_types[break_type] += 1
        
        return {
            'break_type_frequency': dict(break_types),
            'total_breaks': len(compliance_data),
            'compliance_rate': self.user_profiles[user_id]['break_compliance_rate']
        }
    
    def _generate_recommendations(self, user_id: int, analysis: Dict) -> List[Dict]:
        """Generate personalization recommendations"""
        recommendations = []
        
        profile = self.user_profiles[user_id]
        
        # Analyze fatigue analysis
        fatigue_analysis = analysis.get('fatigue_analysis', {})
        if fatigue_analysis.get('average_fatigue', 0) > 0.7:
            recommendations.append({
                'type': 'fatigue_threshold_reduction',
                'message': 'Consider lowering fatigue threshold for earlier interventions',
                'current': profile['fatigue_threshold'],
                'suggested': profile['fatigue_threshold'] - 0.1
            })
        
        # Analyze activity patterns
        activity_analysis = analysis.get('activity_analysis', {})
        if activity_analysis.get('peak_hours'):
            recommendations.append({
                'type': 'optimal_break_time',
                'message': f"Peak activity detected during hours: {activity_analysis['peak_hours']}",
                'peak_hours': activity_analysis['peak_hours']
            })
        
        # Update personalization level
        if len(self.activity_patterns[user_id]) > self.min_data_points * 2:
            profile['personalization_level'] = 'expert'
        elif len(self.activity_patterns[user_id]) > self.min_data_points:
            profile['personalization_level'] = 'intermediate'
        
        return recommendations
    
    def apply_personalization(self, user_id: int, analysis: Dict) -> bool:
        """Apply personalization changes to user profile"""
        if user_id not in self.user_profiles:
            return False
        
        profile = self.user_profiles[user_id]
        
        # Update peak productivity hours
        activity_analysis = analysis.get('activity_analysis', {})
        if activity_analysis.get('peak_hours'):
            profile['peak_productivity_hours'] = activity_analysis['peak_hours']
        
        # Update fatigue threshold if recommended
        recommendations = analysis.get('recommendations', [])
        for rec in recommendations:
            if rec.get('type') == 'fatigue_threshold_reduction':
                profile['fatigue_threshold'] = rec['suggested']
        
        profile['last_updated'] = datetime.now().isoformat()
        logger.info(f"Personalization applied for user {user_id}")
        
        return True
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile"""
        return self.user_profiles.get(user_id)
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences"""
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        profile.update(preferences)
        profile['last_updated'] = datetime.now().isoformat()
        
        logger.info(f"User preferences updated for user {user_id}")
        return True
    
    def save_profile(self, user_id: int, filepath: str) -> bool:
        """Save user profile to file"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return False
            
            with open(filepath, 'wb') as f:
                pickle.dump(profile, f)
            
            logger.info(f"Profile saved for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            return False
    
    def load_profile(self, user_id: int, filepath: str) -> bool:
        """Load user profile from file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    profile = pickle.load(f)
                    self.user_profiles[user_id] = profile
                
                logger.info(f"Profile loaded for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            return False


# Global instance
personalization_engine = None


def get_personalization_engine() -> PersonalizationEngine:
    """Get or create personalization engine instance"""
    global personalization_engine
    if personalization_engine is None:
        personalization_engine = PersonalizationEngine()
    return personalization_engine
