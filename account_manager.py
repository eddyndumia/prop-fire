"""
Account Management Module for PropFire
Handles account setup, equity tracking, and persistence
"""

import json
import sqlite3
import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class EquityPoint:
    """Single equity curve data point"""
    date: datetime.date
    equity: float
    pnl: float

class AccountRepository:
    """Data access layer for account and equity data"""
    
    def __init__(self, db_path: str = "propfire_account.db"):
        self.db_path = db_path
        self.config_file = "account_config.json"
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS equity_curve (
                    date TEXT PRIMARY KEY,
                    equity REAL NOT NULL,
                    pnl REAL DEFAULT 0
                )
            """)
            conn.commit()
    
    def get_starting_balance(self) -> Optional[float]:
        """Get starting balance from config"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('starting_balance')
        except:
            return None
    
    def set_starting_balance(self, balance: float):
        """Set starting balance and clear existing data"""
        config = {'starting_balance': balance}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        
        # Clear existing equity data
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM equity_curve")
            conn.commit()
    
    def get_equity_curve(self) -> List[EquityPoint]:
        """Get equity curve data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date, equity, pnl FROM equity_curve 
                ORDER BY date
            """)
            return [
                EquityPoint(
                    date=datetime.datetime.strptime(row[0], "%Y-%m-%d").date(),
                    equity=row[1],
                    pnl=row[2]
                )
                for row in cursor.fetchall()
            ]
    
    def update_equity(self, date: datetime.date, pnl: float):
        """Update equity curve with new PnL"""
        starting_balance = self.get_starting_balance() or 10000.0
        
        # Get previous equity
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT equity FROM equity_curve 
                WHERE date < ? ORDER BY date DESC LIMIT 1
            """, (date.strftime("%Y-%m-%d"),))
            
            result = cursor.fetchone()
            prev_equity = result[0] if result else starting_balance
            new_equity = prev_equity + pnl
            
            # Insert or update
            conn.execute("""
                INSERT OR REPLACE INTO equity_curve (date, equity, pnl)
                VALUES (?, ?, ?)
            """, (date.strftime("%Y-%m-%d"), new_equity, pnl))
            conn.commit()

class AccountService:
    """Business logic for account management"""
    
    def __init__(self):
        self.repository = AccountRepository()
    
    def setup_account(self, starting_balance: float):
        """Setup new account with starting balance"""
        self.repository.set_starting_balance(starting_balance)
    
    def get_current_equity(self) -> float:
        """Get current account equity"""
        curve = self.repository.get_equity_curve()
        if not curve:
            return self.repository.get_starting_balance() or 10000.0
        return curve[-1].equity
    
    def get_equity_data(self) -> List[EquityPoint]:
        """Get equity curve for charting"""
        return self.repository.get_equity_curve()