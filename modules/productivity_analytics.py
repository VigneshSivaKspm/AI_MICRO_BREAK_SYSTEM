"""
Module 6: Productivity Analytics Module
Tracks and analyzes user productivity, compliance, and system effectiveness
"""

import logging
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from collections import defaultdict
import json
from config.config import ANALYTICS_CONFIG

logger = logging.getLogger(__name__)


class ProductivityAnalytics:
    """Tracks and analyzes productivity metrics"""
    
    def __init__(self):
        self.daily_metrics = defaultdict(dict)  # {user_id: {date: metrics}}
        self.weekly_metrics = defaultdict(list)
        self.monthly_metrics = defaultdict(list)
        self.break_effectiveness_data = defaultdict(list)
        self.retention_period = ANALYTICS_CONFIG['retention_period']
        
    def record_productivity_session(self, user_id: int, session_data: Dict) -> bool:
        """Record a productivity session"""
        try:
            today = date.today()
            
            if user_id not in self.daily_metrics:
                self.daily_metrics[user_id] = {}
            
            if today not in self.daily_metrics[user_id]:
                self.daily_metrics[user_id][today] = self._initialize_daily_metrics()
            
            metrics = self.daily_metrics[user_id][today]
            
            # Update metrics
            metrics['work_sessions'].append(session_data)
            metrics['total_work_time'] += session_data.get('duration', 0)
            metrics['last_activity'] = datetime.now().isoformat()
            metrics['session_count'] += 1
            
            return True
        except Exception as e:
            logger.error(f"Error recording productivity session: {e}")
            return False
    
    def record_break_session(self, user_id: int, break_data: Dict) -> bool:
        """Record a break session"""
        try:
            today = date.today()
            
            if user_id not in self.daily_metrics:
                self.daily_metrics[user_id] = {}
            
            if today not in self.daily_metrics[user_id]:
                self.daily_metrics[user_id][today] = self._initialize_daily_metrics()
            
            metrics = self.daily_metrics[user_id][today]
            
            # Update metrics
            metrics['break_sessions'].append(break_data)
            metrics['total_break_time'] += break_data.get('duration', 0)
            metrics['break_count'] += 1
            
            # Calculate break compliance
            if break_data.get('forced'):
                if break_data.get('complied'):
                    metrics['complied_forced_breaks'] += 1
                metrics['total_forced_breaks'] += 1
            
            return True
        except Exception as e:
            logger.error(f"Error recording break session: {e}")
            return False
    
    def record_fatigue_event(self, user_id: int, fatigue_data: Dict) -> bool:
        """Record a fatigue event"""
        try:
            today = date.today()
            
            if user_id not in self.daily_metrics:
                self.daily_metrics[user_id] = {}
            
            if today not in self.daily_metrics[user_id]:
                self.daily_metrics[user_id][today] = self._initialize_daily_metrics()
            
            metrics = self.daily_metrics[user_id][today]
            
            # Record fatigue event
            metrics['fatigue_events'].append(fatigue_data)
            metrics['total_fatigue_score'] += fatigue_data.get('fatigue_score', 0)
            metrics['fatigue_event_count'] += 1
            
            return True
        except Exception as e:
            logger.error(f"Error recording fatigue event: {e}")
            return False
    
    def calculate_daily_metrics(self, user_id: int, target_date: date = None) -> Dict:
        """Calculate daily productivity metrics"""
        if target_date is None:
            target_date = date.today()
        
        if user_id not in self.daily_metrics or target_date not in self.daily_metrics[user_id]:
            return {}
        
        metrics = self.daily_metrics[user_id][target_date]
        
        # Calculate derived metrics
        total_active_time = metrics['total_work_time'] + metrics['total_break_time']
        
        productivity_score = self._calculate_productivity_score(
            metrics['total_work_time'],
            metrics['total_break_time'],
            metrics['fatigue_event_count'],
            metrics['session_count']
        )
        
        compliance_rate = (
            metrics['complied_forced_breaks'] / metrics['total_forced_breaks']
            if metrics['total_forced_breaks'] > 0 else 0
        )
        
        avg_fatigue = (
            metrics['total_fatigue_score'] / metrics['fatigue_event_count']
            if metrics['fatigue_event_count'] > 0 else 0
        )
        
        focus_score = self._calculate_focus_score(
            metrics['session_count'],
            metrics['fatigue_event_count'],
            compliance_rate
        )
        
        return {
            'user_id': user_id,
            'date': target_date.isoformat(),
            'total_work_time': metrics['total_work_time'],
            'total_break_time': metrics['total_break_time'],
            'total_active_time': total_active_time,
            'productivity_score': productivity_score,
            'average_fatigue_level': avg_fatigue,
            'break_compliance_rate': compliance_rate,
            'focus_score': focus_score,
            'session_count': metrics['session_count'],
            'break_count': metrics['break_count'],
            'fatigue_event_count': metrics['fatigue_event_count']
        }
    
    def calculate_weekly_metrics(self, user_id: int) -> Dict:
        """Calculate weekly productivity metrics"""
        week_metrics = []
        
        for i in range(7):
            past_date = date.today() - timedelta(days=i)
            daily = self.calculate_daily_metrics(user_id, past_date)
            if daily:
                week_metrics.append(daily)
        
        if not week_metrics:
            return {}
        
        # Average metrics
        avg_productivity = np.mean([m['productivity_score'] for m in week_metrics])
        avg_fatigue = np.mean([m['average_fatigue_level'] for m in week_metrics])
        avg_compliance = np.mean([m['break_compliance_rate'] for m in week_metrics])
        total_work_time = sum([m['total_work_time'] for m in week_metrics])
        total_break_time = sum([m['total_break_time'] for m in week_metrics])
        
        return {
            'user_id': user_id,
            'period': f"{(date.today() - timedelta(days=6)).isoformat()} to {date.today().isoformat()}",
            'average_productivity_score': avg_productivity,
            'average_fatigue_level': avg_fatigue,
            'average_compliance_rate': avg_compliance,
            'total_work_time': total_work_time,
            'total_break_time': total_break_time,
            'daily_breakdown': week_metrics
        }
    
    def calculate_monthly_metrics(self, user_id: int) -> Dict:
        """Calculate monthly productivity metrics"""
        month_metrics = []
        
        for i in range(30):
            past_date = date.today() - timedelta(days=i)
            daily = self.calculate_daily_metrics(user_id, past_date)
            if daily:
                month_metrics.append(daily)
        
        if not month_metrics:
            return {}
        
        # Average metrics
        avg_productivity = np.mean([m['productivity_score'] for m in month_metrics])
        avg_fatigue = np.mean([m['average_fatigue_level'] for m in month_metrics])
        avg_compliance = np.mean([m['break_compliance_rate'] for m in month_metrics])
        
        return {
            'user_id': user_id,
            'period': f"Last 30 days (ending {date.today().isoformat()})",
            'average_productivity_score': avg_productivity,
            'average_fatigue_level': avg_fatigue,
            'average_compliance_rate': avg_compliance,
            'total_metrics_days': len(month_metrics)
        }
    
    def _calculate_productivity_score(self, work_time: int, break_time: int, 
                                     fatigue_events: int, sessions: int) -> float:
        """Calculate productivity score (0-100)"""
        if work_time == 0:
            return 0.0
        
        # Normalize work time (assume 8 hours = 100%)
        work_score = min(1.0, work_time / (8 * 60))  # 8 hours in minutes
        
        # Penalize for fatigue events
        fatigue_penalty = min(0.3, fatigue_events * 0.05)
        
        # Reward for consistent sessions
        session_bonus = min(0.2, (sessions - 1) * 0.02)
        
        productivity = (work_score * 0.7 - fatigue_penalty + session_bonus) * 100
        return max(0, min(100, productivity))
    
    def _calculate_focus_score(self, sessions: int, fatigue_events: int, 
                              compliance_rate: float) -> float:
        """Calculate focus score (0-100)"""
        # More sessions = better focus
        session_score = min(1.0, sessions / 10)
        
        # Fewer fatigue events = better focus
        fatigue_score = max(0, 1.0 - (fatigue_events / 10))
        
        # Good compliance = better overall focus
        compliance_score = compliance_rate
        
        focus = (session_score * 0.4 + fatigue_score * 0.3 + compliance_score * 0.3) * 100
        return max(0, min(100, focus))
    
    def get_user_analytics_report(self, user_id: int, period: str = 'week') -> Dict:
        """Get analytics report for user"""
        if period == 'daily':
            return self.calculate_daily_metrics(user_id)
        elif period == 'weekly':
            return self.calculate_weekly_metrics(user_id)
        elif period == 'monthly':
            return self.calculate_monthly_metrics(user_id)
        else:
            return {}
    
    def get_break_effectiveness(self, user_id: int) -> Dict:
        """Analyze break effectiveness"""
        if user_id not in self.break_effectiveness_data:
            return {}
        
        data = self.break_effectiveness_data[user_id]
        if not data:
            return {}
        
        # Before and after fatigue levels
        before_fatigue = [d['before_fatigue'] for d in data]
        after_fatigue = [d['after_fatigue'] for d in data]
        
        avg_reduction = np.mean([b - a for b, a in zip(before_fatigue, after_fatigue)])
        
        return {
            'total_breaks_analyzed': len(data),
            'average_fatigue_reduction': avg_reduction,
            'most_effective_break_type': self._find_most_effective_break_type(data),
            'break_effectiveness_score': (avg_reduction / max(before_fatigue)) * 100 if before_fatigue else 0
        }
    
    def _find_most_effective_break_type(self, data: List[Dict]) -> str:
        """Find most effective break type"""
        effectiveness = defaultdict(list)
        
        for item in data:
            break_type = item.get('break_type', 'unknown')
            reduction = item['before_fatigue'] - item['after_fatigue']
            effectiveness[break_type].append(reduction)
        
        if not effectiveness:
            return 'unknown'
        
        avg_effectiveness = {k: np.mean(v) for k, v in effectiveness.items()}
        return max(avg_effectiveness, key=avg_effectiveness.get)
    
    def record_break_effectiveness(self, user_id: int, break_data: Dict):
        """Record break effectiveness data"""
        self.break_effectiveness_data[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'break_type': break_data.get('break_type'),
            'before_fatigue': break_data.get('fatigue_before', 0),
            'after_fatigue': break_data.get('fatigue_after', 0),
            'duration': break_data.get('duration', 0)
        })
        
        # Keep only recent data
        cutoff_time = datetime.now() - timedelta(days=self.retention_period)
        self.break_effectiveness_data[user_id] = [
            d for d in self.break_effectiveness_data[user_id]
            if datetime.fromisoformat(d['timestamp']) > cutoff_time
        ]
    
    def _initialize_daily_metrics(self) -> Dict:
        """Initialize daily metrics dictionary"""
        return {
            'work_sessions': [],
            'break_sessions': [],
            'fatigue_events': [],
            'total_work_time': 0,
            'total_break_time': 0,
            'session_count': 0,
            'break_count': 0,
            'fatigue_event_count': 0,
            'total_fatigue_score': 0,
            'complied_forced_breaks': 0,
            'total_forced_breaks': 0,
            'last_activity': None
        }
    
    def export_analytics(self, user_id: int, export_format: str = 'json') -> str:
        """Export analytics data"""
        data = {
            'user_id': user_id,
            'daily': self.calculate_daily_metrics(user_id),
            'weekly': self.calculate_weekly_metrics(user_id),
            'monthly': self.calculate_monthly_metrics(user_id),
            'break_effectiveness': self.get_break_effectiveness(user_id)
        }
        
        if export_format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif export_format == 'csv':
            return self._convert_to_csv(data)
        else:
            return json.dumps(data, indent=2, default=str)
    
    def _convert_to_csv(self, data: Dict) -> str:
        """Convert analytics data to CSV"""
        # Simple CSV conversion
        csv_lines = ['metric,value']
        
        daily = data.get('daily', {})
        for key, value in daily.items():
            if key != 'user_id':
                csv_lines.append(f"{key},{value}")
        
        return '\n'.join(csv_lines)


# Global instance
productivity_analytics = None


def get_productivity_analytics() -> ProductivityAnalytics:
    """Get or create productivity analytics instance"""
    global productivity_analytics
    if productivity_analytics is None:
        productivity_analytics = ProductivityAnalytics()
    return productivity_analytics
