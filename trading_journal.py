"""
Trading Journal Module for PropFire
Professional trading journal with calendar view and SQLite persistence
"""

import customtkinter as ctk
import sqlite3
import calendar
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio
import threading

@dataclass
class DailyEntry:
    """Daily trading entry model"""
    date: datetime.date
    pnl: float
    gross: float = 0.0
    fees: float = 0.0
    notes: str = ""

class JournalRepository:
    """Data access layer for trading journal"""
    
    def __init__(self, db_path: str = "trading_journal.db"):
        self.db_path = db_path
        self._init_db()
        self._cache = {}
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_entries (
                    date TEXT PRIMARY KEY,
                    pnl REAL NOT NULL,
                    gross REAL DEFAULT 0,
                    fees REAL DEFAULT 0,
                    notes TEXT DEFAULT ''
                )
            """)
            conn.commit()
    
    def get_monthly_pnl(self, year: int, month: int) -> List[DailyEntry]:
        """Get all entries for a specific month"""
        cache_key = f"{year}-{month:02d}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date, pnl, gross, fees, notes 
                FROM daily_entries 
                WHERE date LIKE ? 
                ORDER BY date
            """, (f"{year}-{month:02d}%",))
            
            entries = [
                DailyEntry(
                    date=datetime.datetime.strptime(row[0], "%Y-%m-%d").date(),
                    pnl=row[1],
                    gross=row[2],
                    fees=row[3],
                    notes=row[4]
                )
                for row in cursor.fetchall()
            ]
            
        self._cache[cache_key] = entries
        return entries
    
    def update_daily_pnl(self, date: datetime.date, pnl: float, gross: float = 0, fees: float = 0, notes: str = ""):
        """Update or insert daily PnL entry"""
        date_str = date.strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO daily_entries (date, pnl, gross, fees, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (date_str, pnl, gross, fees, notes))
            conn.commit()
        
        # Clear cache for affected month
        cache_key = f"{date.year}-{date.month:02d}"
        self._cache.pop(cache_key, None)

