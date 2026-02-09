# AI Micro Break System - Installation Guide

## Quick Start Guide

### For Windows Users

#### 1. Prerequisites Installation
```bash
# Install Python (if not already installed)
# Download from: https://www.python.org/downloads/

# Verify Python installation
python --version
pip --version
```

#### 2. Database Setup
```bash
# Download SQL Server Express (free version)
# https://www.microsoft.com/en-us/sql-server/sql-server-express

# Or use SQL Server if already installed

# Run schema.sql in SQL Server Management Studio (SSMS):
# 1. Open SSMS
# 2. Connect to your SQL Server
# 3. Open database/schema.sql
# 4. Execute the script
```

#### 3. Clone Repository
```bash
# Navigate to project directory
cd "e:\VIGNESH\College Projects\AJJSAPT\Completed\AI MICRO BREAK SYSTEM"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### 4. Install Dependencies
```bash
pip install -r config/requirements.txt
```

#### 5. Configure System
```bash
# Edit config/config.py with your settings:
# - Database credentials
# - Break intervals
# - Fatigue thresholds
# - API settings
```

#### 6. Run Application
```bash
# Terminal 1: Start Backend
cd backend
python app.py
# Server will run at http://localhost:5050

# Terminal 2: Serve Frontend
# In another terminal, navigate to frontend directory
cd frontend
python -m http.server 9000
# Frontend will be at http://localhost:9000
```

#### 7. Access Dashboard
Open your browser and go to: `http://localhost:9000`

### For macOS Users

#### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Python
```bash
brew install python3
python3 --version
```

#### 3. Install SQL Server (Docker method recommended)
```bash
# Install Docker if not installed
brew install --cask docker

# Pull SQL Server image
docker pull mcr.microsoft.com/mssql/server:2019-latest

# Run SQL Server container
docker run -e 'ACCEPT_EULA=Y' -e 'MSSQL_SA_PASSWORD=YourPassword123' \
  -p 1433:1433 --name sqlserver \
  -d mcr.microsoft.com/mssql/server:2019-latest
```

#### 4. Setup Project
```bash
cd "path/to/AI MICRO BREAK SYSTEM"
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

#### 5. Run Application
```bash
# Terminal 1
cd backend
python3 app.py

# Terminal 2
cd frontend
python3 -m http.server 8000
```

### For Linux Users (Ubuntu/Debian)

#### 1. Install Python and Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install additional dependencies
sudo apt install libpq-dev build-essential
```

#### 2. Install SQL Server (Docker method recommended)
```bash
# Install Docker
sudo apt install docker.io
sudo usermod -aG docker $USER

# Pull and run SQL Server
docker pull mcr.microsoft.com/mssql/server:2019-latest
docker run -e 'ACCEPT_EULA=Y' -e 'MSSQL_SA_PASSWORD=YourPassword123' \
  -p 1433:1433 --name sqlserver \
  -d mcr.microsoft.com/mssql/server:2019-latest
```

#### 3. Setup Project
```bash
cd ~/AI\ MICRO\ BREAK\ SYSTEM
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

#### 4. Run Application
```bash
# Terminal 1
cd backend
python3 app.py

# Terminal 2
cd frontend
python3 -m http.server 8000
```

## Configuration

### Database Connection

Edit `config/config.py`:

```python
DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'AI_MicroBreakSystem',
    'user': 'sa',
    'password': 'YourPassword123',  # Change this!
    'authentication': 'sql'
}
```

### Break Timing

```python
BREAK_CONFIG = {
    'default_break_interval': 30,      # minutes
    'default_break_duration': 5,       # minutes
    'micro_break_interval': 20,        # minutes
    'micro_break_duration': 3,         # minutes
    'long_break_interval': 120,        # minutes
    'long_break_duration': 15,         # minutes
}
```

### Fatigue Detection

```python
FATIGUE_CONFIG = {
    'fatigue_threshold': 0.7,          # 0-1 scale
    'eye_strain_threshold': 0.6,
    'posture_threshold': 0.65,
    'use_webcam': True,                # Set False if no webcam
    'detection_interval': 10,          # seconds
}
```

## Troubleshooting Common Issues

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
pip install -r config/requirements.txt
```

### Issue: "Can't connect to database"

**Solutions:**
1. Check SQL Server is running
2. Verify credentials in config.py
3. Ensure database name matches in config.py
4. Check firewall settings

### Issue: "Port 5000 already in use"

**Solution:**
```bash
# Change port in config/config.py
APP_CONFIG = {
    'port': 5001,  # Change to different port
}

# Or kill process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Issue: Webcam not working

**Solution:**
1. Check camera permissions
2. Set `use_webcam = False` in config.py to use simulation
3. Test webcam with:
   ```bash
   python -c "import cv2; cv2.VideoCapture(0).isOpened()"
   ```

### Issue: High CPU usage

**Solution:**
1. Increase `monitor_interval` in config.py (default: 5 seconds)
2. Disable webcam if not needed
3. Reduce `detection_interval`

## Dependencies Installation

If `pip install -r config/requirements.txt` fails, install individually:

```bash
pip install Flask==2.3.2
pip install Flask-CORS==4.0.0
pip install pyodbc==4.0.39
pip install SQLAlchemy==2.0.19
pip install python-dotenv==1.0.0
pip install opencv-python==4.8.0.74
pip install tensorflow==2.13.0
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scikit-learn==1.3.0
pip install pillow==10.0.0
pip install requests==2.31.0
pip install pydantic==2.1.1
pip install psutil==5.9.5
pip install pynput==1.7.6
pip install PyAudio==0.2.13
pip install mss==9.0.1
pip install pyautogui==0.9.53
pip install schedule==1.2.0
pip install flask-sqlalchemy==3.0.5
pip install pyjwt==2.8.0
pip install bcrypt==4.0.1
pip install python-dateutil==2.8.2
```

## Running with Docker (Advanced)

### Dockerfile Example

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY config/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "backend/app.py"]
```

### Build and Run

```bash
# Build image
docker build -t ai-break-system .

# Run container
docker run -p 5000:5000 ai-break-system
```

## Testing the Installation

```bash
# Test imports
python -c "
import flask
import cv2
import tensorflow
import numpy
print('All imports successful!')
"

# Test database connection
python -c "
from backend.database_manager import get_database_manager
db = get_database_manager()
if db.connect():
    print('Database connection successful!')
"

# Test API
curl http://localhost:5000/api/v1/health
```

## Next Steps

1. Open frontend: `http://localhost:8000`
2. Start monitoring: Click "Start Monitoring" button
3. Review logs: Check `logs/app.log`
4. Configure preferences: Go to Profile tab
5. Check analytics: Go to Analytics tab

## Support

For issues or questions:
1. Check logs in `logs/app.log`
2. Review troubleshooting section above
3. Verify all dependencies are installed
4. Ensure database is properly configured

---

**Version**: 1.0.0  
**Last Updated**: January 27, 2026
