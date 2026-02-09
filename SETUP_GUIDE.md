# AI Micro Break System - Setup & Configuration Guide

## Overview

The AI Micro Break System is an intelligent, adaptive system designed to monitor user activity, detect fatigue, and enforce personalized micro-breaks to enhance employee well-being and productivity.

### Key Features

✅ **AI-Powered Fatigue Detection** - Uses Groq AI to intelligently analyze work patterns  
✅ **Adaptive Break Scheduling** - Learns from user patterns and personalizes intervals  
✅ **Personalized Recommendations** - AI suggests break activities based on current state  
✅ **Activity Monitoring** - Tracks keyboard, mouse, and screen interaction  
✅ **Optional Webcam Support** - Detects facial fatigue indicators  
✅ **Productivity Analytics** - Tracks compliance and performance impact  
✅ **Web Dashboard** - Monitor and control the system from browser  

---

## Quick Start (3 Minutes)

### 1. Prerequisites

- Python 3.8+
- Groq API Key (get free at https://console.groq.com)
- MySQL/XAMPP (optional - for database features)

### 2. Install & Configure

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r config/requirements.txt

# 3. Configure environment
# Edit .env file and add your Groq API key:
GROQ_API_KEY=your_api_key_here
```

### 3. Run the System

```bash
# Terminal 1: Start Backend (http://localhost:5050)
python -m backend.app

# Terminal 2: Start Frontend (http://localhost:9000)
cd frontend
python -m http.server 9000
```

### 4. Access Dashboard

Open browser: **http://localhost:9000**

---

## Configuration Guide

### Environment Variables (.env)

```env
# ========== GROQ AI ==========
GROQ_API_KEY=your_api_key_here          # Required - Get from https://console.groq.com
GROQ_MODEL=mixtral-8x7b-32768           # AI model to use

# ========== DATABASE ==========
DB_HOST=localhost                        # MySQL host
DB_PORT=3306                            # MySQL port
DB_NAME=ai_microbreak_system            # Database name
DB_USER=root                            # Database user
DB_PASSWORD=                            # Database password

# ========== FEATURES ==========
ENABLE_AI_FATIGUE_DETECTION=True        # Use AI for fatigue analysis
ENABLE_AI_RECOMMENDATIONS=True          # Use AI for break suggestions
ENABLE_AI_PERSONALIZATION=True          # Personalize to user

# ========== WEBCAM (Optional) ==========
USE_WEBCAM=False                        # Enable facial detection
WEBCAM_INDEX=0                          # Which webcam to use
```

### Configuration File (config/config.py)

Key settings are now environment-driven. Edit these files for advanced tuning:

- `config/config.py` - Main configuration
- `.env` - Environment variables (sensitive data)
- `.env.example` - Template for .env

---

## How It Works

### 1. Activity Monitoring
- Tracks mouse clicks, keyboard presses, idle time
- Updates activity level in real-time
- Identifies work patterns

### 2. Fatigue Detection (AI-Powered)
- Analyzes activity patterns
- Optional: Detects facial fatigue via webcam
- Uses Groq AI to determine fatigue level
- Generates urgency rating (Low/Medium/High/Critical)

### 3. Break Decision
- AI evaluates:
  - Current fatigue level
  - Work duration
  - Activity patterns
  - Time of day
  - User preferences
- Recommends optimal break timing and duration

### 4. Personalized Recommendations
- AI suggests specific activities
- Avoids repetition (learns from history)
- Matches fatigue level
- Provides step-by-step instructions

### 5. Adaptive Learning
- Learns from compliance data
- Adjusts break intervals
- Optimizes recommendations over time
- Balances productivity vs. health

---

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Monitoring
```
POST /api/v1/monitoring/start
POST /api/v1/monitoring/stop
GET /api/v1/monitoring/status
```

### Fatigue Analysis
```
GET /api/v1/fatigue/status
GET /api/v1/fatigue/analysis
```

### Recommendations
```
GET /api/v1/recommendations/next
GET /api/v1/recommendations/schedule
```

### Analytics
```
GET /api/v1/analytics/daily
GET /api/v1/analytics/weekly
GET /api/v1/analytics/monthly
```

---

## Troubleshooting

### Issue: "Groq API key not configured"
**Solution**: Add `GROQ_API_KEY` to `.env` file or environment variables

### Issue: "Database connection failed"
**Solution**: 
- Ensure MySQL is running
- Check DB credentials in `.env`
- Run database setup: `mysql < database/schema.sql`

### Issue: Webcam not working
**Solution**:
- Set `USE_WEBCAM=False` in `.env` to disable
- System works fine without webcam (activity-based detection)

### Issue: Port 5050/9000 already in use
**Solution**:
```bash
# Find process using port
netstat -ano | findstr :5050

# Kill process
taskkill /PID <PID> /F
```

---

## System Architecture

```
┌─────────────────────────────────────────┐
│      Web Dashboard (Frontend)            │  Port 9000
│      - Monitor status                    │
│      - View recommendations              │
│      - Check analytics                   │
└────────────┬──────────────────────────────┘
             │ HTTP
┌────────────▼──────────────────────────────┐
│      Flask Backend (API)                  │  Port 5050
│      - Activity tracking                  │
│      - Fatigue analysis                   │
│      - Recommendations                    │
└────────────┬──────────────────────────────┘
             │
        ┌────┴─────┬──────────┬───────────┐
        ▼          ▼          ▼           ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
    │ Groq   │ │Activity│ │Fatigue │ │Database  │
    │  AI    │ │Monitor │ │Detector│ │(MySQL)   │
    └────────┘ └────────┘ └────────┘ └──────────┘
```

---

## Key Modules

### `modules/groq_ai_integration.py`
- Handles all AI analysis
- Generates fatigue assessments
- Creates personalized recommendations
- Analyzes compliance patterns

### `modules/activity_monitor.py`
- Tracks keyboard/mouse activity
- Measures idle time
- Calculates activity level

### `modules/fatigue_detection.py`
- Analyzes activity for fatigue signs
- Optional webcam integration
- Trend detection

### `modules/break_recommendation.py`
- Generates activity suggestions
- Learns from user history
- Adapts over time

---

## Performance Tips

1. **Use Groq AI** - It's fast and accurate
   - Enable AI features in `.env`
   - Groq responses are typically < 2 seconds

2. **Activity-Based Detection Works Best**
   - Webcam is optional
   - Works fine on low-end systems

3. **Optimize for User Adoption**
   - Set flexible break intervals initially
   - Gradually increase strictness
   - Allow user customization

4. **Monitor Compliance**
   - Check analytics dashboard
   - Adjust recommendations based on data

---

## Contributing & Customization

### Add New Break Activities
Edit `modules/break_recommendation.py` - `activities_db` list

### Adjust Fatigue Thresholds
Edit `config/config.py` - `FATIGUE_CONFIG` section

### Modify AI Prompts
Edit `modules/groq_ai_integration.py` - Prompt templates

---

## Support & Resources

- **Groq Docs**: https://console.groq.com/docs
- **Python Docs**: https://docs.python.org/3/
- **Flask Docs**: https://flask.palletsprojects.com/

---

## License

Project Type: Educational/Research

---

**Last Updated**: January 30, 2026  
**Version**: 2.0 (AI-Enhanced)