class JournalService:
    """Business logic layer for trading journal"""
    
    def __init__(self, repository: JournalRepository):
        self.repository = repository
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Get monthly PnL summary"""
        entries = self.repository.get_monthly_pnl(year, month)
        total_pnl = sum(entry.pnl for entry in entries)
        
        return {
            "total_pnl": total_pnl,
            "entries": {entry.date.day: entry for entry in entries},
            "trading_days": len([e for e in entries if e.pnl != 0])
        }

class TradingJournalWindow:
    """Trading Journal UI - Calendar View"""
    
    def __init__(self, parent_callback=None):
        self.parent_callback = parent_callback
        self.service = JournalService(JournalRepository())
        self.current_date = datetime.date.today()
        self.journal_window = None
        self.day_cells = {}
        
    def show(self):
        """Display trading journal window"""
        if self.journal_window and self.journal_window.winfo_exists():
            self.journal_window.lift()
            return
            
        self.journal_window = ctk.CTkToplevel()
        self.journal_window.title("PropFire - Trading Journal")
        self.journal_window.geometry("800x600+200+100")
        self.journal_window.configure(fg_color="#000000")
        
        self._create_widgets()
        self._load_month_data()
        
    def _create_widgets(self):
        """Create journal UI components"""
        # Header with navigation
        header_frame = ctk.CTkFrame(self.journal_window, fg_color="#111111")
        header_frame.pack(fill='x', padx=10, pady=10)
        
        # Month navigation
        nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_frame.pack(fill='x', pady=5)
        
        prev_btn = ctk.CTkButton(nav_frame, text="◀", width=40, height=30,
                                command=self._prev_month, fg_color="#333333")
        prev_btn.pack(side='left')
        
        self.month_label = ctk.CTkLabel(nav_frame, 
                                       text=f"{calendar.month_name[self.current_date.month]} {self.current_date.year}",
                                       font=('Inter', 18, 'bold'), text_color='#ffffff')
        self.month_label.pack(side='left', expand=True)
        
        next_btn = ctk.CTkButton(nav_frame, text="▶", width=40, height=30,
                                command=self._next_month, fg_color="#333333")
        next_btn.pack(side='right')
        
        # Monthly PnL total
        self.total_label = ctk.CTkLabel(header_frame, text="Total PnL: $0.00",
                                       font=('Inter', 16, 'bold'), text_color='#00FF00')
        self.total_label.pack(pady=5)
        
        # Calendar grid
        self.calendar_frame = ctk.CTkFrame(self.journal_window, fg_color="#000000")
        self.calendar_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Configure grid
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1, uniform="col")
        for i in range(7):  # 6 weeks + header
            self.calendar_frame.grid_rowconfigure(i, weight=1, uniform="row")
        
        # Weekday headers
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(weekdays):
            label = ctk.CTkLabel(self.calendar_frame, text=day,
                               font=('Inter', 12, 'bold'), text_color='#888888')
            label.grid(row=0, column=i, padx=1, pady=1, sticky='nsew')
        
        # Create day cells
        self._create_calendar_grid()
        
        # Close button
        close_btn = ctk.CTkButton(self.journal_window, text="Close",
                                 command=self._close_journal, fg_color="#ff6b35")
        close_btn.pack(pady=10)
    
    def _create_calendar_grid(self):
        """Create calendar day cells"""
        self.day_cells.clear()
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                    
                # Create day cell
                cell = ctk.CTkFrame(self.calendar_frame, fg_color="#111111", 
                                  corner_radius=5, border_width=1, border_color="#333333")
                cell.grid(row=week_num, column=day_num, padx=2, pady=2, sticky='nsew')
                
                # Day number
                day_label = ctk.CTkLabel(cell, text=str(day),
                                       font=('Inter', 12, 'bold'), text_color='#ffffff')
                day_label.pack(anchor='nw', padx=5, pady=2)
                
                # PnL placeholder
                pnl_label = ctk.CTkLabel(cell, text="$0.00",
                                       font=('Courier', 10), text_color='#666666')
                pnl_label.pack(anchor='w', padx=5)
                
                # Store cell reference
                cell_date = datetime.date(self.current_date.year, self.current_date.month, day)
                self.day_cells[cell_date] = {
                    'frame': cell,
                    'pnl_label': pnl_label
                }
                
                # Bind click event
                cell.bind("<Button-1>", lambda e, d=cell_date: self._edit_day(d))
                day_label.bind("<Button-1>", lambda e, d=cell_date: self._edit_day(d))
    
    def _load_month_data(self):
        """Load and display month data"""
        def load_data():
            summary = self.service.get_monthly_summary(
                self.current_date.year, self.current_date.month
            )
            
            # Update UI in main thread
            self.journal_window.after(0, lambda: self._update_calendar_display(summary))
        
        # Load data in background thread
        threading.Thread(target=load_data, daemon=True).start()
    
    def _update_calendar_display(self, summary: Dict):
        """Update calendar with PnL data"""
        # Update total
        total_pnl = summary['total_pnl']
        color = '#00FF00' if total_pnl > 0 else '#FF4444' if total_pnl < 0 else '#888888'
        self.total_label.configure(text=f"Total PnL: ${total_pnl:,.2f}", text_color=color)
        
        # Update day cells
        entries = summary['entries']
        for cell_date, cell_data in self.day_cells.items():
            if cell_date.day in entries:
                entry = entries[cell_date.day]
                pnl_text = f"${entry.pnl:,.0f}" if abs(entry.pnl) >= 1 else f"${entry.pnl:.2f}"
                pnl_color = '#00FF00' if entry.pnl > 0 else '#FF4444' if entry.pnl < 0 else '#666666'
                cell_data['pnl_label'].configure(text=pnl_text, text_color=pnl_color)
    
    def _prev_month(self):
        """Navigate to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self._refresh_calendar()
    
    def _next_month(self):
        """Navigate to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self._refresh_calendar()
    
    def _refresh_calendar(self):
        """Refresh calendar display"""
        # Clear existing cells
        for widget in self.calendar_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:  # Keep headers
                widget.destroy()
        
        # Update month label
        self.month_label.configure(text=f"{calendar.month_name[self.current_date.month]} {self.current_date.year}")
        
        # Recreate calendar
        self._create_calendar_grid()
        self._load_month_data()
    
    def _edit_day(self, date: datetime.date):
        """Open day edit dialog"""
        EditDayDialog(date, self.service, self._refresh_calendar)
    
    def _close_journal(self):
        """Close journal window"""
        if self.journal_window:
            self.journal_window.destroy()
        if self.parent_callback:
            self.parent_callback()

class EditDayDialog:
    """Dialog for editing daily PnL entry"""
    
    def __init__(self, date: datetime.date, service: JournalService, refresh_callback):
        self.date = date
        self.service = service
        self.refresh_callback = refresh_callback
        
        # Get existing entry
        entries = service.get_monthly_summary(date.year, date.month)['entries']
        self.entry = entries.get(date.day, DailyEntry(date=date, pnl=0.0))
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create edit dialog"""
        self.dialog = ctk.CTkToplevel()
        self.dialog.title(f"Edit {self.date.strftime('%B %d, %Y')}")
        self.dialog.geometry("300x250+400+300")
        self.dialog.configure(fg_color="#111111")
        self.dialog.grab_set()
        
        # PnL input
        ctk.CTkLabel(self.dialog, text="Daily PnL ($):", 
                    font=('Inter', 12, 'bold')).pack(pady=10)
        
        self.pnl_entry = ctk.CTkEntry(self.dialog, width=200, font=('Courier', 12))
        self.pnl_entry.pack(pady=5)
        self.pnl_entry.insert(0, str(self.entry.pnl))
        
        # Notes
        ctk.CTkLabel(self.dialog, text="Notes:", 
                    font=('Inter', 12, 'bold')).pack(pady=(20, 5))
        
        self.notes_entry = ctk.CTkTextbox(self.dialog, width=250, height=80)
        self.notes_entry.pack(pady=5)
        self.notes_entry.insert("1.0", self.entry.notes)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(btn_frame, text="Save", command=self._save_entry,
                               fg_color="#00AA00", width=80)
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.dialog.destroy,
                                 fg_color="#666666", width=80)
        cancel_btn.pack(side='left', padx=5)
    
    def _save_entry(self):
        """Save PnL entry"""
        try:
            pnl = float(self.pnl_entry.get() or "0")
            notes = self.notes_entry.get("1.0", "end-1c")
            
            self.service.repository.update_daily_pnl(
                self.date, pnl, notes=notes
            )
            
            self.dialog.destroy()
            self.refresh_callback()
            
        except ValueError:
            # Show error - simplified for minimal implementation
            pass