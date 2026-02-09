"""
Database Setup Script for AI Micro Break System
Initializes MySQL database and creates all required tables
"""

import mysql.connector
from mysql.connector import Error
import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # XAMPP default is empty password
}

DB_NAME = 'ai_microbreak_system'

# SQL schema file path
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'schema.sql')


def test_connection():
    """Test MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.close()
        logger.info("[OK] MySQL connection successful")
        return True
    except Error as e:
        logger.error(f"[ERROR] MySQL connection failed: {e}")
        logger.error("Make sure XAMPP MySQL is running")
        return False


def create_database():
    """Create the database if it doesn't exist"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        logger.info(f"[OK] Database '{DB_NAME}' ready")
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        logger.error(f"[ERROR] Failed to create database: {e}")
        return False


def run_schema():
    """Execute the SQL schema file to create tables"""
    try:
        if not os.path.exists(SCHEMA_FILE):
            logger.error(f"[ERROR] Schema file not found: {SCHEMA_FILE}")
            return False
        
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # First, create and use database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        # Read schema file
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # Remove comments and split statements
        lines = schema_content.split('\n')
        current_statement = []
        
        for line in lines:
            # Remove line comments
            if '--' in line:
                line = line[:line.index('--')]
            
            line = line.strip()
            if line:
                current_statement.append(line)
            
            # Execute when we hit a semicolon
            if line.endswith(';'):
                full_statement = ' '.join(current_statement)
                
                if not full_statement.startswith('CREATE DATABASE') and not full_statement.startswith('USE '):
                    try:
                        cursor.execute(full_statement)
                    except Error as e:
                        if 'already exists' in str(e).lower():
                            pass  # Table already exists, skip
                        elif 'no database selected' in str(e).lower():
                            pass  # Database switched, continue
                        else:
                            logger.warning(f"[WARN] SQL Warning: {e}")
                
                current_statement = []
        
        conn.commit()
        logger.info("[OK] Database schema created successfully")
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        logger.error(f"[ERROR] Failed to execute schema: {e}")
        return False


def create_test_user():
    """Create a test user for development"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_NAME,
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Check if test user already exists
        cursor.execute("SELECT UserID FROM Users WHERE Username = 'testuser'")
        if cursor.fetchone():
            logger.info("[INFO] Test user already exists")
        else:
            # Create test user
            query = """
            INSERT INTO Users (Username, Email, PasswordHash, PreferredBreakDuration, BreakInterval)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, ('testuser', 'test@example.com', 'hashed_password_here', 5, 30))
            conn.commit()
            logger.info("[OK] Test user created successfully")
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        logger.error(f"[ERROR] Failed to create test user: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("AI Micro Break System - Database Setup")
    print("=" * 60)
    
    steps = [
        ("Testing MySQL connection", test_connection),
        ("Creating database", create_database),
        ("Running schema", run_schema),
        ("Creating test user", create_test_user),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if step_func():
            success_count += 1
        else:
            print(f"Failed on: {step_name}")
            print("\nMake sure:")
            print("1. XAMPP is installed")
            print("2. MySQL service is running in XAMPP Control Panel")
            print("3. Database password is empty (default for XAMPP)")
            return False
    
    print("\n" + "=" * 60)
    print(f"Setup Complete! ({success_count}/{len(steps)} steps successful)")
    print("=" * 60)
    print("\nYou can now run: python app.py")
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
