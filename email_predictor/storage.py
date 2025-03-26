import os
import csv
import sqlite3
from collections import defaultdict

class Storage:
    """Simple storage for email patterns using SQLite."""
    
    def __init__(self, db_path="email_patterns.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Create the database if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS domain_patterns (
            id INTEGER PRIMARY KEY,
            domain TEXT,
            pattern TEXT,
            count INTEGER DEFAULT 1,
            UNIQUE(domain, pattern)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_pattern(self, domain, pattern):
        """Add or update a pattern for a domain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO domain_patterns (domain, pattern, count)
        VALUES (?, ?, 1)
        ON CONFLICT(domain, pattern) 
        DO UPDATE SET count = count + 1
        ''', (domain.lower(), pattern))
        
        conn.commit()
        conn.close()
    
    def get_domain_patterns(self, domain):
        """Get patterns for a specific domain with their counts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT pattern, count FROM domain_patterns
        WHERE domain = ?
        ORDER BY count DESC
        ''', (domain.lower(),))
        
        patterns = cursor.fetchall()
        conn.close()
        
        return patterns
    
    def import_from_csv(self, csv_path):
        """Import known email patterns from a CSV file."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header row
            
            for row in reader:
                if len(row) >= 3:  # Expecting: first_name, last_name, email
                    first_name, last_name, email = row[0].lower(), row[1].lower(), row[2].lower()
                    
                    if '@' in email:
                        domain = email.split('@')[1]
                        pattern = self._detect_pattern(first_name, last_name, email)
                        if pattern:
                            self.add_pattern(domain, pattern)
    
    def _detect_pattern(self, first_name, last_name, email):
        """Detect the pattern used in an email address."""
        local_part = email.split('@')[0]
        
        patterns = {
            f"{first_name}.{last_name}": "{first}.{last}@{domain}",
            f"{first_name}{last_name}": "{first}{last}@{domain}",
            f"{first_name}_{last_name}": "{first}_{last}@{domain}",
            f"{first_name[0]}.{last_name}": "{f}.{last}@{domain}",
            f"{first_name[0]}{last_name}": "{flast}@{domain}",
            f"{first_name}.{last_name[0]}": "{first}.{l}@{domain}",
            f"{first_name}{last_name[0]}": "{firstl}@{domain}",
            f"{first_name}": "{first}@{domain}",
            f"{last_name}": "{last}@{domain}"
        }
        
        for key, pattern in patterns.items():
            if local_part == key:
                return pattern
                
        return None 