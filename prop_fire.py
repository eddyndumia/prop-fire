import customtkinter as ctk
from tkinter import messagebox
import datetime
import json
import os
from typing import Dict, List, Optional, Tuple
import threading
import time
from news_api import NewsAPI

# Set customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SplashScreen:
    def __init__(self, callback):
        self.callback = callback
        self.splash = ctk.CTk()
        self.setup_splash()
        
    def setup_splash(self):
        """Configure splash screen"""
        self.splash.title("Prop Fire")
        self.splash.geometry("400x300+" + str(self.splash.winfo_screenwidth()//2 - 200) + "+" + str(self.splash.winfo_screenheight()//2 - 150))
        self.splash.overrideredirect(True)  # Remove window decorations
        self.splash.attributes('-topmost', True)
        
        # Main title
        title_label = ctk.CTkLabel(self.splash, text="🔥 PROP FIRE", 
                                  font=('Inter', 32, 'bold'), 
                                  text_color='#ff6b35')
        title_label.pack(expand=True)
        
        # Made by text
        made_by_label = ctk.CTkLabel(self.splash, text="Made by traderndumia", 
                                    font=('Inter', 12), 
                                    text_color='#888888')
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
        self.config_window = ctk.CTk()
        self.setup_config_window()
        self.create_config_widgets()
        
    def setup_config_window(self):
        """Configure config window properties"""
        self.config_window.title("Prop Fire - Configuration")
        self.config_window.geometry("450x400+" + str(self.config_window.winfo_screenwidth()//2 - 225) + "+" + str(self.config_window.winfo_screenheight()//2 - 200))
        self.config_window.resizable(False, False)
        
    def create_config_widgets(self):
        """Create configuration interface"""
        # Header with exit button
        header_frame = ctk.CTkFrame(self.config_window)
        header_frame.pack(fill='x', padx=20, pady=15)
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(fill='x', padx=15, pady=10)
        
        title_label = ctk.CTkLabel(title_frame, text="🔥 PROP FIRE", 
                                  font=('Inter', 18, 'bold'), 
                                  text_color='#ff6b35')
        title_label.pack(side='left')
        
        exit_button = ctk.CTkButton(title_frame, text="❌", 
                                   font=('Inter', 12), 
                                   width=40, height=30,
                                   command=self.exit_app)
        exit_button.pack(side='right')
        
        subtitle_label = ctk.CTkLabel(header_frame, text="Configuration", 
                                     font=('Inter', 12), 
                                     text_color='#888888')
        subtitle_label.pack(pady=(0,10))
        
        # Settings Frame
        settings_frame = ctk.CTkFrame(self.config_window)
        settings_frame.pack(fill='x', padx=20, pady=15)
        
        # Currency selection
        ctk.CTkLabel(settings_frame, text="Currency:", font=('Inter', 12)).grid(row=0, column=0, sticky='w', padx=15, pady=12)
        self.currency_combo = ctk.CTkComboBox(settings_frame, 
                                             values=["USD", "EUR", "GBP", "JPY", "AUD", "CAD"],
                                             font=('Inter', 12), width=180)
        self.currency_combo.set(self.settings["currency"])
        self.currency_combo.grid(row=0, column=1, padx=15, pady=12)
        
        # Prop firm selection
        ctk.CTkLabel(settings_frame, text="Prop Firm:", font=('Inter', 12)).grid(row=1, column=0, sticky='w', padx=15, pady=12)
        self.firm_combo = ctk.CTkComboBox(settings_frame, 
                                         values=list(self.prop_firms.keys()),
                                         font=('Inter', 12), width=180)
        self.firm_combo.set(self.settings["prop_firm"])
        self.firm_combo.grid(row=1, column=1, padx=15, pady=12)
        
        # Day selection
        ctk.CTkLabel(settings_frame, text="Day:", font=('Inter', 12)).grid(row=2, column=0, sticky='w', padx=15, pady=12)
        self.day_combo = ctk.CTkComboBox(settings_frame, 
                                        values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                        font=('Inter', 12), width=180)
        self.day_combo.set(self.settings["day"])
        self.day_combo.grid(row=2, column=1, padx=15, pady=12)
        
        # Session selection
        ctk.CTkLabel(settings_frame, text="Session:", font=('Inter', 12)).grid(row=3, column=0, sticky='w', padx=15, pady=12)
        self.session_combo = ctk.CTkComboBox(settings_frame, 
                                            values=list(self.sessions.keys()),
                                            font=('Inter', 12), width=180)
        self.session_combo.set(self.settings["session"])
        self.session_combo.grid(row=3, column=1, padx=15, pady=12)
        
        # Button frame
        button_frame = ctk.CTkFrame(self.config_window, fg_color="transparent")
        button_frame.pack(fill='x', padx=20, pady=20)
        
        start_button = ctk.CTkButton(button_frame, text="Start Trading Timer", 
                                    font=('Inter', 14, 'bold'),
                                    fg_color='#ff6b35', hover_color='#e55a2b',
                                    height=40, width=200,
                                    command=self.start_main_app)
        start_button.pack()
        
    def exit_app(self):
        """Exit the application"""
        self.config_window.quit()
        self.config_window.destroy()
        
    def start_main_app(self):
        """Save settings and start main countdown window"""
        # Update settings
        self.settings["currency"] = self.currency_combo.get()
        self.settings["prop_firm"] = self.firm_combo.get()
        self.settings["day"] = self.day_combo.get()
        self.settings["session"] = self.session_combo.get()
        
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
        self.main_window = ctk.CTk()
        self.setup_main_window()
        self.create_main_widgets()
        self.fetch_live_news()
        self.update_timer()
        
    def setup_main_window(self):
        """Configure borderless main window"""
        self.main_window.title("Prop Fire Timer")
        self.main_window.geometry("350x450+50+50")  # Top-left position
        self.main_window.resizable(False, False)
        self.main_window.attributes('-topmost', True)
        self.main_window.overrideredirect(True)  # Borderless
        
    def create_main_widgets(self):
        """Create main countdown interface"""
        # Header with settings and exit buttons
        header_frame = ctk.CTkFrame(self.main_window, fg_color="transparent")
        header_frame.pack(fill='x', padx=15, pady=10)
        
        title_label = ctk.CTkLabel(header_frame, text="🔥 PROP FIRE", 
                                  font=('Inter', 16, 'bold'), 
                                  text_color='#ff6b35')
        title_label.pack(side='left')
        
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side='right')
        
        exit_button = ctk.CTkButton(button_frame, text="❌", 
                                   font=('Inter', 12), 
                                   width=35, height=30,
                                   command=self.exit_app)
        exit_button.pack(side='right', padx=(0,5))
        
        settings_button = ctk.CTkButton(button_frame, text="⚙️", 
                                       font=('Inter', 12), 
                                       width=35, height=30,
                                       command=self.open_settings)
        settings_button.pack(side='right')
        
        # Timer display
        timer_frame = ctk.CTkFrame(self.main_window)
        timer_frame.pack(fill='x', padx=15, pady=10)
        
        self.timer_label = ctk.CTkLabel(timer_frame, text="00:00:00", 
                                       font=('Inter', 28, 'bold'), 
                                       text_color='#00ff00')
        self.timer_label.pack(pady=15)
        
        # Status
        self.status_label = ctk.CTkLabel(self.main_window, text="Calculating...", 
                                        font=('Inter', 12, 'bold'), 
                                        text_color='#ffaa00',
                                        wraplength=300)
        self.status_label.pack(pady=5)
        
        # Current settings info
        info_frame = ctk.CTkFrame(self.main_window)
        info_frame.pack(fill='x', padx=15, pady=10)
        
        info_text = f"{self.settings['currency']} | {self.settings['prop_firm']} | {self.settings['day']} | {self.settings['session']}"
        info_label = ctk.CTkLabel(info_frame, text=info_text, 
                                 font=('Inter', 12))
        info_label.pack(pady=8)
        
        # Prop firm rules
        rules = self.prop_firms[self.settings['prop_firm']]
        rules_text = f"Rules: {rules['before']}min before | {rules['after']}min after"
        rules_label = ctk.CTkLabel(info_frame, text=rules_text, 
                                  font=('Inter', 10), 
                                  text_color='#888888')
        rules_label.pack()
        
        # News event info
        self.news_label = ctk.CTkLabel(self.main_window, text="No upcoming news", 
                                      font=('Inter', 12), 
                                      wraplength=300)
        self.news_label.pack(pady=10)
        
        # Motivational quote
        motivation_label = ctk.CTkLabel(self.main_window, 
                                       text="💪 Stay consistent — small wins compound.", 
                                       font=('Inter', 10), 
                                       text_color='#888888',
                                       wraplength=300)
        motivation_label.pack(pady=5)
        
        # Footer
        footer_label = ctk.CTkLabel(self.main_window, text="Made by traderndumia", 
                                   font=('Inter', 10), 
                                   text_color='#666666')
        footer_label.pack(side='bottom', pady=5)
        
    def exit_app(self):
        """Exit the application"""
        self.main_window.quit()
        self.main_window.destroy()
        
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
                    
                self.timer_label.configure(text=timer_text, text_color=timer_color)
                self.status_label.configure(text=status_message)
            else:
                self.timer_label.configure(text="TRADE NOW", text_color='#00ff00')
                self.status_label.configure(text="Session Active - No Restrictions")
                
            # Update news information with API error handling
            if self.api_error_message:
                self.news_label.configure(text=f"⚠️ {self.api_error_message}\nUsing fallback mode", text_color='#ffaa00')
            else:
                next_event = self.get_next_news_event()
                if next_event:
                    news_text = f"📰 {next_event['name']}\n{next_event['datetime'].strftime('%Y-%m-%d %H:%M UTC')}"
                    self.news_label.configure(text=news_text, text_color='#ffffff')
                elif self.current_news_event is None:
                    self.news_label.configure(text="📰 No major news — preparing for session open", text_color='#888888')
                else:
                    self.news_label.configure(text="📰 No high-impact news in session", text_color='#888888')
                
        except Exception as e:
            self.timer_label.configure(text="ERROR", text_color='#ff4444')
            self.status_label.configure(text="Calculation error")
            
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