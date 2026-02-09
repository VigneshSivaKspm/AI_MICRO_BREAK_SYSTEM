# Migration Guide: SQL Server → Groq AI + MySQL

This document shows all changes made to migrate from SQL Server to Groq AI + XAMPP MySQL.

## What Changed

### 1. Dependencies (config/requirements.txt)
**REMOVED:**
- `pyodbc==4.0.39` (SQL Server ODBC driver)

**ADDED:**
- `mysql-connector-python==8.2.0` (MySQL client library)
- `groq==0.4.1` (Groq AI SDK)

---

### 2. Database Configuration (config/config.py)

**OLD (SQL Server):**
```python
DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'AI_MicroBreakSystem',
    'user': 'sa',
    'password': 'YourPassword123',
    'authentication': 'sql'
}
```

**NEW (MySQL):**
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'ai_microbreak_system',
    'user': 'root',
    'password': '',  # XAMPP default (empty)
    'charset': 'utf8mb4',
    'autocommit': True,
}
```

**KEY DIFFERENCES:**
- No ODBC driver configuration needed
- Database name in lowercase with underscores
- Default XAMPP user is `root` with empty password
- MySQL port is always 3306
- Added charset configuration
- Added autocommit flag

---

### 3. ML Configuration (config/config.py)

**OLD (TensorFlow):**
```python
ML_CONFIG = {
    'model_type': 'tensorflow',
    'fatigue_model_path': 'models/fatigue_detection_model.h5',
    'posture_model_path': 'models/posture_detection_model.h5',
    # ... training parameters
}
```

**NEW (Groq AI):**
```python
ML_CONFIG = {
    'model_type': 'groq_ai',
    'groq_api_key': 'gsk_YOUR_GROQ_API_KEY_HERE',  # Get from console.groq.com
    'groq_model': 'mixtral-8x7b-32768',  # Fast and capable
    'fatigue_model_path': 'models/fatigue_detection_model.h5',  # For training
    'posture_model_path': 'models/posture_detection_model.h5',  # For training
    # ... training parameters unchanged
}
```

**KEY BENEFITS:**
- No local model training required
- Instant AI-powered analysis via Groq
- Faster inference time
- Cloud-based, always up-to-date models

---

### 4. Database Manager (backend/database_manager.py)

**IMPORTS:**
```python
# OLD
import pyodbc

# NEW
import mysql.connector
from mysql.connector import Error
```

**CONNECTION METHOD:**
```python
# OLD
def _build_connection_string(self) -> str:
    return f"Driver={...};Server={...};Database={...};"
self.connection = pyodbc.connect(self.connection_string)

# NEW
def connect(self) -> bool:
    self.connection = mysql.connector.connect(
        host=self.config['host'],
        port=self.config['port'],
        database=self.config['database'],
        user=self.config['user'],
        password=self.config['password'],
        charset=self.config.get('charset', 'utf8mb4'),
        autocommit=self.config.get('autocommit', True)
    )
```

**CURSOR HANDLING:**
```python
# OLD - pyodbc default
cursor = self.connection.cursor()

# NEW - MySQL with dictionary results
cursor = self.connection.cursor(dictionary=True)
```

**QUERY PARAMETERS:**
```python
# OLD - SQL Server syntax (? placeholders)
query = "INSERT INTO Users VALUES (?, ?, ?)"

# NEW - MySQL syntax (% placeholders)
query = "INSERT INTO Users VALUES (%s, %s, %s)"
```

**ERROR HANDLING:**
```python
# OLD
except Exception as e:

# NEW - More specific
except Error as e:
```

---

### 5. Database Schema (database/schema.sql)

#### Structure Changes

**OLD (SQL Server):**
```sql
-- Database
CREATE DATABASE IF NOT EXISTS AI_MicroBreakSystem;
GO
USE AI_MicroBreakSystem;
GO

-- Table
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(100) NOT NULL UNIQUE,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE(),
    LastLogin DATETIME,
    IsActive BIT DEFAULT 1,
);
GO

-- Indexes
CREATE INDEX idx_ActivityLog_UserID ON ActivityLog(UserID);
GO
```

**NEW (MySQL):**
```sql
-- Database
CREATE DATABASE IF NOT EXISTS ai_microbreak_system;
USE ai_microbreak_system;

-- Table
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(100) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    LastLogin TIMESTAMP NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    INDEX idx_username (Username),
    INDEX idx_email (Email)
);

