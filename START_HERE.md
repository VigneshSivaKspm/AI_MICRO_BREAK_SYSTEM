# AI MICRO BREAK SYSTEM - START HERE 🚀

Welcome to the **AI Micro Break System** project! This is a complete, production-ready system for intelligent fatigue detection and break management.

## 📖 Quick Navigation

### 👈 First Time? Start Here:
1. **[READ THIS FIRST](./README.md)** - Complete system overview
2. **[Installation Guide](./docs/INSTALLATION.md)** - Setup instructions for your OS
3. **[Quick Start](./quickstart.bat)** or **[Quick Start](./quickstart.sh)** - Automated setup

### 🔧 For Developers:
- **[API Documentation](./docs/API.md)** - All 20+ REST endpoints with examples
- **[Project Summary](./PROJECT_SUMMARY.md)** - Technical details and statistics
- **[Contributing Guidelines](./docs/CONTRIBUTING.md)** - How to contribute

### 📁 Project Structure:

```
├── backend/              👈 Flask REST API Server
├── modules/              👈 6 Core AI/ML Modules
│   ├── activity_monitor.py
│   ├── fatigue_detection.py
│   ├── break_enforcement.py
│   ├── break_recommendation.py
│   ├── personalization.py
│   └── productivity_analytics.py
├── frontend/             👈 Interactive Dashboard
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── config/               👈 Configuration Files
│   ├── config.py
│   └── requirements.txt
├── database/             👈 SQL Server Schema
│   └── schema.sql
├── docs/                 👈 Documentation
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── API.md
│   └── CONTRIBUTING.md
└── quickstart.bat/sh     👈 Auto Setup Scripts
```

---

## ⚡ 5-Minute Quick Start

### Windows:
```bash
# Run this in Command Prompt
quickstart.bat
```

### macOS/Linux:
```bash
# Run this in Terminal
chmod +x quickstart.sh
./quickstart.sh
```

### Or Manual Setup:
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r config/requirements.txt

# 3. Terminal 1: Start Backend
cd backend
python app.py

# 4. Terminal 2: Start Frontend (new terminal)
cd frontend
python -m http.server 8000

# 5. Open http://localhost:8000 in your browser
```

---

## 🎯 What This System Does

### Monitor
👁️ Tracks mouse, keyboard, idle time, and fatigue indicators

### Detect
🧠 AI-powered detection of:
- Eye strain
- Poor posture
- Facial fatigue
- Cognitive load

### Enforce
⏰ Intelligent break management:
- Personalized break timing
- Screen locking
- Notifications
- Progress tracking

### Recommend
💡 Smart wellness suggestions:
- 10 curated activities
- Personalized to user
- Adaptive learning
- Compliance tracking

### Analyze
📊 Comprehensive analytics:
- Productivity scores
- Compliance rates
- Fatigue patterns
- Trends & insights

---

## 🔑 Key Features

✅ **AI-Powered Fatigue Detection** - Webcam + activity analysis  
✅ **Personalized Break Engine** - Learns user preferences  
✅ **Real-time Dashboard** - Beautiful, responsive interface  
✅ **REST API** - 20+ endpoints for integration  
✅ **Analytics** - Daily/weekly/monthly reports  
✅ **Cross-Platform** - Windows, macOS, Linux  
✅ **Production Ready** - 5,000+ lines of quality code  

---

## 📊 Dashboard Features

### Real-Time Monitoring
- Activity level indicator
- Fatigue score
- Eye strain detection
- Posture assessment
- Status alerts

### Break Management
- Enforce micro-breaks
- Custom duration
- Screen lock option
- Break timer
- Compliance tracking

### Analytics
- Productivity score
- Work/break time
- Compliance rate
- Focus score
- Weekly/monthly trends

### Personalization
- User profiles
- Preference settings
- Activity history
- Performance tracking

---

## 🔌 API Examples

### Start Monitoring
```bash
curl -X POST http://localhost:5000/api/v1/monitoring/start
```

### Get Fatigue Status
```bash
curl http://localhost:5000/api/v1/fatigue/status
```

### Get Recommendations
```bash
curl http://localhost:5000/api/v1/recommendations?user_id=1
```

### Enforce Break
```bash
curl -X POST http://localhost:5000/api/v1/breaks/enforce \
  -H "Content-Type: application/json" \
  -d '{"duration": 5, "break_type": "micro"}'
