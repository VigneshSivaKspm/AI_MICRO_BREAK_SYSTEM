"""
Data Service Layer
Bridges modules with database for persistent storage and retrieval
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional
from backend.database_manager import get_database_manager
import json

logger = logging.getLogger(__name__)


class DataService:
    """Service layer for data persistence and retrieval"""
    
    def __init__(self):
        self.db = get_database_manager()
    
    # ==================== ACTIVITY LOGGING ====================
    
    def log_activity(self, user_id: int, activity_data: Dict) -> bool:
        """Log activity to database"""
        return self.db.log_activity(user_id, activity_data)
    
    def get_latest_activity(self, user_id: int) -> Optional[Dict]:
        """Get latest activity log entry"""
        query = """
            SELECT * FROM ActivityLog 
            WHERE UserID = %s 
            ORDER BY Timestamp DESC 
            LIMIT 1
        """
        return self.db.fetch_one(query, [user_id])
    
    def get_activity_summary(self, user_id: int, hours: int = 1) -> Dict:
        """Get activity summary for last N hours"""
        query = """
            SELECT 
                COUNT(*) as total_entries,
                SUM(MouseActivity) as total_clicks,
                SUM(KeyboardActivity) as total_presses,
                SUM(IdlePeriod) as total_idle,
                AVG(ScreenInteractionTime) as avg_screen_time
            FROM ActivityLog
            WHERE UserID = %s AND Timestamp >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        """
        result = self.db.fetch_one(query, [user_id, hours])
        
        if result:
            return {
                'total_logs': result.get('total_entries', 0) or 0,
                'total_mouse_clicks': result.get('total_clicks', 0) or 0,
                'total_keyboard_presses': result.get('total_presses', 0) or 0,
                'total_idle_time': result.get('total_idle', 0) or 0,
                'avg_screen_time': result.get('avg_screen_time', 0) or 0
            }
        
        return {
            'total_logs': 0,
            'total_mouse_clicks': 0,
            'total_keyboard_presses': 0,
            'total_idle_time': 0,
            'avg_screen_time': 0
        }
    
    # ==================== FATIGUE LOGGING ====================
    
    def log_fatigue(self, user_id: int, fatigue_data: Dict) -> bool:
        """Log fatigue detection to database"""
        return self.db.log_fatigue(user_id, fatigue_data)
    
    def get_latest_fatigue(self, user_id: int) -> Optional[Dict]:
        """Get latest fatigue detection"""
        query = """
            SELECT * FROM FatigueDetection 
            WHERE UserID = %s 
            ORDER BY Timestamp DESC 
            LIMIT 1
        """
        return self.db.fetch_one(query, [user_id])
    
    def get_fatigue_trend(self, user_id: int, last_n: int = 10) -> List[Dict]:
        """Get fatigue trend for last N entries"""
        query = """
            SELECT FatigueScore, EyeStrainLevel, PostureScore, Timestamp 
            FROM FatigueDetection
            WHERE UserID = %s 
            ORDER BY Timestamp DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, [user_id, last_n])
        return list(reversed(results)) if results else []
    
    def get_average_fatigue(self, user_id: int, hours: int = 1) -> float:
        """Get average fatigue for last N hours"""
        query = """
            SELECT AVG(FatigueScore) as avg_fatigue 
            FROM FatigueDetection
            WHERE UserID = %s AND Timestamp >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        """
        result = self.db.fetch_one(query, [user_id, hours])
        return float(result.get('avg_fatigue', 0) or 0) if result else 0.0
    
    # ==================== BREAK LOGGING ====================
    
    def log_break(self, user_id: int, break_data: Dict) -> bool:
        """Log break to database"""
        return self.db.log_break(user_id, break_data)
    
    def get_breaks_today(self, user_id: int) -> List[Dict]:
        """Get all breaks taken today"""
        query = """
            SELECT * FROM BreakRecords 
            WHERE UserID = %s AND DATE(BreakStartTime) = CURDATE()
            ORDER BY BreakStartTime DESC
        """
        return self.db.fetch_all(query, [user_id])
    
    def get_break_compliance_rate(self, user_id: int, days: int = 7) -> float:
        """Get break compliance rate for last N days"""
        query = """
            SELECT 
                SUM(CASE WHEN ComplianceStatus = 'Completed' THEN 1 ELSE 0 END) as completed,
                COUNT(*) as total
            FROM BreakRecords
            WHERE UserID = %s AND BreakStartTime >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        result = self.db.fetch_one(query, [user_id, days])
        
        if result and result.get('total', 0) > 0:
            return (result.get('completed', 0) or 0) / result.get('total', 1)
        return 0.0
    
    # ==================== ANALYTICS ====================
    
    def get_daily_metrics(self, user_id: int, target_date: Optional[str] = None) -> Dict:
        """Get daily metrics from database"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        query = """
            SELECT * FROM ProductivityAnalytics
            WHERE UserID = %s AND Date = %s
        """
        result = self.db.fetch_one(query, [user_id, target_date])
        
        if result:
            return dict(result)
        
        # Return empty metrics if none exist
        return {
            'user_id': user_id,
            'date': target_date,
            'total_work_time': 0,
            'total_break_time': 0,
            'productivity_score': 0,
            'average_fatigue_level': 0,
            'break_compliance_rate': 0,
            'focus_score': 0
        }
    
    def get_weekly_metrics(self, user_id: int) -> Dict:
        """Get weekly metrics from database"""
        query = """
            SELECT 
                SUM(TotalWorkTime) as total_work_time,
                SUM(TotalBreakTime) as total_break_time,
                AVG(ProductivityScore) as avg_productivity,
                AVG(AverageFatigueLevel) as avg_fatigue,
                AVG(BreakCompliance) as avg_compliance,
                AVG(FocusScore) as avg_focus
            FROM ProductivityAnalytics
            WHERE UserID = %s AND Date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """
        result = self.db.fetch_one(query, [user_id])
        
        if result:
            return {
                'total_work_time': result.get('total_work_time', 0) or 0,
                'total_break_time': result.get('total_break_time', 0) or 0,
                'avg_productivity_score': result.get('avg_productivity', 0) or 0,
                'avg_fatigue_level': result.get('avg_fatigue', 0) or 0,
                'avg_compliance': result.get('avg_compliance', 0) or 0,
                'avg_focus_score': result.get('avg_focus', 0) or 0
            }
        
        return {
            'total_work_time': 0,
            'total_break_time': 0,
            'avg_productivity_score': 0,
            'avg_fatigue_level': 0,
            'avg_compliance': 0,
            'avg_focus_score': 0
        }
    
    def upsert_daily_analytics(self, user_id: int, metrics: Dict) -> bool:
        """Insert or update daily analytics"""
        try:
            target_date = metrics.get('date', date.today().isoformat())
            
            # Check if exists
            query_check = """
                SELECT AnalyticsID FROM ProductivityAnalytics
                WHERE UserID = %s AND Date = %s
            """
            existing = self.db.fetch_one(query_check, [user_id, target_date])
            
            if existing:
                # Update
                query = """
                    UPDATE ProductivityAnalytics SET
                    TotalWorkTime = %s,
                    TotalBreakTime = %s,
                    ProductivityScore = %s,
                    AverageFatigueLevel = %s,
                    BreakCompliance = %s,
                    FocusScore = %s
                    WHERE UserID = %s AND Date = %s
                """
                params = [
                    metrics.get('total_work_time', 0),
                    metrics.get('total_break_time', 0),
                    metrics.get('productivity_score', 0),
                    metrics.get('average_fatigue_level', 0),
                    metrics.get('break_compliance_rate', 0),
                    metrics.get('focus_score', 0),
                    user_id,
                    target_date
                ]
            else:
                # Insert
                query = """
                    INSERT INTO ProductivityAnalytics
                    (UserID, Date, TotalWorkTime, TotalBreakTime, ProductivityScore, AverageFatigueLevel, BreakCompliance, FocusScore)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = [
                    user_id,
                    target_date,
                    metrics.get('total_work_time', 0),
                    metrics.get('total_break_time', 0),
                    metrics.get('productivity_score', 0),
                    metrics.get('average_fatigue_level', 0),
                    metrics.get('break_compliance_rate', 0),
                    metrics.get('focus_score', 0)
                ]
            
            return self.db.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error upserting daily analytics: {e}")
            return False
    
    # ==================== RECOMMENDATIONS ====================
    
    def log_recommendation(self, user_id: int, recommendation_data: Dict) -> bool:
        """Log recommendation"""
        try:
            query = """
                INSERT INTO Recommendations
                (UserID, RecommendationType, Activity, Duration, Priority)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = [
                user_id,
                recommendation_data.get('recommendation_type', 'Break'),
                recommendation_data.get('activity', ''),
                recommendation_data.get('duration', 5),
                recommendation_data.get('priority', 1)
            ]
            return self.db.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error logging recommendation: {e}")
            return False
    
    def get_latest_recommendations(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get latest recommendations"""
        query = """
            SELECT * FROM Recommendations
            WHERE UserID = %s
            ORDER BY Timestamp DESC
            LIMIT %s
        """
        return self.db.fetch_all(query, [user_id, limit])
    
    # ==================== PERSONALIZATION ====================
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        """Get user preferences"""
        query = """
            SELECT * FROM PersonalizationProfile
            WHERE UserID = %s
        """
        return self.db.fetch_one(query, [user_id])
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            query = """
                UPDATE PersonalizationProfile SET
                PreferredActivities = %s,
                OptimalBreakTime = %s,
                FatigueThreshold = %s,
                BreakPreferences = %s
                WHERE UserID = %s
            """
            params = [
                json.dumps(preferences.get('preferred_activities', [])),
                preferences.get('optimal_break_time', '09:00:00'),
                preferences.get('fatigue_threshold', 0.7),
                json.dumps(preferences.get('break_preferences', {})),
                user_id
            ]
            return self.db.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False


# Global instance
data_service = None


def get_data_service() -> DataService:
    """Get or create data service instance"""
    global data_service
    if data_service is None:
        data_service = DataService()
    return data_service
