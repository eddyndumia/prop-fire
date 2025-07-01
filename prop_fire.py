import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os
from typing import Dict, List, Optional, Tuple

class PropFireApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.load_settings()
        self.setup_data()
        self.create_widgets()
        self.update_timer()
        
    def setup_window(self):
        """Configure main window properties"""
        self.root.title("Prop Fire - Trade Timer")
        self.root.geometry("400x500+50+50")  # Position at top-left
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)  # Keep on top
        self.root.configure(bg='#1a1a1a')
        
    def load_settings(self):
        """Load user preferences from file"""
        self.settings_file = "propfire_settings.json"
        default_settings = {
            "currency": "USD",
            "prop_firm": "FTMO",
            "day": "Tuesday",
            "session": "London",
            "dark_mode": True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = default_settings
        except:
            self.settings = default_settings
            
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except:
            pass
            
    def setup_data(self):
        """Initialize prop firm rules and mock news data"""
        # Prop firm trading restrictions (minutes before/after news)
        self.prop_firms = {
            "FTMO": {"before": 2, "after": 2},
            "MyForexFunds": {"before": 5, "after": 5},
            "The5ers": {"before": 3, "after": 3},
            "FundedNext": {"before": 2, "after": 3}
        }
        
        # Trading sessions (UTC times)
        self.sessions = {
            "Asia": {"start": "00:00", "end": "09:00"},
            "London": {"start": "08:00", "end": "17:00"},
            "New York": {"start": "13:00", "end": "22:00"}
        }
        
        # Mock high-impact news events (would normally fetch from API)
        self.mock_news = self.generate_mock_news()
        
    def generate_mock_news(self) -> List[Dict]:
        """Generate sample news events for demonstration"""
        today = datetime.datetime.now()
        news_events = []
        
        # Sample news for different currencies and days
        sample_events = [
            {"currency": "USD", "name": "FOMC Meeting", "impact": "high", "time": "14:00"},
            {"currency": "USD", "name": "NFP Release", "impact": "high", "time": "12:30"},
            {"currency": "EUR", "name": "ECB Rate Decision", "impact": "high", "time": "11:45"},
            {"currency": "GBP", "name": "BOE Meeting", "impact": "high", "time": "12:00"},
            {"currency": "JPY", "name": "BOJ Statement", "impact": "high", "time": "03:00"}
        ]
        
        # Generate events for the next 7 days
        for i in range(7):
            event_date = today + datetime.timedelta(days=i)
            for event in sample_events:
                if event_date.weekday() < 5:  # Weekdays only
                    news_events.append({
                        "date": event_date.strftime("%Y-%m-%d"),
                        "time": event["time"],
                        "currency": event["currency"],
                        "name": event["name"],
                        "impact": event["impact"]
                    })
        
        return news_events
        
    def create_widgets(self):
        """Create and arrange GUI elements"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a1a')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = tk.Label(header_frame, text="🔥 PROP FIRE", 
                              font=('Arial', 18, 'bold'), 
                              fg='#ff6b35', bg='#1a1a1a')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Trade Timer & News Tracker", 
                                 font=('Arial', 10), 
                                 fg='#888888', bg='#1a1a1a')
        subtitle_label.pack()
        
        # Settings Frame
        settings_frame = tk.LabelFrame(self.root, text="Trading Setup", 
                                      font=('Arial', 10, 'bold'),
                                      fg='#ffffff', bg='#2a2a2a', bd=1)
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Currency selection
        tk.Label(settings_frame, text="Currency:", fg='#ffffff', bg='#2a2a2a').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.currency_var = tk.StringVar(value=self.settings["currency"])
        currency_combo = ttk.Combobox(settings_frame, textvariable=self.currency_var, 
                                     values=["USD", "EUR", "GBP", "JPY", "AUD", "CAD"], 
                                     state="readonly", width=15)
        currency_combo.grid(row=0, column=1, padx=5, pady=5)
        currency_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        
        # Prop firm selection
        tk.Label(settings_frame, text="Prop Firm:", fg='#ffffff', bg='#2a2a2a').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.firm_var = tk.StringVar(value=self.settings["prop_firm"])
        firm_combo = ttk.Combobox(settings_frame, textvariable=self.firm_var, 
                                 values=list(self.prop_firms.keys()), 
                                 state="readonly", width=15)
        firm_combo.grid(row=1, column=1, padx=5, pady=5)
        firm_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        
        # Day selection
        tk.Label(settings_frame, text="Day:", fg='#ffffff', bg='#2a2a2a').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.day_var = tk.StringVar(value=self.settings["day"])
        day_combo = ttk.Combobox(settings_frame, textvariable=self.day_var, 
                                values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], 
                                state="readonly", width=15)
        day_combo.grid(row=2, column=1, padx=5, pady=5)
        day_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        
        # Session selection
        tk.Label(settings_frame, text="Session:", fg='#ffffff', bg='#2a2a2a').grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.session_var = tk.StringVar(value=self.settings["session"])
        session_combo = ttk.Combobox(settings_frame, textvariable=self.session_var, 
                                    values=list(self.sessions.keys()), 
                                    state="readonly", width=15)
        session_combo.grid(row=3, column=1, padx=5, pady=5)
        session_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        
        # Status Frame
        status_frame = tk.LabelFrame(self.root, text="Current Status", 
                                    font=('Arial', 10, 'bold'),
                                    fg='#ffffff', bg='#2a2a2a', bd=1)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = tk.Label(status_frame, text="Calculating...", 
                                    font=('Arial', 12, 'bold'), 
                                    fg='#00ff00', bg='#2a2a2a')
        self.status_label.pack(pady=10)
        
        # Timer Frame
        timer_frame = tk.LabelFrame(self.root, text="Countdown Timer", 
                                   font=('Arial', 10, 'bold'),
                                   fg='#ffffff', bg='#2a2a2a', bd=1)
        timer_frame.pack(fill='x', padx=20, pady=10)
        
        self.timer_label = tk.Label(timer_frame, text="00:00:00", 
                                   font=('Arial', 24, 'bold'), 
                                   fg='#ff6b35', bg='#2a2a2a')
        self.timer_label.pack(pady=15)
        
        # News Frame
        news_frame = tk.LabelFrame(self.root, text="Next News Event", 
                                  font=('Arial', 10, 'bold'),
                                  fg='#ffffff', bg='#2a2a2a', bd=1)
        news_frame.pack(fill='x', padx=20, pady=10)
        
        self.news_label = tk.Label(news_frame, text="No upcoming news", 
                                  font=('Arial', 10), 
                                  fg='#ffffff', bg='#2a2a2a', 
                                  wraplength=350, justify='center')
        self.news_label.pack(pady=10)
        
        # Motivation Frame
        motivation_frame = tk.Frame(self.root, bg='#1a1a1a')
        motivation_frame.pack(fill='x', padx=20, pady=10)
        
        motivation_label = tk.Label(motivation_frame, 
                                   text="💪 Trade with discipline — consistency builds equity.", 
                                   font=('Arial', 9, 'italic'), 
                                   fg='#888888', bg='#1a1a1a',
                                   wraplength=350, justify='center')
        motivation_label.pack()
        
    def on_setting_change(self, event=None):
        """Handle setting changes"""
        self.settings["currency"] = self.currency_var.get()
        self.settings["prop_firm"] = self.firm_var.get()
        self.settings["day"] = self.day_var.get()
        self.settings["session"] = self.session_var.get()
        self.save_settings()
        
    def get_next_news_event(self) -> Optional[Dict]:
        """Find the next relevant news event"""
        now = datetime.datetime.now()
        target_day = self.settings["day"]
        target_currency = self.settings["currency"]
        
        # Convert day name to weekday number
        day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        target_weekday = day_map[target_day]
        
        # Find next occurrence of target day
        days_ahead = target_weekday - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        target_date = now + datetime.timedelta(days=days_ahead)
        
        # Find news events for that day and currency
        relevant_events = []
        for event in self.mock_news:
            event_date = datetime.datetime.strptime(event["date"], "%Y-%m-%d")
            if (event_date.date() == target_date.date() and 
                event["currency"] == target_currency and
                event["impact"] == "high"):
                
                event_time = datetime.datetime.strptime(f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M")
                if self.is_in_session(event_time):
                    relevant_events.append({
                        "datetime": event_time,
                        "name": event["name"],
                        "currency": event["currency"]
                    })
        
        # Return the earliest event
        if relevant_events:
            return min(relevant_events, key=lambda x: x["datetime"])
        return None
        
    def is_in_session(self, event_time: datetime.datetime) -> bool:
        """Check if event time falls within selected session"""
        session = self.sessions[self.settings["session"]]
        start_time = datetime.datetime.strptime(session["start"], "%H:%M").time()
        end_time = datetime.datetime.strptime(session["end"], "%H:%M").time()
        
        return start_time <= event_time.time() <= end_time
        
    def calculate_next_trade_time(self) -> Tuple[datetime.datetime, str]:
        """Calculate when next trade opportunity is available"""
        now = datetime.datetime.now()
        next_event = self.get_next_news_event()
        
        if next_event:
            # Apply prop firm restrictions
            firm_rules = self.prop_firms[self.settings["prop_firm"]]
            news_time = next_event["datetime"]
            
            # Calculate blocked window
            block_start = news_time - datetime.timedelta(minutes=firm_rules["before"])
            block_end = news_time + datetime.timedelta(minutes=firm_rules["after"])
            
            # If we're before the block, trade until block starts
            if now < block_start:
                return block_start, f"Trading blocked before {next_event['name']}"
            # If we're in the block, wait until it ends
            elif now <= block_end:
                return block_end, f"Waiting for {next_event['name']} restriction to end"
            else:
                # Find next session start
                return self.get_next_session_start(), "Waiting for next session"
        else:
            # No news events, wait for session start
            return self.get_next_session_start(), "Waiting for session to begin"
            
    def get_next_session_start(self) -> datetime.datetime:
        """Get the next session start time"""
        now = datetime.datetime.now()
        session = self.sessions[self.settings["session"]]
        
        # Try today first
        today_start = datetime.datetime.combine(now.date(), 
                                               datetime.datetime.strptime(session["start"], "%H:%M").time())
        
        if now < today_start:
            return today_start
        else:
            # Next day
            tomorrow = now + datetime.timedelta(days=1)
            return datetime.datetime.combine(tomorrow.date(), 
                                           datetime.datetime.strptime(session["start"], "%H:%M").time())
            
    def update_timer(self):
        """Update countdown timer and status"""
        try:
            next_trade_time, status_message = self.calculate_next_trade_time()
            now = datetime.datetime.now()
            
            # Calculate time difference
            time_diff = next_trade_time - now
            
            if time_diff.total_seconds() > 0:
                hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                # Update status color based on time remaining
                if time_diff.total_seconds() < 300:  # Less than 5 minutes
                    timer_color = '#ff4444'
                elif time_diff.total_seconds() < 900:  # Less than 15 minutes
                    timer_color = '#ffaa00'
                else:
                    timer_color = '#00ff00'
                    
                self.timer_label.config(text=timer_text, fg=timer_color)
                self.status_label.config(text=status_message, fg='#ffaa00')
            else:
                self.timer_label.config(text="TRADE NOW", fg='#00ff00')
                self.status_label.config(text="Session Active - No Restrictions", fg='#00ff00')
                
            # Update news information
            next_event = self.get_next_news_event()
            if next_event:
                news_text = f"{next_event['name']}\n{next_event['datetime'].strftime('%Y-%m-%d %H:%M UTC')}"
                self.news_label.config(text=news_text)
            else:
                self.news_label.config(text="No high-impact news scheduled")
                
        except Exception as e:
            self.timer_label.config(text="ERROR", fg='#ff4444')
            self.status_label.config(text="Calculation error", fg='#ff4444')
            
        # Schedule next update
        self.root.after(1000, self.update_timer)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PropFireApp()
    app.run()