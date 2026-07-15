import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime

class DBManager:
    """
    OOP Database Manager for SQLite operations, including user authentication,
    dashboard query abstractions, and activity logging.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "executive_dashboard.db")
        self.db_path = db_path
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        """Returns a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes the database using the schema.sql file if schema is empty."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            cursor.executescript(schema_sql)
            conn.commit()
        
        conn.close()
        
        # Seed default users
        self.seed_default_users()

    def hash_password(self, password: str) -> str:
        """Hashes a password using SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def seed_default_users(self):
        """Seeds default demonstration users into the database if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        default_users = [
            ("ceo", "ceo123", "CEO", "Aarav Sharma", "ceo@company.com"),
            ("admin", "admin123", "Executive Admin", "Neha Verma", "admin@company.com"),
            ("viewer", "viewer123", "Viewer", "Rohan Gupta", "viewer@company.com")
        ]
        
        for username, password, role, full_name, email in default_users:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                password_hash = self.hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
                    (username, password_hash, role, full_name, email)
                )
                conn.commit()
                self.log_action("SYSTEM", "SEED_USER", f"Seeded user '{username}' with role '{role}'")
        
        conn.close()

    def authenticate_user(self, username, password):
        """
        Authenticates a user against SQLite.
        Returns user details dict if successful, None otherwise.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT username, role, full_name, email FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user_info = {
                "username": row["username"],
                "role": row["role"],
                "full_name": row["full_name"],
                "email": row["email"]
            }
            self.log_action(username, "LOGIN", "User logged in successfully")
            return user_info
        else:
            self.log_action(username or "ANONYMOUS", "LOGIN_FAILED", "Authentication failed")
            return None

    def add_user(self, username, password, role, full_name, email, operator="SYSTEM"):
        """Adds a new user to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, role, full_name, email)
            )
            conn.commit()
            self.log_action(operator, "CREATE_USER", f"Created user '{username}' with role '{role}'")
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_users(self):
        """Retrieves list of users for display."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT id, username, role, full_name, email FROM users", conn)
        conn.close()
        return df

    def log_action(self, username: str, action: str, details: str):
        """Logs an event to the audit_logs table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        username_val = username or "UNKNOWN"
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, username, action, details) VALUES (?, ?, ?, ?)",
            (timestamp, username_val, action, details)
        )
        conn.commit()
        conn.close()

    def get_audit_logs(self, limit: int = 100):
        """Retrieves recent audit logs."""
        conn = self.get_connection()
        df = pd.read_sql_query(
            f"SELECT timestamp, username, action, details FROM audit_logs ORDER BY timestamp DESC LIMIT {limit}",
            conn
        )
        conn.close()
        return df

    def get_table_dataframe(self, table_name: str) -> pd.DataFrame:
        """Retrieves an entire table as a Pandas DataFrame."""
        conn = self.get_connection()
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df

    def insert_dataframe(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        """Inserts a pandas DataFrame into a database table."""
        conn = self.get_connection()
        df.to_sql(table_name, conn, if_exists=mode, index=False)
        conn.close()

    def save_wbr_report(self, report_text: str, author: str):
        """Saves a generated WBR report into the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        generated_at = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO wbr_reports (generated_at, report_text, author) VALUES (?, ?, ?)",
            (generated_at, report_text, author)
        )
        conn.commit()
        conn.close()
        self.log_action(author, "GENERATE_WBR", "Generated weekly business review report")

    def get_wbr_reports(self, limit: int = 10):
        """Retrieves historically generated WBR reports."""
        conn = self.get_connection()
        df = pd.read_sql_query(
            f"SELECT id, generated_at, report_text, author FROM wbr_reports ORDER BY generated_at DESC LIMIT {limit}",
            conn
        )
        conn.close()
        return df
