"""
Database connection and management module
MySQL version for XAMPP with connection pooling and thread safety
"""

import logging
import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional, List, Dict, Any, Union
from config.config import DATABASE_CONFIG
import threading
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MySQL database connections and queries with connection pooling"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.connection_pool = None
        self.pool_lock = threading.Lock()
        self.is_initialized = False
        self._initialize_pool()
    
    def _initialize_pool(self) -> bool:
        """Initialize connection pool"""
        try:
            pool_config = {
                'pool_name': 'ai_microbreak_pool',
                'pool_size': 10,
                'pool_reset_session': True,
                'host': self.config['host'],
                'port': self.config['port'],
                'database': self.config['database'],
                'user': self.config['user'],
                'password': self.config['password'],
                'charset': self.config.get('charset', 'utf8mb4'),
                'autocommit': self.config.get('autocommit', True),
                'sql_mode': 'TRADITIONAL'
            }
            
            self.connection_pool = pooling.MySQLConnectionPool(**pool_config)
            self.is_initialized = True
            logger.info(f"Connection pool initialized for database: {self.config['database']}")
            return True
        except Error as e:
            logger.error(f"Connection pool initialization failed: {e}")
            self.is_initialized = False
            return False
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool with automatic cleanup"""
        connection = None
        connection_created = False
        try:
            with self.pool_lock:
                if not self.is_initialized:
                    if not self._initialize_pool():
                        raise Error("Failed to initialize connection pool")
                    connection_created = True
                
                connection = self.connection_pool.get_connection()
                
            if connection:
                # Only log when we actually create a new connection or pool
                if connection_created:
                    logger.info(f"Connected to MySQL database: {self.config['database']}")
                yield connection
            else:
                raise Error("Failed to get connection from pool")
                
        except Error as e:
            logger.error(f"Database connection error: {e}")
            # Try to reinitialize pool on connection error
            with self.pool_lock:
                self.is_initialized = False
            raise e
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def close_pool(self):
        """Close all connections in the pool"""
        try:
            if self.connection_pool:
                # MySQLConnectionPool doesn't have a close() method in mysql-connector-python
                self.connection_pool = None
                logger.info("Connection pool cleared")
        except Exception as e:
            logger.error(f"Error clearing connection pool: {e}")
    
    def execute_query(self, query: str, params: List = None, retries: int = 2) -> Union[bool, int]:
        """Execute a query (INSERT, UPDATE, DELETE) and return success or last row ID"""
        for attempt in range(retries):
            try:
                with self.get_connection() as connection:
                    cursor = connection.cursor()
                    try:
                        if params:
                            cursor.execute(query, params)
                        else:
                            cursor.execute(query)
                        
                        connection.commit()
                        
                        # If it was an INSERT, return the ID
                        if query.strip().upper().startswith('INSERT'):
                            last_id = cursor.lastrowid
                            return last_id if last_id else True
                            
                        return True
                    finally:
                        cursor.close()
                        
            except Error as e:
                logger.error(f"Query execution failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    return False
                time.sleep(0.5)  # Brief delay before retry
        return False
    
    def fetch_one(self, query: str, params: List = None, retries: int = 2) -> Optional[Dict]:
        """Fetch a single row with connection pooling"""
        for attempt in range(retries):
            try:
                with self.get_connection() as connection:
                    cursor = connection.cursor(dictionary=True)
                    try:
                        if params:
                            cursor.execute(query, params)
                        else:
                            cursor.execute(query)
                        
                        result = cursor.fetchone()
                        return result
                    finally:
                        cursor.close()
                        
            except Error as e:
                if attempt == 0 or 'timeout' in str(e).lower():
                    logger.warning(f"Fetch one failed (attempt {attempt + 1}/{retries}): {e}")
                else:
                    logger.error(f"Fetch one failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    return None
                time.sleep(0.3)  # Brief delay before retry
        return None
    
    def fetch_all(self, query: str, params: List = None, retries: int = 2) -> List[Dict]:
        """Fetch all rows with connection pooling"""
        for attempt in range(retries):
            try:
                with self.get_connection() as connection:
                    cursor = connection.cursor(dictionary=True)
                    try:
                        if params:
                            cursor.execute(query, params)
                        else:
                            cursor.execute(query)
                        
                        result = cursor.fetchall()
                        return result if result else []
                    finally:
                        cursor.close()
                     
            except Error as e:
                if attempt == 0 or 'timeout' in str(e).lower():
                    logger.warning(f"Fetch all failed (attempt {attempt + 1}/{retries}): {e}")
                else:
                    logger.error(f"Fetch all failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    return []
                time.sleep(0.3)  # Brief delay before retry
        return []
    
    def log_activity(self, user_id: int, activity_data: Dict) -> bool:
        """Log user activity with improved error handling"""
        try:
            query = """
                INSERT INTO ActivityLog 
                (UserID, MouseActivity, KeyboardActivity, ScreenInteractionTime, IdlePeriod, ApplicationName)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = [
                user_id,
                activity_data.get('mouse_clicks', 0),
                activity_data.get('keyboard_presses', 0),
                activity_data.get('screen_time', 0),
                activity_data.get('idle_time', 0),
                activity_data.get('app_name', 'Unknown')
            ]
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
    
    def log_fatigue(self, user_id: int, fatigue_data: Dict) -> bool:
        """Log fatigue detection with improved error handling"""
        try:
            query = """
                INSERT INTO FatigueDetection
                (UserID, FatigueScore, EyeStrainLevel, BlinkRate, PostureScore, FacialExpression, WebcamDataUsed, AlertGenerated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = [
                user_id,
                fatigue_data.get('fatigue_score', 0),
                fatigue_data.get('eye_strain_level', 0),
                fatigue_data.get('blink_rate', 0),
                fatigue_data.get('posture_score', 0),
                fatigue_data.get('facial_expression', 'neutral'),
                fatigue_data.get('webcam_data_used', False),
                fatigue_data.get('alert_generated', False)
            ]
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error logging fatigue: {e}")
            return False
    
    def log_break(self, user_id: int, break_data: Dict) -> bool:
        """Log break record with improved error handling"""
        try:
            query = """
                INSERT INTO BreakRecords
                (UserID, BreakDuration, BreakType, Reason, ComplianceStatus)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = [
                user_id,
                break_data.get('duration', 5),
                break_data.get('break_type', 'micro'),
                break_data.get('reason', 'Scheduled'),
                break_data.get('compliance_status', 'Pending')
            ]
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error logging break: {e}")
            return False
    
    def update_break_status(self, break_id: int, status: str) -> bool:
        """Update compliance status of a break"""
        try:
            query = "UPDATE BreakRecords SET ComplianceStatus = %s WHERE BreakID = %s"
            return bool(self.execute_query(query, [status, break_id]))
        except Exception as e:
            logger.error(f"Error updating break status: {e}")
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email with improved error handling"""
        try:
            query = "SELECT * FROM Users WHERE Email = %s"
            return self.fetch_one(query, [email])
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def create_user(self, username: str, email: str, password_hash: str) -> bool:
        """Create new user with improved error handling"""
        try:
            query = """
                INSERT INTO Users (Username, Email, PasswordHash, CreatedAt)
                VALUES (%s, %s, %s, NOW())
            """
            return self.execute_query(query, [username, email, password_hash])
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def get_daily_analytics(self, user_id: int, date_str: str) -> Optional[Dict]:
        """Get daily analytics with improved error handling"""
        try:
            query = """
                SELECT * FROM ProductivityAnalytics
                WHERE UserID = %s AND Date = %s
            """
            return self.fetch_one(query, [user_id, date_str])
        except Exception as e:
            logger.error(f"Error getting daily analytics: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    return True
                finally:
                    cursor.close()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_pool_stats(self) -> Dict:
        """Get connection pool statistics"""
        try:
            if not self.connection_pool or not self.is_initialized:
                return {"status": "not_initialized"}
            
            return {
                "status": "healthy" if self.is_initialized else "unhealthy",
                "pool_name": "ai_microbreak_pool",
                "pool_size": 10,
                "is_initialized": self.is_initialized
            }
        except Exception as e:
            logger.warning(f"Error getting pool stats: {e}")
            return {"status": "error", "error": str(e), "is_initialized": self.is_initialized}


# Global instance
db_manager = None


def get_database_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
