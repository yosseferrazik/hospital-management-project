import sys
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import hash_password, verify_password
from db import postgres as db
from db.cache import cache

class LoginAttemptTracker:
    def __init__(self):
        self.attempts = defaultdict(list)
        self.locked_until = {}
    
    def record_failed_attempt(self, username):
        """Record a failed login attempt"""
        now = datetime.now()
        
        # Clean old attempts (older than 5 minutes)
        self.attempts[username] = [
            attempt_time for attempt_time in self.attempts[username]
            if now - attempt_time < timedelta(minutes=5)
        ]
        
        # Add new attempt
        self.attempts[username].append(now)
        
        # Lock account if 5 or more attempts in last 5 minutes
        if len(self.attempts[username]) >= 5:
            self.locked_until[username] = now + timedelta(minutes=2)
    
    def is_locked(self, username):
        """Check if account is currently locked"""
        if username in self.locked_until:
            if datetime.now() < self.locked_until[username]:
                remaining = self.locked_until[username] - datetime.now()
                return True, int(remaining.total_seconds())
            else:
                # Lock expired, clear attempts
                del self.locked_until[username]
                self.attempts[username] = []
        return False, 0
    
    def get_remaining_attempts(self, username):
        """Get remaining attempts before lockout"""
        now = datetime.now()
        
        # Clean old attempts
        self.attempts[username] = [
            attempt_time for attempt_time in self.attempts[username]
            if now - attempt_time < timedelta(minutes=5)
        ]
        
        remaining = 5 - len(self.attempts[username])
        return max(0, remaining)
    
    def reset_attempts(self, username):
        """Reset attempts on successful login"""
        if username in self.attempts:
            self.attempts[username] = []
        if username in self.locked_until:
            del self.locked_until[username]

# Global login tracker instance
login_tracker = LoginAttemptTracker()

def login(username, password):
    """Authenticate user with rate limiting"""
    if not username or not password:
        return None, "Username and password are required"
    
    # Check if account is locked
    is_locked, remaining_seconds = login_tracker.is_locked(username)
    if is_locked:
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        if minutes > 0:
            msg = f"Too many failed attempts. Please wait {minutes} minute(s) and {seconds} second(s)"
        else:
            msg = f"Too many failed attempts. Please wait {seconds} second(s)"
        return None, msg
    
    cache_key = f"user:{username}"
    cached_user = cache.get(cache_key)
    
    if cached_user:
        login_tracker.reset_attempts(username)
        return cached_user, None
    
    query = """
        SELECT user_id, username, password_hash, role, staff_id, is_active
        FROM app_users 
        WHERE username = %s AND is_active = true
    """
    
    result = db.execute_query(query, (username,))
    
    if result:
        stored_hash = result[0][2]
        
        if verify_password(password, stored_hash):
            # Successful login - reset attempts
            login_tracker.reset_attempts(username)
            
            user = {
                'user_id': result[0][0],
                'username': result[0][1],
                'role': result[0][3],
                'staff_id': result[0][4],
                'is_active': result[0][5]
            }
            
            db.execute_query(
                "UPDATE app_users SET last_login = CURRENT_TIMESTAMP WHERE username = %s",
                (username,)
            )
            
            cache.set(cache_key, user, ttl=3600)
            return user, None
        else:
            # Failed login - record attempt
            login_tracker.record_failed_attempt(username)
            remaining = login_tracker.get_remaining_attempts(username)
            
            if remaining > 0:
                msg = f"Invalid password. {remaining} attempt(s) remaining before 2-minute lockout"
            else:
                msg = "Maximum attempts reached. Account locked for 2 minutes"
            
            return None, msg
    else:
        # User doesn't exist - still record attempt to prevent enumeration
        login_tracker.record_failed_attempt(username)
        remaining = login_tracker.get_remaining_attempts(username)
        
        if remaining > 0:
            msg = f"Invalid username or password. {remaining} attempt(s) remaining before 2-minute lockout"
        else:
            msg = "Maximum attempts reached. Please wait 2 minutes before trying again"
        
        return None, msg

def register(username, password, role, staff_id):
    """Register a new user"""
    if not username or not password:
        return False, "Username and password are required"
    
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    
    check_query = "SELECT user_id FROM app_users WHERE username = %s"
    existing = db.execute_query(check_query, (username,))
    
    if existing:
        return False, "Username already exists"
    
    staff_check = "SELECT staff_id FROM staff WHERE staff_id = %s"
    staff_exists = db.execute_query(staff_check, (staff_id,))
    
    if not staff_exists:
        return False, "Staff ID not found"
    
    user_check = "SELECT user_id FROM app_users WHERE staff_id = %s"
    user_exists = db.execute_query(user_check, (staff_id,))
    
    if user_exists:
        return False, "User already exists for this staff member"
    
    hashed_pw = hash_password(password)
    
    insert_query = """
        INSERT INTO app_users (username, password_hash, staff_id, role)
        VALUES (%s, %s, %s, %s)
    """
    
    try:
        db.execute_query(insert_query, (username, hashed_pw, staff_id, role))
        db.connection.commit()
        return True, "User registered successfully"
    except Exception as e:
        db.connection.rollback()
        return False, f"Registration failed: {str(e)}"

def get_login_status(username):
    """Get current login status for a user"""
    is_locked, remaining = login_tracker.is_locked(username)
    remaining_attempts = login_tracker.get_remaining_attempts(username)
    
    return {
        'is_locked': is_locked,
        'lock_remaining_seconds': remaining if is_locked else 0,
        'remaining_attempts': remaining_attempts,
        'total_attempts': len(login_tracker.attempts.get(username, []))
    }