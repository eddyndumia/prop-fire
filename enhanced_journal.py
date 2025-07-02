"""
Enhanced Trading Journal with image attachments and trade details
"""

import customtkinter as ctk
import sqlite3
import calendar
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional
from dataclasses import dataclass
import os
import shutil
from PIL import Image, ImageTk
from account_manager import AccountService

@dataclass
class TradeEntry:
    """Enhanced trade entry with full details"""
    date: datetime.date
    pnl: float
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    risk_reward: float = 0.0
    notes: str = ""
    chart_image: str = ""  # Path to image file

class EnhancedJournalRepository:
    """Enhanced repository with image support"""
    
    def __init__(self, db_path: str = "enhanced_journal.db"):
        self.db_path = db_path
        self.images_dir = "journal_images"
        os.makedirs(self.images_dir, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize enhanced database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_entries (
                    date TEXT PRIMARY KEY,
                    pnl REAL NOT NULL,
                    entry_price REAL DEFAULT 0,
                    stop_loss REAL DEFAULT 0,
                    take_profit REAL DEFAULT 0,
                    risk_reward REAL DEFAULT 0,
                    notes TEXT DEFAULT '',
                    chart_image TEXT DEFAULT ''
                )
            """)
            conn.commit()
    
    def get_trade_entry(self, date: datetime.date) -> Optional[TradeEntry]:
        """Get trade entry for specific date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM trade_entries WHERE date = ?
            """, (date.strftime("%Y-%m-%d"),))
            
            row = cursor.fetchone()
            if row:
                return TradeEntry(
                    date=datetime.datetime.strptime(row[0], "%Y-%m-%d").date(),
                    pnl=row[1],
                    entry_price=row[2],
                    stop_loss=row[3],
                    take_profit=row[4],
                    risk_reward=row[5],
                    notes=row[6],
                    chart_image=row[7]
                )
            return None
    
    def save_trade_entry(self, entry: TradeEntry):
        """Save trade entry with image"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO trade_entries 
                (date, pnl, entry_price, stop_loss, take_profit, risk_reward, notes, chart_image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.date.strftime("%Y-%m-%d"),
                entry.pnl,
                entry.entry_price,
                entry.stop_loss,
                entry.take_profit,
                entry.risk_reward,
                entry.notes,
                entry.chart_image
            ))
            conn.commit()
    
    def save_chart_image(self, date: datetime.date, image_path: str) -> str:
        """Save chart image and return stored path"""
        if not os.path.exists(image_path):
            return ""
        
        # Create unique filename
        ext = os.path.splitext(image_path)[1]
        filename = f"{date.strftime('%Y-%m-%d')}_chart{ext}"
        dest_path = os.path.join(self.images_dir, filename)
        
        # Copy image
        shutil.copy2(image_path, dest_path)
        return dest_path

