# AI Micro Break System - AI-Enhanced Edition

A comprehensive AI-powered system designed to intelligently monitor user activity, detect fatigue using Groq AI, and enforce personalized micro-breaks to enhance employee well-being and productivity.

## ✨ Key Features

✅ **Groq AI-Powered Fatigue Analysis**
- Real-time activity-based fatigue detection
- Optional webcam integration for facial analysis
- AI determines optimal break intervals dynamically
- Learns work patterns over time

✅ **Intelligent Break Recommendations**
- AI generates personalized activity suggestions
- Avoids activity repetition
- Adapts to current fatigue level and available time
- Provides step-by-step instructions

✅ **Adaptive Scheduling**
- AI learns individual work patterns
- Adjusts break intervals based on productivity
- Balances health vs. performance
- Flexible to user preferences

✅ **User Activity Monitoring**
- Real-time mouse and keyboard tracking
- Idle period detection
- Activity level analysis
- Session duration tracking

✅ **Productivity Analytics**
- Track compliance with breaks
- Measure break effectiveness
- Analyze productivity patterns
- Generate weekly/monthly reports

✅ **Web Dashboard**
- Real-time status monitoring
- Manual break triggering
- View recommendations
- Check analytics
- User-friendly interface

## Technology Stack

- **Backend**: Flask + Python
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Engine**: Groq API (Mixtral model)
- **Database**: MySQL
- **Activity Tracking**: pynput, psutil
- **Vision**: OpenCV (optional)

## Quick Start

```bash
# 1. Clone/Download project
# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r config/requirements.txt

# 4. Configure (edit .env file)
GROQ_API_KEY=your_api_key_here

# 5. Run backend
python -m backend.app

# 6. Run frontend (new terminal)
cd frontend && python -m http.server 9000

# 7. Open http://localhost:9000 in browser
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed configuration.

## Project Structure

```
AI MICRO BREAK SYSTEM/
├── backend/
│   ├── app.py                 # Flask REST API
│   ├── database_manager.py    # Database operations
├── modules/
│   ├── activity_monitor.py           # Module 1: Activity Monitoring
│   ├── fatigue_detection.py          # Module 2: Fatigue Detection
│   ├── break_enforcement.py          # Module 3: Break Enforcement
│   ├── break_recommendation.py       # Module 4: Recommendations
│   ├── personalization.py            # Module 5: Personalization
│   ├── productivity_analytics.py     # Module 6: Analytics
├── frontend/
│   ├── index.html             # Main dashboard UI
│   ├── styles.css             # Styling
│   ├── script.js              # Frontend logic
├── config/
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
├── database/
│   ├── schema.sql             # SQL Server database schema
├── logs/                       # Application logs
└── docs/
    └── README.md              # This file
```

## System Architecture

### 6 Core Modules

#### 1. **User Activity Monitoring Module**
- Tracks mouse clicks, keyboard presses
- Monitors screen interaction time
- Detects idle periods
- Analyzes keystroke and mouse dynamics
- Real-time activity level calculation

#### 2. **AI-Based Fatigue Detection Module**
- OpenCV-based facial analysis
- Eye strain detection
- Posture assessment
- Blink rate analysis
- Facial expression recognition
- Webcam integration (optional)

#### 3. **Break Enforcement Module**
- Screen locking mechanism
- Input muting capability
- Progressive notifications
- Cross-platform support
- Graceful break completion

#### 4. **Break Recommendation Module**
- 10 wellness activities database
- Smart filtering by fatigue type
- User preference personalization
- Weighted random selection
- Rotation strategies

#### 5. **Personalization & Learning Module**
- User profile creation and management
- Pattern analysis (activity, fatigue, compliance)
- Adaptive threshold adjustment
- Profile persistence
- Preference learning

#### 6. **Productivity Analytics Module**
- Daily/weekly/monthly metrics
- Productivity scoring algorithm
- Focus score calculation
- Break effectiveness analysis
- Compliance rate tracking
- Export capabilities (JSON, CSV)

## Installation & Setup

### Prerequisites
- Python 3.8+
- SQL Server (or SQL Server Express)
- Pip package manager
- Webcam (optional)

### Step 1: Clone/Download Project
```bash
cd "e:\VIGNESH\College Projects\AJJSAPT\Completed\AI MICRO BREAK SYSTEM"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r config/requirements.txt
```

### Step 4: Configure Database

#### Option A: Use SQL Server (Recommended)
1. Open SQL Server Management Studio (SSMS)
2. Run the script: `database/schema.sql`
3. Update credentials in `config/config.py`:
   ```python
   DATABASE_CONFIG = {
       'server': 'YOUR_SERVER',
       'database': 'AI_MicroBreakSystem',
       'user': 'your_user',
       'password': 'your_password'
   }
   ```

#### Option B: Use SQLite (For Testing)
- Modify `config.py` to use SQLite
- Schema will be auto-created

### Step 5: Update Configuration
Edit `config/config.py` with your preferences:
- Break intervals and durations
- Fatigue thresholds
- Database credentials
- Logging settings

### Step 6: Run the Backend
```bash
cd backend
python app.py
```

Server will start at: `http://localhost:5050`

