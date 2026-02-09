"""
Configuration file for AI Micro Break System
Load sensitive data from environment variables
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== DATABASE CONFIGURATION (MYSQL - XAMPP) ====================
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'ai_microbreak_system'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4',
    'autocommit': True,
}

# ==================== APPLICATION SETTINGS ====================
APP_CONFIG = {
    'app_name': 'AI Micro Break System',
    'version': '1.0.0',
    'debug': True,
    'host': '127.0.0.1',
    'port': 2050,
    'secret_key': 'your-secret-key-change-this',
}

# ==================== BREAK SETTINGS ====================
BREAK_CONFIG = {
    'adaptive_break_interval': True,  # Let AI determine optimal break intervals
    'default_break_interval_min': 15,  # minimum minutes between breaks
    'default_break_interval_max': 45,  # maximum minutes between breaks
    'default_break_duration': 5,       # default break duration in minutes
    'default_break_duration_min': 3,   # minimum break duration in minutes
    'default_break_duration_max': 10,  # maximum break duration in minutes
    'daily_work_limit': 480,           # minutes (8 hours)
    'enforce_break_on_detection': True,
    'screen_fade_duration': 10,        # seconds
}

# ==================== FATIGUE DETECTION SETTINGS ====================
FATIGUE_CONFIG = {
    'use_ai_analysis': True,           # Use Groq AI for fatigue analysis
    'use_webcam': os.getenv('USE_WEBCAM', 'False').lower() == 'true',  # Optional webcam
    'webcam_index': int(os.getenv('WEBCAM_INDEX', 0)),
    'detection_interval': 10,          # seconds between detections
    'face_cascade_path': 'models/haarcascade_frontalface_default.xml',
    'eye_cascade_path': 'models/haarcascade_eye.xml',
    'min_fatigue_score_for_break': 0.6,  # AI will determine if break needed
}

# ==================== ACTIVITY MONITORING SETTINGS ====================
ACTIVITY_CONFIG = {
    'monitor_interval': 5,  # seconds
    'idle_threshold': 300,  # seconds (5 minutes)
    'low_activity_threshold': 50,  # clicks/keystrokes per minute
    'log_activity': True,
    'activity_buffer_size': 1000,
}

# ==================== ML MODEL SETTINGS (with GROQ AI) ====================
ML_CONFIG = {
    'model_type': 'groq_ai',  # Using Groq AI for inference
    'groq_api_key': os.getenv('GROQ_API_KEY', ''),  # Get from https://console.groq.com (Free tier)
    'groq_model': os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant'),  # Free tier: fastest production model
    'enable_ai_fatigue_detection': True,  # Use AI for fatigue analysis
    'enable_ai_recommendations': True,  # Use AI for break recommendations
    'enable_ai_personalization': True,  # Use AI for personalization
    'ai_analysis_confidence_threshold': 0.7,  # Confidence threshold for AI decisions
    'retrain_interval': 7,  # days
    'training_data_retention': 30,  # days
}

# ==================== PERSONALIZATION SETTINGS ====================
PERSONALIZATION_CONFIG = {
    'adapt_to_user': True,
    'learning_window': 14,  # days
    'min_data_points': 100,
    'update_frequency': 1,  # days
    'preferred_break_types': ['eye_exercise', 'stretching', 'hydration', 'breathing', 'walking'],
}

# ==================== RECOMMENDATION SETTINGS ====================
RECOMMENDATION_CONFIG = {
    'random_tips': True,
    'personalized_tips': True,
    'tips_per_break': 2,
    'rotation_strategy': 'weighted_random',  # can be 'random', 'sequential', 'weighted_random'
}

# ==================== LOGGING SETTINGS ====================
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_dir': 'logs',
    'log_file': 'app.log',
    'max_log_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5,
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# ==================== NOTIFICATION SETTINGS ====================
NOTIFICATION_CONFIG = {
    'enable_sound': True,
    'enable_popup': True,
    'sound_file': 'sounds/notification.wav',
    'notification_duration': 5,  # seconds
}

# ==================== FILE PATHS ====================
FILE_PATHS = {
    'models_dir': 'models',
    'data_dir': 'data',
    'logs_dir': 'logs',
    'cache_dir': 'cache',
    'temp_dir': 'temp',
    'frontend_dir': 'frontend',
}

# ==================== SECURITY SETTINGS ====================
SECURITY_CONFIG = {
    'enable_encryption': True,
    'session_timeout': 3600,  # seconds
    'password_min_length': 8,
    'password_require_special_chars': True,
    'enable_2fa': False,
}

# ==================== ANALYTICS SETTINGS ====================
ANALYTICS_CONFIG = {
    'track_productivity': True,
    'track_compliance': True,
    'export_format': 'csv',  # can be 'csv', 'json', 'excel'
    'retention_period': 90,  # days
}

# ==================== API SETTINGS ====================
API_CONFIG = {
    'api_prefix': '/api/v1',
    'enable_cors': True,
    'cors_origins': ['http://localhost:3000', 'http://localhost:5050', 'http://localhost:9000'],
    'rate_limit': 1000,  # requests per hour
}

# ==================== DEVELOPMENT SETTINGS ====================
if os.environ.get('ENVIRONMENT') == 'development':
    APP_CONFIG['debug'] = True
    LOGGING_CONFIG['log_level'] = 'DEBUG'
    FATIGUE_CONFIG['use_webcam'] = False
elif os.environ.get('ENVIRONMENT') == 'production':
    APP_CONFIG['debug'] = False
    LOGGING_CONFIG['log_level'] = 'WARNING'
    SECURITY_CONFIG['enable_encryption'] = True

# ==================== CONSTANTS ====================
BREAK_TYPES = ['micro', 'regular', 'long', 'forced']
ACTIVITY_TYPES = ['keyboard', 'mouse', 'screen_interaction', 'idle']
FATIGUE_LEVELS = ['low', 'moderate', 'high', 'critical']
RECOMMENDATION_TYPES = ['eye_exercise', 'stretching', 'hydration', 'breathing', 'meditation', 'walking']
