import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os
from typing import Dict, List, Optional, Tuple
import threading
import time
from news_api import NewsAPI

class SplashScreen:
    def __init__(self, callback):
        self.callback = callback
        self.splash = tk.Tk()
        self.setup_splash()
        
    def setup_splash(self):
        """Configure splash screen"""
        self.splash.title("Prop Fire")
        self.splash.geometry("400x300+" + str(self.splash.winfo_screenwidth()//2 - 200) + "+" + str(self.splash.winfo_screenheight()//2 - 150))
        self.splash.configure(bg='#1a1a1a')
        self.splash.overrideredirect(True)  # Remove window decorations
        self.splash.attributes('-topmost', True)
        
        # Main title
        title_label = tk.Label(self.splash, text="🔥 PROP FIRE", 
                              font=('Arial', 32, 'bold'), 
                              fg='#ff6b35', bg='#1a1a1a')
        title_label.pack(expand=True)
        
        # Made by text
        made_by_label = tk.Label(self.splash, text="Made by traderndumia", 
                                font=('Arial', 12), 
                                fg='#888888', bg='#1a1a1a')
        made_by_label.pack(side='bottom', pady=20)
        
        # Auto-close after 3 seconds
        self.splash.after(3000, self.close_splash)
        
    def close_splash(self):
        """Close splash and open main app"""
        self.splash.destroy()
        self.callback()
        
    def show(self):
        """Display splash screen"""
        self.splash.mainloop()

class ConfigWindow:
    def __init__(self, settings, prop_firms, sessions, callback):
        self.settings = settings
        self.prop_firms = prop_firms
        self.sessions = sessions
        self.callback = callback
        self.config_window = tk.Tk()
        self.setup_config_window()
        self.create_config_widgets()
        
    def setup_config_window(self):
        """Configure config window properties"""
        self.config_window.title("Prop Fire - Configuration")
        self.config_window.geometry("400x350+" + str(self.config_window.winfo_screenwidth()//2 - 200) + "+" + str(self.config_window.winfo_screenheight()//2 - 175))
        self.config_window.resizable(False, False)
        self.config_window.configure(bg='#1a1a1a')
        
    def create_config_widgets(self):
        """Create configuration interface"""
        # Header
        header_frame = tk.Frame(self.config_window, bg='#1a1a1a')
        header_frame.pack(fill='x', padx=20, pady=15)
        
        title_label = tk.Label(header_frame, text="🔥 PROP FIRE", 
                              font=('Arial', 18, 'bold'), 
                              fg='#ff6b35', bg='#1a1a1a')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Configuration", 
                                 font=('Arial', 12), 
                                 fg='#888888', bg='#1a1a1a')
        subtitle_label.pack()
        
        # Settings Frame
        settings_frame = tk.LabelFrame(self.config_window, text="Trading Setup", 
                                      font=('Arial', 10, 'bold'),
                                      fg='#ffffff', bg='#2a2a2a', bd=1)
        settings_frame.pack(fill='x', padx=20, pady=15)
        
        # Currency selection
        tk.Label(settings_frame, text="Currency:", fg='#ffffff', bg='#2a2a2a').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.currency_var = tk.StringVar(value=self.settings["currency"])
        currency_combo = ttk.Combobox(settings_frame, textvariable=self.currency_var, 
                                     values=["USD", "EUR", "GBP", "JPY", "AUD", "CAD"], 
                                     state="readonly", width=18)
        currency_combo.grid(row=0, column=1, padx=10, pady=8)
        
        # Prop firm selection
        tk.Label(settings_frame, text="Prop Firm:", fg='#ffffff', bg='#2a2a2a').grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.firm_var = tk.StringVar(value=self.settings["prop_firm"])
        firm_combo = ttk.Combobox(settings_frame, textvariable=self.firm_var, 
                                 values=list(self.prop_firms.keys()), 
                                 state="readonly", width=18)
        firm_combo.grid(row=1, column=1, padx=10, pady=8)
        
        # Day selection
        tk.Label(settings_frame, text="Day:", fg='#ffffff', bg='#2a2a2a').grid(row=2, column=0, sticky='w', padx=10, pady=8)
        self.day_var = tk.StringVar(value=self.settings["day"])
        day_combo = ttk.Combobox(settings_frame, textvariable=self.day_var, 
                                values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], 
                                state="readonly", width=18)
        day_combo.grid(row=2, column=1, padx=10, pady=8)
        
        # Session selection
        tk.Label(settings_frame, text="Session:", fg='#ffffff', bg='#2a2a2a').grid(row=3, column=0, sticky='w', padx=10, pady=8)
        self.session_var = tk.StringVar(value=self.settings["session"])
        session_combo = ttk.Combobox(settings_frame, textvariable=self.session_var, 
                                    values=list(self.sessions.keys()), 
                                    state="readonly", width=18)
        session_combo.grid(row=3, column=1, padx=10, pady=8)
        
        # Button frame
        button_frame = tk.Frame(self.config_window, bg='#1a1a1a')
        button_frame.pack(fill='x', padx=20, pady=15)
        
        start_button = tk.Button(button_frame, text="Start Trading Timer", 
                                font=('Arial', 12, 'bold'),
                                bg='#ff6b35', fg='white', 
                                relief='flat', padx=20, pady=10,
                                command=self.start_main_app)
        start_button.pack()
        
    def start_main_app(self):
        """Save settings and start main countdown window"""
        # Update settings
        self.settings["currency"] = self.currency_var.get()
        self.settings["prop_firm"] = self.firm_var.get()
        self.settings["day"] = self.day_var.get()
        self.settings["session"] = self.session_var.get()
        
        # Close config window and start main app
        self.config_window.destroy()
        self.callback(self.settings)
        
    def show(self):
        """Display config window"""
        self.config_window.mainloop()

class MainCountdownWindow:
    def __init__(self, settings, prop_firms, sessions, mock_news, config_callback):
        self.settings = settings
        self.prop_firms = prop_firms
        self.sessions = sessions
        self.mock_news = mock_news
        self.config_callback = config_callback
        self.news_api = NewsAPI()
        self.current_news_event = None
        self.api_error_message = None
        self.main_window = tk.Tk()
        self.setup_main_window()
        self.create_main_widgets()
        self.fetch_live_news()
        self.update_timer()
        
    def setup_main_window(self):
        """Configure borderless main window"""
        self.main_window.title("Prop Fire Timer")
        self.main_window.geometry("320x400+50+50")  # Top-left position
        self.main_window.resizable(False, False)
        self.main_window.attributes('-topmost', True)
        self.main_window.overrideredirect(True)  # Borderless
        self.main_window.configure(bg='#1a1a1a')
        
        # Add border effect
        border_frame = tk.Frame(self.main_window, bg='#ff6b35', bd=0)
        border_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        self.content_frame = tk.Frame(border_frame, bg='#1a1a1a')
        self.content_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
    def create_main_widgets(self):
        """Create main countdown interface"""
        # Header with settings button
        header_frame = tk.Frame(self.content_frame, bg='#1a1a1a')
        header_frame.pack(fill='x', padx=15, pady=10)
        
        title_label = tk.Label(header_frame, text="🔥 PROP FIRE", 
                              font=('Arial', 16, 'bold'), 
                              fg='#ff6b35', bg='#1a1a1a')
        title_label.pack(side='left')
        
        settings_button = tk.Button(header_frame, text="⚙️", 
                                   font=('Arial', 12), 
                                   bg='#2a2a2a', fg='#ffffff',
                                   relief='flat', padx=8, pady=4,
                                   command=self.open_settings)
        settings_button.pack(side='right')
        
        # Timer display
        timer_frame = tk.Frame(self.content_frame, bg='#2a2a2a', relief='solid', bd=1)
        timer_frame.pack(fill='x', padx=15, pady=10)
        
        self.timer_label = tk.Label(timer_frame, text="00:00:00", 
                                   font=('Arial', 28, 'bold'), 
                                   fg='#00ff00', bg='#2a2a2a')
        self.timer_label.pack(pady=15)
        
        # Status
        self.status_label = tk.Label(self.content_frame, text="Calculating...", 
                                    font=('Arial', 10, 'bold'), 
                                    fg='#ffaa00', bg='#1a1a1a',
                                    wraplength=280, justify='center')
        self.status_label.pack(pady=5)
        
        # Current settings info
        info_frame = tk.Frame(self.content_frame, bg='#2a2a2a', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=15, pady=10)
        
        info_text = f"{self.settings['currency']} | {self.settings['prop_firm']} | {self.settings['day']} | {self.settings['session']}"
        info_label = tk.Label(info_frame, text=info_text, 
                             font=('Arial', 9), 
                             fg='#ffffff', bg='#2a2a2a')
        info_label.pack(pady=8)
        
        # Prop firm rules
        rules = self.prop_firms[self.settings['prop_firm']]
        rules_text = f"Rules: {rules['before']}min before | {rules['after']}min after"
        rules_label = tk.Label(info_frame, text=rules_text, 
                              font=('Arial', 8), 
                              fg='#888888', bg='#2a2a2a')
        rules_label.pack()
        
        # News event info
        self.news_label = tk.Label(self.content_frame, text="No upcoming news", 
                                  font=('Arial', 9), 
                                  fg='#ffffff', bg='#1a1a1a', 
                                  wraplength=280, justify='center')
        self.news_label.pack(pady=10)
        
        # Motivational quote
        motivation_label = tk.Label(self.content_frame, 
                                   text="💪 Stay consistent — small wins compound.", 
                                   font=('Arial', 8, 'italic'), 
                                   fg='#888888', bg='#1a1a1a',
                                   wraplength=280, justify='center')
        motivation_label.pack(pady=5)
        
        # Footer
        footer_label = tk.Label(self.content_frame, text="Made by traderndumia", 
                               font=('Arial', 8), 
                               fg='#666666', bg='#1a1a1a')
        footer_label.pack(side='bottom', pady=5)
        
    def open_settings(self):
        """Close main window and open config"""
        self.main_window.destroy()
        self.config_callback()
        
    def fetch_live_news(self):
        """Fetch live news data from API in background thread"""
        def fetch_news():
            try:
                self.current_news_event = self.news_api.fetch_high_impact_news(
                    self.settings["currency"], 
                    self.settings["day"]
                )
                self.api_error_message = None
            except Exception as e:
                self.api_error_message = f"API Error: {str(e)}"
                self.current_news_event = None
                
        # Run in background thread to avoid blocking UI
        thread = threading.Thread(target=fetch_news, daemon=True)
        thread.start()
        
    def get_next_news_event(self) -> Optional[Dict]:
        """Find the next relevant news event from live API data"""
        # Return live news event if available and within session
        if self.current_news_event and self.is_in_session_time(self.current_news_event["time"]):
            return {
                "datetime": self.current_news_event["datetime"],
                "name": self.current_news_event["event_name"],
                "currency": self.settings["currency"]
            }
        return None
        
    def is_in_session(self, event_time: datetime.datetime) -> bool:
        """Check if event time falls within selected session"""
        session = self.sessions[self.settings["session"]]
        start_time = datetime.datetime.strptime(session["start"], "%H:%M").time()
        end_time = datetime.datetime.strptime(session["end"], "%H:%M").time()
        
        return start_time <= event_time.time() <= end_time
        
    def is_in_session_time(self, time_str: str) -> bool:
        """Check if time string falls within selected session"""
        try:
            event_time = datetime.datetime.strptime(time_str, "%H:%M").time()
            session = self.sessions[self.settings["session"]]
            start_time = datetime.datetime.strptime(session["start"], "%H:%M").time()
            end_time = datetime.datetime.strptime(session["end"], "%H:%M").time()
            return start_time <= event_time <= end_time
        except:
            return False
        
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
                self.status_label.config(text=status_message)
            else:
                self.timer_label.config(text="TRADE NOW", fg='#00ff00')
                self.status_label.config(text="Session Active - No Restrictions")
                
            # Update news information with API error handling
            if self.api_error_message:
                self.news_label.config(text=f"⚠️ {self.api_error_message}\nUsing fallback mode", fg='#ffaa00')
            else:
                next_event = self.get_next_news_event()
                if next_event:
                    news_text = f"📰 {next_event['name']}\n{next_event['datetime'].strftime('%Y-%m-%d %H:%M UTC')}"
                    self.news_label.config(text=news_text, fg='#ffffff')
                elif self.current_news_event is None:
                    self.news_label.config(text="📰 No major news — preparing for session open", fg='#888888')
                else:
                    self.news_label.config(text="📰 No high-impact news in session", fg='#888888')
                
        except Exception as e:
            self.timer_label.config(text="ERROR", fg='#ff4444')
            self.status_label.config(text="Calculation error")
            
        # Schedule next update
        self.main_window.after(1000, self.update_timer)
        
    def show(self):
        """Display main countdown window"""
        self.main_window.mainloop()

class PropFireApp:
    def __init__(self):
        self.load_settings()
        self.setup_data()
        self.news_api = NewsAPI()
        self.show_splash()
        
    def show_splash(self):
        """Show splash screen first"""
        splash = SplashScreen(self.show_config)
        splash.show()
        
    def show_config(self):
        """Show configuration window"""
        config = ConfigWindow(self.settings, self.prop_firms, self.sessions, self.show_main)
        config.show()
        
    def show_main(self, updated_settings):
        """Show main countdown window"""
        self.settings = updated_settings
        self.save_settings()
        main_window = MainCountdownWindow(self.settings, self.prop_firms, self.sessions, self.mock_news, self.show_config)
        main_window.show()
        
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
        
    def run(self):
        """Start the application with splash screen"""
        pass  # Application flow now handled by splash -> config -> main

if __name__ == "__main__":
    app = PropFireApp()
    app.run()