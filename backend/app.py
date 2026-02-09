"""
Flask backend API for AI Micro Break System
"""

import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import APP_CONFIG, LOGGING_CONFIG
from backend.database_manager import get_database_manager
from backend.data_service import get_data_service
from modules.activity_monitor import get_activity_monitor
from modules.fatigue_detection import get_fatigue_detector
from modules.break_enforcement import get_break_enforcer
from modules.break_recommendation import get_break_recommender
from modules.personalization import get_personalization_engine
from modules.productivity_analytics import get_productivity_analytics

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['log_level']),
    format=LOGGING_CONFIG['log_format'],
    handlers=[
        logging.FileHandler(os.path.join(LOGGING_CONFIG['log_dir'], LOGGING_CONFIG['log_file'])),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = APP_CONFIG['secret_key']
CORS(app)

# Initialize managers
db_manager = get_database_manager()
data_service = get_data_service()
activity_monitor = get_activity_monitor()
fatigue_detector = get_fatigue_detector()
break_enforcer = get_break_enforcer()
break_recommender = get_break_recommender()
personalization_engine = get_personalization_engine()
productivity_analytics = get_productivity_analytics()

# ==================== HEALTH CHECK ====================

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check database health
        db_healthy = db_manager.health_check()
        
        # Check component status
        components_status = {
            'database': db_healthy,
            'activity_monitor': activity_monitor is not None,
            'fatigue_detector': fatigue_detector is not None,
            'data_service': data_service is not None,
            'monitoring_active': activity_monitor.is_monitoring if activity_monitor else False,
            'detection_active': fatigue_detector.is_running if fatigue_detector else False
        }
        
        # Overall health
        overall_healthy = all([
            components_status['database'],
            components_status['activity_monitor'],
            components_status['fatigue_detector'],
            components_status['data_service']
        ])
        
        return jsonify({
            'status': 'healthy' if overall_healthy else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'version': APP_CONFIG['version'],
            'components': components_status
        }), 200
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# ==================== USER MANAGEMENT ====================

@app.route('/api/v1/users/register', methods=['POST'])
def register_user():
    """Register new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Hash password (in production, use proper hashing)
        password_hash = password  # TODO: Use bcrypt
        
        if db_manager.create_user(username, email, password_hash):
            # Create user profile
            personalization_engine.create_user_profile(1, {
                'preferred_break_types': data.get('preferred_break_types', ['eye_exercise', 'stretching'])
            })
            
            return jsonify({
                'message': 'User registered successfully',
                'username': username
            }), 201
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== MONITORING STATUS ====================

@app.route('/api/v1/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """Get current monitoring status"""
    try:
        # Get pool stats
        pool_stats = db_manager.get_pool_stats()
        
        return jsonify({
            'activity_monitoring': activity_monitor.is_monitoring,
            'fatigue_detection': fatigue_detector.is_running,
            'database_healthy': db_manager.health_check(),
            'database_pool': pool_stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ACTIVITY MONITORING ====================

@app.route('/api/v1/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start activity monitoring with duplicate call prevention"""
    try:
        # Get user_id from JSON body or default to 1
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        
        # Check if monitoring is already running
        if activity_monitor.is_monitoring:
            logger.warning("Monitoring already started")
            return jsonify({
                'message': 'Monitoring already started',
                'timestamp': datetime.now().isoformat(),
                'status': 'already_running'
            }), 200
        
        # Start monitoring components
        activity_started = activity_monitor.start_monitoring()
        fatigue_started = fatigue_detector.start_detection()
        
        if not activity_started or not fatigue_started:
            # Cleanup if either failed
            try:
                activity_monitor.stop_monitoring()
                fatigue_detector.stop_detection()
            except Exception as cleanup_error:
                logger.error(f"Error during startup cleanup: {cleanup_error}")
            
            return jsonify({
                'error': 'Failed to start monitoring components',
                'activity_started': activity_started,
                'fatigue_started': fatigue_started
            }), 500
        
        # Log initial state (with error handling)
        try:
            activity_summary = activity_monitor.get_activity_summary()
            data_service.log_activity(user_id, activity_summary)
        except Exception as log_error:
            logger.warning(f"Failed to log initial activity: {log_error}")
        
        return jsonify({
            'message': 'Monitoring started successfully',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop activity monitoring with proper cleanup"""
    try:
        # Get user_id from JSON body or default to 1
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        
        # Check if monitoring is running
        if not activity_monitor.is_monitoring:
            logger.warning("Monitoring not running")
            return jsonify({
                'message': 'Monitoring not running',
                'timestamp': datetime.now().isoformat(),
                'status': 'already_stopped'
            }), 200
        
        # Log final state before stopping (with error handling)
        try:
            activity_summary = activity_monitor.get_activity_summary()
            data_service.log_activity(user_id, activity_summary)
        except Exception as log_error:
            logger.warning(f"Failed to log final activity: {log_error}")
        
        # Stop monitoring components
        activity_monitor.stop_monitoring()
        fatigue_detector.stop_detection()
        
        return jsonify({
            'message': 'Monitoring stopped successfully',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/activity/current', methods=['GET'])
def get_current_activity():
    """Get real-time activity status from activity monitor"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # Get REAL-TIME data from activity monitor (not database)
        if activity_monitor and activity_monitor.is_monitoring:
            activity_data = activity_monitor.get_activity_summary()
            
            return jsonify({
                'total_mouse_clicks': activity_data.get('mouse_clicks', 0),
                'total_keyboard_presses': activity_data.get('keyboard_presses', 0),
                'total_idle_time': activity_data.get('idle_time', 0),
                'activity_level': activity_data.get('activity_level', 0),
                'last_activity_time': activity_data.get('last_activity', ''),
                'is_idle': activity_data.get('is_idle', False),
                'monitoring_status': 'active'
            }), 200
        else:
            # If not monitoring, try to get from database
            try:
                activity_summary = data_service.get_activity_summary(user_id, hours=1)
                return jsonify({
                    'total_mouse_clicks': activity_summary.get('total_mouse_clicks', 0),
                    'total_keyboard_presses': activity_summary.get('total_keyboard_presses', 0),
                    'total_idle_time': activity_summary.get('total_idle_time', 0),
                    'activity_level': 0.5,
                    'monitoring_status': 'idle'
                }), 200
            except Exception as db_error:
                logger.warning(f"Database error in get_current_activity: {db_error}")
                return jsonify({
                    'total_mouse_clicks': 0,
                    'total_keyboard_presses': 0,
                    'total_idle_time': 0,
                    'activity_level': 0,
                    'monitoring_status': 'error'
                }), 200
        
    except Exception as e:
        logger.error(f"Error getting activity: {e}")
        # Return minimal response instead of error
        return jsonify({
            'total_logs': 0, 'total_mouse_clicks': 0, 'total_keyboard_presses': 0,
            'total_idle_time': 0, 'avg_screen_time': 0, 'error': 'Failed to retrieve activity data'
        }), 200

# ==================== FATIGUE DETECTION ====================

@app.route('/api/v1/fatigue/status', methods=['GET'])
def get_fatigue_status():
    """Get real-time fatigue status from detector (priority) then database"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # PRIORITY 1: Get REAL-TIME data from detector if monitoring
        if fatigue_detector and fatigue_detector.is_running:
            try:
                status = fatigue_detector.get_fatigue_status()
                return jsonify(status), 200
            except Exception as detector_error:
                logger.debug(f"Error getting fatigue from detector: {detector_error}")
        
        # PRIORITY 2: Get from database if detector not running
        try:
            latest_fatigue = data_service.get_latest_fatigue(user_id)
            if latest_fatigue:
                return jsonify({
                    'fatigue_score': latest_fatigue.get('FatigueScore', 0),
                    'eye_strain_level': latest_fatigue.get('EyeStrainLevel', 0),
                    'posture_score': latest_fatigue.get('PostureScore', 0),
                    'blink_rate': latest_fatigue.get('BlinkRate', 0),
                    'facial_expression': latest_fatigue.get('FacialExpression', 'neutral'),
                    'alert_generated': latest_fatigue.get('AlertGenerated', False),
                    'timestamp': latest_fatigue.get('Timestamp', '').isoformat() if latest_fatigue.get('Timestamp') else None
                }), 200
        except Exception as db_error:
            logger.debug(f"Database error in get_fatigue_status: {db_error}")
        
        # Default response when nothing available
        return jsonify({
            'fatigue_score': 0.0,
            'eye_strain_level': 0,
            'posture_score': 1.0,
            'blink_rate': 18.0,
            'facial_expression': 'neutral',
            'alert_generated': False,
            'timestamp': datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"Error getting fatigue status: {e}")
        return jsonify({
            'fatigue_score': 0.0, 'eye_strain_level': 0, 'posture_score': 1.0,
            'blink_rate': 18.0, 'facial_expression': 'neutral', 'alert_generated': False,
            'timestamp': datetime.now().isoformat()
        }), 200

@app.route('/api/v1/fatigue/recommendations', methods=['GET'])
def get_fatigue_recommendations():
    """Get recommendations based on fatigue"""
    try:
        recommendations = fatigue_detector.get_recommendations_for_fatigue()
        return jsonify({'recommendations': recommendations}), 200
    except Exception as e:
        logger.error(f"Error getting fatigue recommendations: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== BREAK MANAGEMENT ====================

@app.route('/api/v1/breaks/enforce', methods=['POST'])
def enforce_break():
    """Enforce a break"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        duration = data.get('duration', 5)  # minutes
        break_type = data.get('break_type', 'micro')
        lock_screen = data.get('lock_screen', True)
        mute_input = data.get('mute_input', True)
        
        # Log break to database
        break_record = {
            'duration': duration,
            'break_type': break_type,
            'reason': 'Enforced Break',
            'compliance_status': 'In Progress'
        }
        data_service.log_break(user_id, break_record)
        
        break_enforcer.enforce_break(
            duration * 60,  # Convert to seconds
            break_type,
            lock_screen,
            mute_input
        )
        
        # Show notification
        break_enforcer.show_notification(
            'Micro Break',
            f'Time for a {break_type} break! Duration: {duration} minutes'
        )
        
        return jsonify({
            'message': f'{break_type} break enforced',
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error enforcing break: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/breaks/status', methods=['GET'])
def get_break_status():
    """Get break enforcement status"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # Get breaks from today from database
        breaks_today = data_service.get_breaks_today(user_id)
        compliance_rate = data_service.get_break_compliance_rate(user_id, days=7)
        
        return jsonify({
            'breaks_today': len(breaks_today),
            'compliance_rate': compliance_rate,
            'recent_breaks': breaks_today[:5] if breaks_today else []
        }), 200
    except Exception as e:
        logger.error(f"Error getting break status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/breaks/stop', methods=['POST'])
def stop_break():
    """Stop current break enforcement"""
    try:
        break_enforcer.stop_enforcement()
        return jsonify({'message': 'Break enforcement stopped'}), 200
    except Exception as e:
        logger.error(f"Error stopping break: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== RECOMMENDATIONS ====================

@app.route('/api/v1/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized break recommendations"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        fatigue_status = fatigue_detector.get_fatigue_status()
        activity_summary = activity_monitor.get_activity_summary()
        
        recommendations = break_recommender.get_recommendations(
            fatigue_status,
            activity_summary,
            user_id,
            count=2
        )
        
        # Log recommendations to database
        for rec in recommendations:
            data_service.log_recommendation(user_id, rec)
        
        return jsonify({'recommendations': recommendations}), 200
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== PERSONALIZATION ====================

@app.route('/api/v1/personalization/profile', methods=['GET'])
def get_user_profile():
    """Get user profile"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        profile = personalization_engine.get_user_profile(user_id)
        
        if profile:
            return jsonify(profile), 200
        else:
            return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/personalization/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        preferences = data.get('preferences', {})
        
        if personalization_engine.update_user_preferences(user_id, preferences):
            return jsonify({'message': 'Preferences updated'}), 200
        else:
            return jsonify({'error': 'Update failed'}), 500
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/personalization/analyze', methods=['POST'])
def analyze_patterns():
    """Analyze user patterns"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        analysis = personalization_engine.analyze_patterns(user_id)
        
        if analysis:
            return jsonify(analysis), 200
        else:
            return jsonify({'message': 'Not enough data for analysis'}), 202
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ANALYTICS ====================

@app.route('/api/v1/analytics/daily', methods=['GET'])
def get_daily_analytics():
    """Get daily analytics"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        date_str = request.args.get('date', None)
        
        # Get metrics from database
        metrics = data_service.get_daily_metrics(user_id, date_str)
        
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error getting daily analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/analytics/weekly', methods=['GET'])
def get_weekly_analytics():
    """Get weekly analytics"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        metrics = data_service.get_weekly_metrics(user_id)
        
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error getting weekly analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    """Get monthly analytics"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        metrics = data_service.get_weekly_metrics(user_id)  # Using weekly for now
        
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error getting monthly analytics: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== FRONTEND STATIC FILES ====================

@app.route('/')
def serve_index():
    """Serve the main index.html file"""
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    # Check if file exists in frontend directory
    file_path = os.path.join(frontend_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(frontend_dir, filename)
    # Return 404 for missing files
    return jsonify({'error': 'File not found'}), 404

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== APPLICATION STARTUP ====================

import signal
import atexit

def cleanup_on_exit():
    """Cleanup function for graceful shutdown"""
    try:
        logger.info("Shutting down AI Micro Break System...")
        
        # Stop monitoring components
        if activity_monitor.is_monitoring:
            activity_monitor.stop_monitoring()
        
        if fatigue_detector.is_running:
            fatigue_detector.stop_detection()
        
        # Close database connections
        db_manager.close_pool()
        
        logger.info("Cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def handle_signal(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    cleanup_on_exit()
    import sys
    sys.exit(0)

# Register cleanup handlers
atexit.register(cleanup_on_exit)
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

if __name__ == '__main__':
    try:
        logger.info("Starting AI Micro Break System...")
        
        # Create logs directory if not exists
        os.makedirs(LOGGING_CONFIG['log_dir'], exist_ok=True)
        
        # Test database connection
        if db_manager.health_check():
            logger.info("Database connected")
        else:
            logger.warning("Could not connect to database - some features may not work")
        
        # Run Flask app
        logger.info(f"Starting server on {APP_CONFIG['host']}:{APP_CONFIG['port']}")
        app.run(
            host=APP_CONFIG['host'],
            port=APP_CONFIG['port'],
            debug=APP_CONFIG['debug']
        )
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error starting application: {e}")
    finally:
        cleanup_on_exit()