class EnhancedJournalWindow:
    """Enhanced journal window with trade details and images"""
    
    def __init__(self):
        self.repository = EnhancedJournalRepository()
        self.account_service = AccountService()
        self.current_date = datetime.date.today()
        self.journal_window = None
    
    def show(self):
        """Display enhanced journal window"""
        if self.journal_window and self.journal_window.winfo_exists():
            self.journal_window.lift()
            return
            
        self.journal_window = ctk.CTkToplevel()
        self.journal_window.title("PropFire - Enhanced Trading Journal")
        self.journal_window.geometry("900x700+150+50")
        self.journal_window.configure(fg_color="#000000")
        self.journal_window.attributes('-topmost', True)
        
        self._create_widgets()
        self._load_month_data()
    
    def _create_widgets(self):
        """Create enhanced journal UI"""
        # Header with current equity
        header_frame = ctk.CTkFrame(self.journal_window, fg_color="#111111")
        header_frame.pack(fill='x', padx=10, pady=10)
        
        current_equity = self.account_service.get_current_equity()
        equity_label = ctk.CTkLabel(header_frame, 
                                   text=f"Current Equity: ${current_equity:,.2f}",
                                   font=('Inter', 16, 'bold'), text_color='#00FF00')
        equity_label.pack(pady=5)
        
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
        self.day_cells = {}
        self._create_calendar_grid()
        
        # Close button
        close_btn = ctk.CTkButton(self.journal_window, text="Close",
                                 command=self._close_journal, fg_color="#ff6b35")
        close_btn.pack(pady=10)
    
    def _create_calendar_grid(self):
        """Create calendar day cells"""
        # Clear existing day cells
        for widget in self.calendar_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:  # Keep headers
                widget.destroy()
        
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
    
    def _edit_day(self, date: datetime.date):
        """Open enhanced trade dialog for day"""
        from enhanced_journal import EnhancedTradeDialog
        EnhancedTradeDialog(date, self.repository, self.account_service)
    
    def _load_month_data(self):
        """Load and display month data"""
        # Load trade entries for the month
        for day in range(1, 32):
            try:
                cell_date = datetime.date(self.current_date.year, self.current_date.month, day)
                if cell_date in self.day_cells:
                    entry = self.repository.get_trade_entry(cell_date)
                    if entry and entry.pnl != 0:
                        pnl_text = f"${entry.pnl:,.0f}" if abs(entry.pnl) >= 1 else f"${entry.pnl:.2f}"
                        pnl_color = '#00FF00' if entry.pnl > 0 else '#FF4444' if entry.pnl < 0 else '#666666'
                        self.day_cells[cell_date]['pnl_label'].configure(text=pnl_text, text_color=pnl_color)
            except ValueError:
                break  # Invalid date
    
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
        self.month_label.configure(text=f"{calendar.month_name[self.current_date.month]} {self.current_date.year}")
        self._create_calendar_grid()
        self._load_month_data()
    
    def _close_journal(self):
        """Close journal window"""
        if self.journal_window:
            self.journal_window.destroy()

