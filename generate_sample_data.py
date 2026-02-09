"""
Sample Data Generator
Populates database with realistic sample data for testing
"""

import logging
from datetime import datetime, timedelta
from backend.data_service import get_data_service
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sample_data():
    """Generate sample data for user 1"""
    try:
        data_service = get_data_service()
        user_id = 1
        
        print("Generating sample activity data...")
        
        # Generate activity logs for the last 8 hours
        for hour in range(8, 0, -1):
            timestamp = datetime.now() - timedelta(hours=hour)
            activity_data = {
                'mouse_clicks': random.randint(20, 100),
                'keyboard_presses': random.randint(50, 200),
                'screen_time': random.randint(300, 600),
                'idle_time': random.randint(10, 60),
                'app_name': random.choice(['Visual Studio Code', 'Chrome', 'Word', 'Excel', 'Slack'])
            }
            data_service.log_activity(user_id, activity_data)
            print(f"  [OK] Activity logged for {hour} hours ago")
        
        print("\nGenerating sample fatigue data...")
        
        # Generate fatigue detection logs
        for i in range(8):
            fatigue_data = {
                'fatigue_score': random.uniform(0.3, 0.8),
                'eye_strain_level': random.randint(2, 7),
                'blink_rate': random.uniform(12, 20),
                'posture_score': round(random.uniform(0.4, 0.9), 2),
                'facial_expression': random.choice(['alert', 'neutral', 'tired']),
                'webcam_data_used': True,
                'alert_generated': random.choice([True, False])
            }
            data_service.log_fatigue(user_id, fatigue_data)
            print(f"  [OK] Fatigue entry {i+1} logged")
        
        print("\nGenerating sample break records...")
        
        # Generate break records
        for i in range(3):
            break_data = {
                'duration': random.choice([3, 5, 10]),
                'break_type': random.choice(['micro', 'regular', 'long']),
                'reason': random.choice(['Eye strain', 'Fatigue', 'Scheduled', 'High activity']),
                'compliance_status': random.choice(['Completed', 'Skipped'])
            }
            data_service.log_break(user_id, break_data)
            print(f"  [OK] Break record {i+1} logged")
        
        print("\nGenerating daily analytics...")
        
        # Generate daily analytics
        daily_metrics = {
            'date': datetime.now().date().isoformat(),
            'total_work_time': random.randint(300, 480),  # 5-8 hours
            'total_break_time': random.randint(15, 45),   # 15-45 minutes
            'productivity_score': random.randint(60, 90),
            'average_fatigue_level': round(random.uniform(0.4, 0.7), 2),
            'break_compliance_rate': round(random.uniform(0.6, 0.95), 2),
            'focus_score': random.randint(70, 95)
        }
        data_service.upsert_daily_analytics(user_id, daily_metrics)
        print("  [OK] Daily analytics computed and saved")
        
        print("\n" + "="*50)
        print("Sample data generation complete!")
        print("="*50)
        print("\nYou can now:")
        print("1. Open http://127.0.0.1:2050 in your browser")
        print("2. View real data in the dashboard")
        print("3. Check Analytics tab for metrics")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        print(f"[ERROR] {e}")
        return False


if __name__ == '__main__':
    generate_sample_data()