### Step 7: Open Frontend
Open `frontend/index.html` in your web browser or serve it:
```bash
# Using Python's built-in server
python -m http.server 9000 --directory frontend
```

Access at: `http://localhost:9000`

## API Endpoints

### Health Check
- `GET /api/v1/health` - System health status

### Monitoring
- `POST /api/v1/monitoring/start` - Start monitoring
- `POST /api/v1/monitoring/stop` - Stop monitoring
- `GET /api/v1/activity/current` - Get current activity

### Fatigue Detection
- `GET /api/v1/fatigue/status` - Get fatigue status
- `GET /api/v1/fatigue/recommendations` - Get recommendations

### Break Management
- `POST /api/v1/breaks/enforce` - Enforce break
- `GET /api/v1/breaks/status` - Get break status
- `POST /api/v1/breaks/stop` - Stop break enforcement

### Personalization
- `GET /api/v1/personalization/profile` - Get user profile
- `PUT /api/v1/personalization/preferences` - Update preferences
- `POST /api/v1/personalization/analyze` - Analyze patterns

### Analytics
- `GET /api/v1/analytics/daily` - Daily metrics
- `GET /api/v1/analytics/weekly` - Weekly metrics
- `GET /api/v1/analytics/monthly` - Monthly metrics

## Usage Guide

### Starting the System
1. Click "▶️ Start Monitoring" button
2. System begins tracking activity and fatigue
3. Alerts appear when fatigue is detected
4. Recommendations are provided automatically

### Taking a Break
1. Click "☕ Take Break" or "💡 Get Tips"
2. Select break duration
3. Click "🔒 Enforce Break"
4. Screen locks (optional) and notifications appear
5. Break timer counts down

### Customizing Settings
1. Go to "Profile" tab
2. Adjust break duration and interval
3. Enable/disable webcam and notifications
4. Save preferences

### Viewing Analytics
1. Go to "Analytics" tab
2. View daily productivity score
3. Check compliance rates
4. Review focus metrics
5. Download reports (if enabled)

## Configuration Options

### Break Timing
```python
BREAK_CONFIG = {
    'default_break_interval': 30,      # minutes between breaks
    'default_break_duration': 5,       # minutes per break
    'micro_break_interval': 20,        # micro break timing
    'micro_break_duration': 3,
    'long_break_interval': 120,        # long break timing
}
```

### Fatigue Detection
```python
FATIGUE_CONFIG = {
    'fatigue_threshold': 0.7,          # 0-1 scale
    'eye_strain_threshold': 0.6,
    'posture_threshold': 0.65,
    'use_webcam': True,                # Enable/disable webcam
}
```

### Activity Monitoring
```python
ACTIVITY_CONFIG = {
    'monitor_interval': 5,             # seconds
    'idle_threshold': 300,             # seconds
    'low_activity_threshold': 50,      # clicks/keystrokes per minute
}
```

### Machine Learning
```python
ML_CONFIG = {
    'batch_size': 32,
    'epochs': 50,
    'learning_rate': 0.001,
    'validation_split': 0.2,
}
```

## Database Schema