class EnhancedTradeDialog:
    """Enhanced trade entry dialog with image support"""
    
    def __init__(self, date: datetime.date, repository: EnhancedJournalRepository, account_service: AccountService):
        self.date = date
        self.repository = repository
        self.account_service = account_service
        self.entry = repository.get_trade_entry(date) or TradeEntry(date=date, pnl=0.0)
        self.image_path = ""
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create enhanced trade dialog"""
        self.dialog = ctk.CTkToplevel()
        self.dialog.title(f"Trade Entry - {self.date.strftime('%B %d, %Y')}")
        self.dialog.geometry("500x600+300+200")
        self.dialog.configure(fg_color="#111111")
        self.dialog.attributes('-topmost', True)
        self.dialog.grab_set()
        
        # Trade details frame
        details_frame = ctk.CTkFrame(self.dialog)
        details_frame.pack(fill='x', padx=20, pady=10)
        
        # Entry Price
        ctk.CTkLabel(details_frame, text="Entry Price:", font=('Inter', 12)).pack(anchor='w', pady=2)
        self.entry_price_var = ctk.StringVar(value=str(self.entry.entry_price))
        ctk.CTkEntry(details_frame, textvariable=self.entry_price_var, font=('Inter', 11)).pack(fill='x', pady=2)
        
        # Stop Loss
        ctk.CTkLabel(details_frame, text="Stop Loss:", font=('Inter', 12)).pack(anchor='w', pady=2)
        self.stop_loss_var = ctk.StringVar(value=str(self.entry.stop_loss))
        ctk.CTkEntry(details_frame, textvariable=self.stop_loss_var, font=('Inter', 11)).pack(fill='x', pady=2)
        
        # Take Profit
        ctk.CTkLabel(details_frame, text="Take Profit:", font=('Inter', 12)).pack(anchor='w', pady=2)
        self.take_profit_var = ctk.StringVar(value=str(self.entry.take_profit))
        ctk.CTkEntry(details_frame, textvariable=self.take_profit_var, font=('Inter', 11)).pack(fill='x', pady=2)
        
        # PnL
        ctk.CTkLabel(details_frame, text="Net PnL ($):", font=('Inter', 12)).pack(anchor='w', pady=2)
        self.pnl_var = ctk.StringVar(value=str(self.entry.pnl))
        ctk.CTkEntry(details_frame, textvariable=self.pnl_var, font=('Inter', 11)).pack(fill='x', pady=2)
        
        # Risk/Reward (calculated)
        self.rr_label = ctk.CTkLabel(details_frame, text=f"R/R: {self.entry.risk_reward:.2f}", 
                                    font=('Inter', 12), text_color='#00FF00')
        self.rr_label.pack(anchor='w', pady=5)
        
        # Image attachment
        image_frame = ctk.CTkFrame(self.dialog)
        image_frame.pack(fill='x', padx=20, pady=10)
        
        ctk.CTkButton(image_frame, text="📷 Attach Chart Image", 
                     command=self._attach_image, font=('Inter', 11)).pack(pady=5)
        
        # Save/Cancel buttons
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Save", command=self._save_entry,
                     fg_color="#00AA00", width=80, font=('Inter', 11)).pack(side='left', padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", command=self.dialog.destroy,
                     fg_color="#666666", width=80, font=('Inter', 11)).pack(side='left', padx=5)
    
    def _attach_image(self):
        """Attach chart image"""
        file_path = filedialog.askopenfilename(
            title="Select Chart Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.image_path = file_path
    
    def _calculate_rr(self) -> float:
        """Calculate risk/reward ratio"""
        try:
            entry = float(self.entry_price_var.get() or "0")
            stop = float(self.stop_loss_var.get() or "0")
            target = float(self.take_profit_var.get() or "0")
            
            if entry > 0 and stop > 0 and target > 0:
                risk = abs(entry - stop)
                reward = abs(target - entry)
                return reward / risk if risk > 0 else 0
        except:
            pass
        return 0.0
    
    def _save_entry(self):
        """Save enhanced trade entry"""
        try:
            # Calculate R/R
            rr = self._calculate_rr()
            
            # Create entry
            entry = TradeEntry(
                date=self.date,
                pnl=float(self.pnl_var.get() or "0"),
                entry_price=float(self.entry_price_var.get() or "0"),
                stop_loss=float(self.stop_loss_var.get() or "0"),
                take_profit=float(self.take_profit_var.get() or "0"),
                risk_reward=rr,
                chart_image=self.repository.save_chart_image(self.date, self.image_path) if self.image_path else ""
            )
            
            # Save to repository
            self.repository.save_trade_entry(entry)
            
            # Update equity curve
            self.account_service.repository.update_equity(self.date, entry.pnl)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")

class AccountSetupDialog:
    """Account setup dialog"""
    
    def __init__(self, account_service: AccountService, callback=None):
        self.account_service = account_service
        self.callback = callback
        self._create_dialog()
    
    def _create_dialog(self):
        """Create account setup dialog"""
        self.dialog = ctk.CTkToplevel()
        self.dialog.title("Account Setup")
        self.dialog.geometry("400x200+400+300")
        self.dialog.configure(fg_color="#111111")
        self.dialog.attributes('-topmost', True)
        self.dialog.grab_set()
        
        ctk.CTkLabel(self.dialog, text="Set Starting Balance", 
                    font=('Inter', 16, 'bold')).pack(pady=20)
        
        self.balance_var = ctk.StringVar(value="10000")
        balance_entry = ctk.CTkEntry(self.dialog, textvariable=self.balance_var, 
                                   font=('Inter', 14), width=200)
        balance_entry.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Set Balance", command=self._save_balance,
                     fg_color="#00AA00", font=('Inter', 12)).pack(side='left', padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", command=self.dialog.destroy,
                     fg_color="#666666", font=('Inter', 12)).pack(side='left', padx=5)
    
    def _save_balance(self):
        """Save starting balance"""
        try:
            balance = float(self.balance_var.get())
            self.account_service.setup_account(balance)
            self.dialog.destroy()
            if self.callback:
                self.callback()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")