```

### Get Analytics
```bash
curl http://localhost:5000/api/v1/analytics/daily?user_id=1
```

[See all API endpoints →](./docs/API.md)

---

## 🛠️ Configuration

Edit `config/config.py` to customize:

```python
# Break timing
BREAK_CONFIG['default_break_interval'] = 30  # minutes
BREAK_CONFIG['default_break_duration'] = 5   # minutes

# Fatigue detection
FATIGUE_CONFIG['fatigue_threshold'] = 0.7    # 0-1 scale
FATIGUE_CONFIG['use_webcam'] = True          # Enable/disable webcam

# Monitoring
ACTIVITY_CONFIG['monitor_interval'] = 5      # seconds
ACTIVITY_CONFIG['idle_threshold'] = 300      # seconds
```

[Full configuration guide →](./README.md#Configuration%20Options)

---

## 📚 Documentation

| Document | Purpose | Length |
|----------|---------|--------|
| [README.md](./README.md) | Complete overview & guide | 500+ lines |
| [INSTALLATION.md](./docs/INSTALLATION.md) | Setup for all platforms | 400+ lines |
| [API.md](./docs/API.md) | REST API reference | 500+ lines |
| [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) | Technical details | 300+ lines |

---

## 🆘 Troubleshooting

### "Module not found" error
```bash
pip install -r config/requirements.txt
```

### Database connection failed
1. Install SQL Server (or SQL Server Express)
2. Update credentials in `config/config.py`
3. Run `database/schema.sql`

### Port already in use
```bash
# Change port in config/config.py
# Or kill process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

### Webcam not detected
```python
# Disable in config.py
FATIGUE_CONFIG['use_webcam'] = False
```

[More troubleshooting →](./docs/INSTALLATION.md#Troubleshooting%20Common%20Issues)

---

## 🎓 For Students/Researchers

This project demonstrates:
- ✅ **Machine Learning** - Fatigue detection models
- ✅ **Computer Vision** - OpenCV for facial analysis  
- ✅ **Web Development** - REST API + Frontend
- ✅ **Database Design** - SQL schema optimization
- ✅ **System Design** - Modular architecture
- ✅ **Best Practices** - Documentation, testing, deployment

Perfect for:
- Portfolio projects
- Academic research
- Thesis work
- Learning full-stack development

---

## 💼 For Enterprises

Ready for:
- ✅ Deployment to production
- ✅ Integration with existing systems
- ✅ Multi-user configuration
- ✅ Docker containerization
- ✅ Cloud deployment (AWS, Azure, GCP)
- ✅ Custom modifications

---

## 📞 Need Help?

1. **Check the README** - [README.md](./README.md)
2. **Review Installation Guide** - [INSTALLATION.md](./docs/INSTALLATION.md)
3. **Check API Docs** - [API.md](./docs/API.md)
4. **View logs** - `logs/app.log`
5. **See troubleshooting** - [INSTALLATION.md#Troubleshooting](./docs/INSTALLATION.md#Troubleshooting%20Common%20Issues)

---

## 🚀 Next Steps

1. **Start the application** - Run quickstart script
2. **Open dashboard** - Go to `http://localhost:8000`
3. **Enable monitoring** - Click "Start Monitoring"
4. **Check metrics** - View real-time data
5. **Configure settings** - Customize for your needs

---

## ✨ You're all set! 

**Start monitoring** → **Take breaks** → **Get productive** → **Be healthy**

🎉 Welcome to the AI Micro Break System!

---

**Last Updated**: January 27, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