-- Indexes (automatically managed)
```

#### Data Type Mapping

| SQL Server | MySQL | Notes |
|-----------|-------|-------|
| `NVARCHAR(n)` | `VARCHAR(n)` | Unicode by default in MySQL |
| `DATETIME` | `TIMESTAMP` | For auto-timestamps |
| `BIT` | `BOOLEAN` | Equivalent types |
| `FLOAT` | `FLOAT` | Unchanged |
| `NVARCHAR(MAX)` | `JSON` | For PersonalizationProfile |
| `IDENTITY(1,1)` | `AUTO_INCREMENT` | Auto-incrementing IDs |
| `GETDATE()` | `CURRENT_TIMESTAMP` | Current time function |
| `DEFAULT GETDATE()` | `DEFAULT CURRENT_TIMESTAMP` | Default timestamps |

#### Foreign Keys

**OLD:**
```sql
FOREIGN KEY (UserID) REFERENCES Users(UserID)
```

**NEW:**
```sql
FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
```

MySQL includes explicit cascade delete for referential integrity.

---

### 6. New Groq AI Module (modules/groq_ai_integration.py)

**NEW FILE** - Provides AI-powered analysis:

```python
class GroqAIIntegration:
    def analyze_fatigue_status(self, fatigue_metrics: Dict) -> Dict
    def get_personalized_recommendation(self, user_profile: Dict, activity_history: List) -> Dict
    def analyze_productivity_patterns(self, analytics_data: Dict) -> Dict
```

**Features:**
- Real-time fatigue analysis using Groq AI
- Personalized break recommendations
- Productivity pattern insights
- Fallback logic when API unavailable
- Conversation history support

---

### 7. Frontend Integration (No Changes Required)

The frontend (`frontend/index.html`, `frontend/script.js`, `frontend/styles.css`) remains unchanged:
- API endpoints remain the same
- Request/response formats unchanged
- UI functionality identical
- Works seamlessly with new backend

---

## SQL Server → MySQL Query Syntax Changes

### Common Changes in Application Queries

**SELECT with Timestamps:**
```sql
-- OLD (SQL Server)
SELECT * FROM ActivityLog WHERE Timestamp > GETDATE() - 1

-- NEW (MySQL)
SELECT * FROM ActivityLog WHERE Timestamp > DATE_SUB(NOW(), INTERVAL 1 DAY)
```

**INSERT with IDENTITY:**
```sql
-- OLD (SQL Server)
INSERT INTO Users (Username, Email) VALUES ('user', 'email@test.com')
-- Returns @@IDENTITY

-- NEW (MySQL)
INSERT INTO Users (Username, Email) VALUES ('user', 'email@test.com')
-- Returns LAST_INSERT_ID()
```

**Bulk Insert:**
```sql
-- OLD (SQL Server)
INSERT INTO ActivityLog VALUES (?, ?, ?), (?, ?, ?), (?, ?, ?)

-- NEW (MySQL)
INSERT INTO ActivityLog VALUES (%s, %s, %s), (%s, %s, %s), (%s, %s, %s)
```

---

## Installation Steps Summary

1. **Install XAMPP** → Includes MySQL
2. **Configure MySQL** → Create database `ai_microbreak_system`
3. **Import Schema** → Run `database/schema.sql` in phpMyAdmin
4. **Get Groq API Key** → From https://console.groq.com
5. **Update Config** → Add API key to `config/config.py`
6. **Install Dependencies** → `pip install -r config/requirements.txt`
7. **Run Application** → Start backend and frontend

---

## Verification Commands

### Test MySQL Connection
```bash
mysql -u root -p
# Then:
USE ai_microbreak_system;
SHOW TABLES;
```

### Test Groq Integration
```python
from modules.groq_ai_integration import get_groq_ai
groq = get_groq_ai()
result = groq.analyze_fatigue_status({'fatigue_score': 0.7})
print(result)
```

### Test Full Stack
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && python -m http.server 8000

# Browser: http://localhost:8000
```

---

## Rollback (If Needed)

To revert to SQL Server version:

1. **Revert Dependencies:**
   ```bash
   # Remove new packages
   pip uninstall mysql-connector-python groq -y
   # Install old
   pip install pyodbc
   ```

2. **Restore Old Config:**
   - Replace `config/config.py` from backup
   - Update `DATABASE_CONFIG` with SQL Server settings

3. **Restore Old Database Manager:**
   - Use original `backend/database_manager.py`
   - Update pyodbc connection logic

4. **Restore SQL Schema:**
   - Import original `database/schema.sql` for SQL Server

---

## Summary

| Aspect | SQL Server | Groq AI + MySQL |
|--------|-----------|-----------------|
| Database | SQL Server (ODBC) | XAMPP MySQL |
| AI Model | Local TensorFlow | Cloud Groq AI |
| Setup | Complex (SQL Server install) | Simple (XAMPP) |
| Cost | SQL Server license | Groq free tier |
| Scalability | Limited | Highly scalable |
| Maintenance | Manual updates | Cloud managed |
| Performance | Depends on hardware | Cloud optimized |
| Deployment | On-premises only | Cloud-ready |

---

## Performance Notes

**Improvements:**
- Faster AI inference (Groq optimized models)
- Reduced local memory usage (no local ML models)
- Simpler deployment (no SQL Server required)
- Better scalability (cloud-based)

**Considerations:**
- Requires internet for Groq API
- MySQL slower than SQL Server for complex queries (offset by Groq speed)
- XAMPP suitable for development, use production MySQL for deployment

---

## Next Steps

1. Follow `docs/GROQ_MYSQL_SETUP.md` for detailed setup
2. Test all endpoints with new configuration
3. Verify Groq AI responses are working
4. Monitor API usage and costs
5. Configure production environment if needed
