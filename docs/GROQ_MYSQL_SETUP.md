# Setup Guide: Groq AI + XAMPP MySQL

This guide helps you set up the AI Micro Break System with **Groq AI** and **XAMPP MySQL**.

## Prerequisites

- Windows, macOS, or Linux
- Python 3.8+
- XAMPP (for MySQL)
- Groq API Key

---

## Step 1: Install XAMPP

### Windows
1. Download XAMPP from [https://www.apachefriends.org](https://www.apachefriends.org)
2. Run the installer (xampp-windows-x64-installer.exe)
3. Choose components: Apache, MySQL, PHP
4. Install to `C:\xampp` (default)
5. Start XAMPP Control Panel
6. Click "Start" for MySQL

### macOS
```bash
# Download XAMPP
wget https://sourceforge.net/projects/xampp/files/XAMPP%20Mac/8.2.0/xampp-osx-8.2.0-0-installer.dmg

# Install by opening the DMG and following prompts
# Or use Homebrew
brew install xampp

# Start MySQL
sudo /Applications/XAMPP/xamppfiles/bin/mysqld_safe
```

### Linux
```bash
# Download and install
wget https://sourceforge.net/projects/xampp/files/XAMPP%20Linux/8.2.0/xampp-linux-x64-8.2.0-0-installer.run
chmod +x xampp-linux-x64-8.2.0-0-installer.run
sudo ./xampp-linux-x64-8.2.0-0-installer.run

# Start XAMPP
sudo /opt/lampp/lampp start
```

---

## Step 2: Create Database

### Option A: Using phpMyAdmin (Easiest)

1. Open browser: `http://localhost/phpmyadmin`
2. Click "New" in left sidebar
3. Database name: `ai_microbreak_system`
4. Collation: `utf8mb4_unicode_ci`
5. Click "Create"
6. Select the new database
7. Click "Import" tab
8. Choose `database/schema.sql` file
9. Click "Go"

### Option B: Using Command Line

```bash
# Connect to MySQL
mysql -u root -p

# If XAMPP MySQL has no password, just press Enter when prompted

# Create database
CREATE DATABASE ai_microbreak_system;
USE ai_microbreak_system;

# Import schema
SOURCE /path/to/database/schema.sql;
```

---

## Step 3: Get Groq API Key

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to "API Keys" section
4. Click "Create API Key"
5. Copy the API key
6. Keep it safe (you'll need it in next step)

---

## Step 4: Configure the Application

### Edit `config/config.py`

**Find DATABASE_CONFIG section:**
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'ai_microbreak_system',
    'user': 'root',
    'password': '',  # Leave empty if XAMPP MySQL has no password
    'charset': 'utf8mb4',
    'autocommit': True,
}
```

**If you set a MySQL password during XAMPP install:**
```python
'password': 'your_mysql_password',
```

**Find ML_CONFIG section and add your Groq API key:**
```python
ML_CONFIG = {
    'model_type': 'groq_ai',
    'groq_api_key': 'gsk_YOUR_GROQ_API_KEY_HERE',  # Replace with your key
    'groq_model': 'mixtral-8x7b-32768',
    # ... rest of config
}
```

---

## Step 5: Install Dependencies

```bash
# Navigate to project directory
cd "path/to/AI MICRO BREAK SYSTEM"

# Install Python packages
pip install -r config/requirements.txt
```

---

## Step 6: Run the Application

### Terminal 1: Start Backend
```bash
cd backend
python app.py
```

Expected output:
```
* Running on http://127.0.0.1:5000
* WARNING: This is a development server. Do not use it in production.
```

### Terminal 2: Start Frontend
```bash
cd frontend
python -m http.server 8000
```

Expected output:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

---

## Step 7: Access Dashboard

1. Open browser
2. Go to `http://localhost:8000`
3. You should see the AI Micro Break System dashboard

---

## Verification Checklist

- [ ] XAMPP MySQL running (`http://localhost/phpmyadmin` accessible)
- [ ] Database `ai_microbreak_system` created
- [ ] `schema.sql` imported successfully
- [ ] Python packages installed without errors
- [ ] Groq API key added to `config/config.py`
- [ ] Backend running on `http://localhost:5000`
- [ ] Frontend accessible at `http://localhost:8000`
- [ ] Dashboard loads without errors

---

## Troubleshooting

### MySQL Connection Error
```
Error: [2003] Can't connect to MySQL server on 'localhost:3306'
```

**Solution:**
- Start XAMPP MySQL service
- Check if MySQL port is correct (default 3306)
- Verify credentials in config.py

### Groq API Error
```
Error: Invalid API key
```

**Solution:**
- Verify API key is correct in config/config.py
- Check API key at https://console.groq.com
- Ensure no extra spaces in API key

### Database Import Failed
```
Error: Unknown command '@@'
```

**Solution:**
- Use `schema.sql` (not SQL Server version)
- Ensure file is MySQL syntax compatible
- Try importing via phpMyAdmin instead

### Frontend Not Loading
```
Connection refused on http://localhost:8000
```

**Solution:**
- Ensure `python -m http.server 8000` is running
- Check if port 8000 is available
- Try different port: `python -m http.server 8001`

### Backend API Error
```
ModuleNotFoundError: No module named 'mysql'
```

**Solution:**
- Run: `pip install mysql-connector-python`
- Or: `pip install -r config/requirements.txt`

---

## Testing Groq AI Integration

### Test via API
```bash
# Create a test user
curl -X POST http://localhost:5000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"testpass123"}'

# Get fatigue recommendations (uses Groq AI)
curl http://localhost:5000/api/v1/fatigue/recommendations
```

### Test via Dashboard
1. Start monitoring
2. Wait 10 seconds for fatigue detection
3. Check dashboard for AI-powered analysis
4. Observe Groq AI insights in real-time

---

## Production Deployment

For production use:

1. **Security:**
   - Never commit API keys to version control
   - Use environment variables instead
   - Enable CORS for specific domains only

2. **Database:**
   - Use strong MySQL password
   - Enable backups
   - Consider external database service (AWS RDS, etc.)

3. **Groq AI:**
   - Monitor API usage and costs
   - Implement rate limiting
   - Cache responses when possible

4. **Server:**
   - Use production WSGI server (Gunicorn, uWSGI)
   - Enable SSL/HTTPS
   - Deploy behind reverse proxy (Nginx, Apache)

---

## Next Steps

- [ ] Customize break timing in `config/config.py`
- [ ] Enable/disable webcam in `config/config.py`
- [ ] Configure notification settings
- [ ] Set up user accounts in dashboard
- [ ] Explore AI-powered recommendations
- [ ] Monitor productivity analytics
- [ ] Review logs in `logs/` directory

---

## Support

For issues:
1. Check `logs/app.log` for error details
2. Review troubleshooting section above
3. Check Groq API status: https://status.groq.com
4. Verify MySQL is running in XAMPP Control Panel

## Additional Resources

- [Groq AI Documentation](https://console.groq.com/docs)
- [XAMPP Support](https://www.apachefriends.org/support.html)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Python MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)