### Key Tables
- **Users** - User accounts and settings
- **ActivityLog** - Monitored user activity
- **FatigueDetection** - Fatigue scores and data
- **BreakRecords** - Break history
- **Recommendations** - Suggested activities
- **PersonalizationProfile** - User preferences
- **ProductivityAnalytics** - Metrics and analytics
- **WellnessTips** - Wellness activity database

## Features in Detail

### Activity Monitoring
- Tracks mouse clicks and movements
- Monitors keyboard input rate
- Detects idle periods
- Analyzes work-rest cycles
- Calculates activity level percentage

### Fatigue Detection
- Face detection using Haar Cascades
- Eye region analysis
- Posture estimation
- Blink rate calculation
- Facial expression classification
- Combined fatigue score (0-1)

### Break Enforcement
- OS-specific screen locking
- Keyboard/mouse input blocking (Windows)
- Progressive notifications
- Break countdown timer
- Graceful state restoration

### Recommendation Engine
- 10 pre-loaded wellness activities
- Filtering by fatigue type (eye, posture, general)
- User preference personalization
- Weighted random selection
- Activity rotation prevention

### Personalization
- Learns user activity patterns
- Adapts fatigue thresholds
- Identifies peak productivity hours
- Tracks break preferences
- Maintains user profiles

### Analytics
- Productivity scoring (0-100)
- Focus score calculation
- Break compliance tracking
- Break effectiveness analysis
- Daily/weekly/monthly reports
- Data export (JSON/CSV)

## Performance Considerations

### System Requirements
- Processor: Intel i3 or equivalent
- RAM: 4GB minimum
- Storage: 2GB for logs and data
- OS: Windows, macOS, or Linux

### Optimization Tips
1. Increase `monitor_interval` if high CPU usage
2. Reduce `fatigue_threshold` for earlier detection
3. Disable webcam if not needed
4. Archive old logs periodically
5. Tune break intervals based on user feedback

## Troubleshooting

### Connection Issues
```
Error: Database connection failed
Solution: Check credentials in config.py and verify SQL Server is running
```

### Monitoring Not Starting
```
Error: Activity monitoring fails to start
Solution: Ensure pynput library is installed: pip install pynput
```

### Webcam Issues
```
Error: Webcam not detected
Solution: Check camera permissions, set use_webcam=False in config
```

### API Errors
```
Error: 500 Internal Server Error
Solution: Check logs in logs/app.log for details
```

## Advanced Features

### Custom ML Models
- Replace pre-trained models in `models/` directory
- Update model paths in `config.py`
- Retrain periodically with user data

### Database Optimization
- Create indexes on frequently queried columns
- Archive old data periodically
- Monitor query performance

### Scaling
- Use connection pooling for database
- Implement caching for analytics
- Consider load balancing for multiple users

## Security Considerations

### Data Privacy
- Encrypt sensitive user data
- Implement access controls
- Secure webcam data handling
- GDPR compliance considerations

### Authentication
- Implement user authentication (JWT recommended)
- Hash passwords using bcrypt
- Implement session timeouts
- Enable 2FA (optional)

### Encryption
- Encrypt database connections
- Use HTTPS for API
- Encrypt user preference data

## Future Enhancements

- [ ] Integration with wearable devices (Apple Watch, Fitbit)
- [ ] Advanced ML models for better fatigue detection
- [ ] Team analytics and compliance reporting
- [ ] Mobile app (iOS/Android)
- [ ] Voice-based recommendations
- [ ] Integration with calendar systems
- [ ] Multi-language support
- [ ] Advanced visualization dashboards

## Support & Documentation

- **Issues**: Report bugs with logs and screenshots
- **Documentation**: See `docs/` directory
- **API Documentation**: OpenAPI/Swagger support available
- **Logs**: Check `logs/app.log` for troubleshooting

## License

This project is provided as-is for educational and commercial use.

## Authors

Developed as an AI Micro Break System for improving employee well-being and productivity.

## Changelog

### Version 1.0.0 (January 2026)
- Initial release
- All 6 modules implemented
- Frontend dashboard
- REST API
- Database schema
- Complete documentation

---

**Last Updated**: January 27, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
