import customtkinter as ctk
from tkinter import messagebox
import datetime
import json
import os
from typing import Dict, List, Optional, Tuple
import threading
import time
import pytz
import webbrowser
from news_api import NewsAPI
from trading_journal import TradingJournalWindow

# Set customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SplashScreen:
    def __init__(self, callback):
        self.callback = callback
        self.splash = ctk.CTk()
        self.after_job = None
        self.setup_splash()
        
    def setup_splash(self):
        """Configure splash screen"""
        self.splash.title("PropFire")
        
        # Get screen dimensions for perfect centering
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        window_width = 400
        window_height = 250
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.splash.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.splash.overrideredirect(True)
        self.splash.attributes('-topmost', True)
        
        # Main container with responsive layout
        main_frame = ctk.CTkFrame(self.splash, fg_color="transparent")
        main_frame.pack(fill='both', expand=True)
        
        # Center the title perfectly
        title_label = ctk.CTkLabel(main_frame, text="PropFire", 
                                  font=('Inter', 42, 'bold'), 
                                  text_color='#ff6b35')
        title_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Auto-close after 2.5 seconds
        self.after_job = self.splash.after(2500, self.close_splash)
        
    def close_splash(self):
        """Close splash and open main app"""
        try:
            if self.after_job:
                self.splash.after_cancel(self.after_job)
            self.splash.destroy()
            self.callback()
        except:
            pass
        
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
        self.drag_data = {"x": 0, "y": 0}
        self.setup_config_window()
        self.create_config_widgets()
        self.setup_drag()
        
    def setup_config_window(self):
        """Configure config window properties"""
        self.config_window.title("PropFire - Configuration")
        
        # Get screen dimensions for responsive sizing
        screen_width = self.config_window.winfo_screenwidth()
        screen_height = self.config_window.winfo_screenheight()
        
        # Dynamic window sizing based on screen
        window_width = min(500, int(screen_width * 0.4))
        window_height = min(700, int(screen_height * 0.8))
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.config_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.config_window.resizable(True, True)
        self.config_window.minsize(450, 600)
        self.config_window.overrideredirect(True)
        self.config_window.attributes('-topmost', True)
        
    def create_config_widgets(self):
        """Create configuration interface with scrollable layout"""
        # Main container with border effect
        main_container = ctk.CTkFrame(self.config_window, corner_radius=12)
        main_container.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(main_container, corner_radius=0)
        self.scrollable_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Header with title and exit button (fixed at top)
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=60)
        header_frame.pack(fill='x', padx=20, pady=(15, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, text="PropFire", 
                                  font=('Inter', 22, 'bold'), 
                                  text_color='#ff6b35')
        title_label.pack(side='left', pady=15)
        
        exit_button = ctk.CTkButton(header_frame, text="❌", 
                                   font=('Inter', 14), 
                                   width=36, height=36,
                                   corner_radius=18,
                                   command=self.exit_app)
        exit_button.pack(side='right', pady=12)
        
        # Subtitle in scrollable area
        subtitle_label = ctk.CTkLabel(self.scrollable_frame, text="Trading Configuration", 
                                     font=('Inter', 16, 'bold'), 
                                     text_color='#aaaaaa')
        subtitle_label.pack(pady=(20, 30))
        
        # Settings container with proper grid layout in scrollable area
        settings_container = ctk.CTkFrame(self.scrollable_frame)
        settings_container.pack(fill='x', padx=20, pady=(0, 30))
        
        # Configure grid weights for responsive layout
        settings_container.grid_columnconfigure(1, weight=1)
        
        # Currency selection
        ctk.CTkLabel(settings_container, text="Currency:", 
                    font=('Inter', 13, 'bold')).grid(row=0, column=0, sticky='w', padx=20, pady=15)
        self.currency_combo = ctk.CTkComboBox(settings_container, 
                                             values=["USD", "EUR", "GBP", "JPY", "AUD", "CAD"],
                                             font=('Inter', 13), width=200, height=35)
        self.currency_combo.set(self.settings["currency"])
        self.currency_combo.grid(row=0, column=1, sticky='ew', padx=(10, 20), pady=15)
        
        # Prop firm selection
        ctk.CTkLabel(settings_container, text="Prop Firm:", 
                    font=('Inter', 13, 'bold')).grid(row=1, column=0, sticky='w', padx=20, pady=15)
        self.firm_combo = ctk.CTkComboBox(settings_container, 
                                         values=list(self.prop_firms.keys()),
                                         font=('Inter', 13), width=200, height=35)
        self.firm_combo.set(self.settings["prop_firm"])
        self.firm_combo.grid(row=1, column=1, sticky='ew', padx=(10, 20), pady=15)
        
        # Day selection
        ctk.CTkLabel(settings_container, text="Trading Day:", 
                    font=('Inter', 13, 'bold')).grid(row=2, column=0, sticky='w', padx=20, pady=15)
        self.day_combo = ctk.CTkComboBox(settings_container, 
                                        values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                        font=('Inter', 13), width=200, height=35)
        self.day_combo.set(self.settings["day"])
        self.day_combo.grid(row=2, column=1, sticky='ew', padx=(10, 20), pady=15)
        
        # Session selection
        ctk.CTkLabel(settings_container, text="Session:", 
                    font=('Inter', 13, 'bold')).grid(row=3, column=0, sticky='w', padx=20, pady=15)
        self.session_combo = ctk.CTkComboBox(settings_container, 
                                            values=list(self.sessions.keys()),
                                            font=('Inter', 13), width=200, height=35)
        self.session_combo.set(self.settings["session"])
        self.session_combo.grid(row=3, column=1, sticky='ew', padx=(10, 20), pady=15)
        
        # Account size input
        ctk.CTkLabel(settings_container, text="Account Size:", 
                    font=('Inter', 13, 'bold')).grid(row=4, column=0, sticky='w', padx=20, pady=15)
        self.account_entry = ctk.CTkEntry(settings_container, 
                                         font=('Inter', 13), width=200, height=35,
                                         placeholder_text="e.g., 10000")
        self.account_entry.insert(0, str(self.settings.get("account_size", "10000")))
        self.account_entry.grid(row=4, column=1, sticky='ew', padx=(10, 20), pady=15)
        
        # Risk percentage input
        ctk.CTkLabel(settings_container, text="Risk %:", 
                    font=('Inter', 13, 'bold')).grid(row=5, column=0, sticky='w', padx=20, pady=15)
        self.risk_entry = ctk.CTkEntry(settings_container, 
                                      font=('Inter', 13), width=200, height=35,
                                      placeholder_text="e.g., 1.5")
        self.risk_entry.insert(0, str(self.settings.get("risk_percent", "1.0")))
        self.risk_entry.grid(row=5, column=1, sticky='ew', padx=(10, 20), pady=15)
        
        # Button container in scrollable area - always visible
        button_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        button_container.pack(fill='x', padx=20, pady=(20, 40))
        
        start_button = ctk.CTkButton(button_container, text="Start Trading Timer", 
                                    font=('Inter', 16, 'bold'),
                                    fg_color='#ff6b35', hover_color='#e55a2b',
                                    height=50, corner_radius=10,
                                    command=self.start_main_app)
        start_button.pack(pady=15, fill='x', padx=30)
        
        print(f"DEBUG: Submit button created and packed in scrollable frame")
        
    def open_coffee_link(self):
        """Open Buy Me Coffee link in browser"""
        webbrowser.open('https://www.buymeacoffee.com/traderndumia')
        
    def exit_app(self):
        """Exit the application"""
        self.config_window.quit()
        self.config_window.destroy()
        
    def setup_drag(self):
        """Setup window dragging functionality"""
        self.config_window.bind("<Button-1>", self.start_drag)
        self.config_window.bind("<B1-Motion>", self.do_drag)
        
    def start_drag(self, event):
        """Start dragging the window"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def do_drag(self, event):
        """Drag the window"""
        x = self.config_window.winfo_x() + (event.x - self.drag_data["x"])
        y = self.config_window.winfo_y() + (event.y - self.drag_data["y"])
        self.config_window.geometry(f"+{x}+{y}")
        
    def start_main_app(self):
        """Save settings and start main countdown window"""
        # Update settings
        self.settings["currency"] = self.currency_combo.get()
        self.settings["prop_firm"] = self.firm_combo.get()
        self.settings["day"] = self.day_combo.get()
        self.settings["session"] = self.session_combo.get()
        
        # Save account size and risk percentage
        try:
            self.settings["account_size"] = float(self.account_entry.get() or "10000")
            self.settings["risk_percent"] = float(self.risk_entry.get() or "1.0")
        except ValueError:
            self.settings["account_size"] = 10000.0
            self.settings["risk_percent"] = 1.0
        
        # Close config window and start main app with news loading
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
        self.current_news_events = []
        self.api_error_message = None
        self.after_job = None
        self.drag_data = {"x": 0, "y": 0}
        self.session_start_times = {
            "London": "03:00",   # 8AM GMT = 3AM EST
            "New York": "08:00", # 8AM EST
            "Tokyo": "19:00",    # 8AM JST = 7PM EST (previous day)
            "Sydney": "17:00"    # 8AM AEDT = 5PM EST (previous day)
        }
        self.main_window = ctk.CTk()
        self.setup_main_window()
        self.create_main_widgets()
        self.setup_drag()
        # Load news when starting trading
        self.load_cached_news()
        self.fetch_live_news()
        self.update_timer()
        
    def setup_main_window(self):
        """Configure resizable main window with professional layout"""
        self.main_window.title("PropFire - Professional Trading Timer")
        
        # Set wider initial size for better visibility
        self.main_window.geometry("1200x700+100+50")
        self.main_window.resizable(True, True)
        self.main_window.minsize(1000, 600)
        self.main_window.attributes('-topmost', False)
        
        # Configure main window grid for responsive layout
        self.main_window.grid_rowconfigure(0, weight=1)
        self.main_window.grid_columnconfigure(0, weight=1)
        
    def create_main_widgets(self):
        """Create compact main countdown interface"""
        # Main container with grid layout
        main_container = ctk.CTkFrame(self.main_window, corner_radius=12)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure grid for two-column layout
        main_container.grid_columnconfigure(0, weight=2)  # Left column (news)
        main_container.grid_columnconfigure(1, weight=1)  # Right column (rules)
        main_container.grid_rowconfigure(3, weight=1)     # News table row
        
        # Header spanning both columns
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=15, pady=(10, 5))
        
        title_label = ctk.CTkLabel(header_frame, text="PropFire", 
                                  font=('Inter', 20, 'bold'), 
                                  text_color='#ff6b35')
        title_label.pack(side='left')
        
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side='right')
        
        settings_button = ctk.CTkButton(controls_frame, text="⚙️", 
                                       font=('Inter', 14), 
                                       width=36, height=36, corner_radius=18,
                                       command=self.open_settings)
        settings_button.pack(side='right', padx=(0, 5))
        
        exit_button = ctk.CTkButton(controls_frame, text="❌", 
                                   font=('Inter', 14), 
                                   width=36, height=36, corner_radius=18,
                                   command=self.exit_app)
        exit_button.pack(side='right')
        
        # Timer display spanning both columns
        timer_container = ctk.CTkFrame(main_container, corner_radius=10)
        timer_container.grid(row=1, column=0, columnspan=2, sticky='ew', padx=20, pady=10)
        
        self.timer_label = ctk.CTkLabel(timer_container, text="00:00:00", 
                                       font=('Inter', 32, 'bold'), 
                                       text_color='#00ff00')
        self.timer_label.pack(pady=20)
        
        # Status and time display spanning both columns
        status_time_frame = ctk.CTkFrame(main_container, fg_color='transparent')
        status_time_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        
        self.status_label = ctk.CTkLabel(status_time_frame, text="Calculating...", 
                                        font=('Inter', 13, 'bold'), 
                                        text_color='#ffaa00')
        self.status_label.pack(side='left')
        
        self.time_label = ctk.CTkLabel(status_time_frame, text="Local: 00:00:00 | EST: 00:00:00", 
                                      font=('Inter', 11), 
                                      text_color='#aaaaaa')
        self.time_label.pack(side='right')
        
        # Left column - News table
        news_container = ctk.CTkFrame(main_container, corner_radius=8)
        news_container.grid(row=3, column=0, sticky='nsew', padx=(20, 10), pady=(0, 10))
        
        # Professional table header
        header_frame = ctk.CTkFrame(news_container, fg_color='#333333')
        header_frame.pack(fill='x', padx=5, pady=(5, 0))
        
        headers = ['Time (EST)', 'Currency', 'Event', 'Impact']
        weights = [1, 1, 4, 1]
        for i, (header, weight) in enumerate(zip(headers, weights)):
            header_frame.grid_columnconfigure(i, weight=weight)
            
            # Create header cell with border
            header_cell = ctk.CTkFrame(header_frame, fg_color='#444444', corner_radius=0)
            header_cell.grid(row=0, column=i, padx=1, pady=1, sticky='nsew')
            
            label = ctk.CTkLabel(header_cell, text=header, font=('Inter', 12, 'bold'), anchor='w')
            label.pack(padx=8, pady=5, fill='x')
        
        self.news_scroll = ctk.CTkScrollableFrame(news_container)
        self.news_scroll.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Right column - Controls and Rules
        right_column = ctk.CTkFrame(main_container, corner_radius=8)
        right_column.grid(row=3, column=1, sticky='nsew', padx=(10, 20), pady=(0, 10))
        
        # Refresh button
        refresh_button = ctk.CTkButton(right_column, text="🔄 Refresh News", 
                                      font=('Inter', 12, 'bold'), 
                                      width=140, height=35,
                                      fg_color='#28a745', hover_color='#218838',
                                      command=self.refresh_news)
        refresh_button.pack(pady=(15, 10))
        
        # Prop firm rules in right column
        self.create_prop_firm_rules_panel(right_column)
        
        # Trading Journal button
        journal_button = ctk.CTkButton(right_column, text="📊 Trading Journal", 
                                      font=('Inter', 12, 'bold'), 
                                      width=140, height=35,
                                      fg_color='#4A90E2', hover_color='#357ABD',
                                      command=self.open_trading_journal)
        journal_button.pack(pady=(10, 5))
        
        # Sticky footer spanning both columns - BOTTOM MOST
        footer_frame = ctk.CTkFrame(main_container, fg_color='transparent')
        footer_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        # Support link
        support_label = ctk.CTkLabel(footer_frame, text="Buy me a coffee/beer", 
                                    font=('Inter', 16, 'underline'), 
                                    text_color='#4A90E2',
                                    cursor='hand2')
        support_label.pack(pady=5)
        support_label.bind("<Button-1>", lambda e: webbrowser.open('https://www.buymeacoffee.com/traderndumia'))
        
    def exit_app(self):
        """Exit the application"""
        try:
            if hasattr(self, 'after_job') and self.after_job:
                self.main_window.after_cancel(self.after_job)
            self.main_window.quit()
            self.main_window.destroy()
        except Exception as e:
            print(f"Exit error: {e}")
        
    def setup_drag(self):
        """Setup window dragging functionality"""
        self.main_window.bind("<Button-1>", self.start_drag)
        self.main_window.bind("<B1-Motion>", self.do_drag)
        
    def start_drag(self, event):
        """Start dragging the window"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def do_drag(self, event):
        """Drag the window"""
        x = self.main_window.winfo_x() + (event.x - self.drag_data["x"])
        y = self.main_window.winfo_y() + (event.y - self.drag_data["y"])
        self.main_window.geometry(f"+{x}+{y}")
        
    def open_settings(self):
        """Close main window and open config"""
        try:
            if hasattr(self, 'after_job') and self.after_job:
                self.main_window.after_cancel(self.after_job)
            self.main_window.destroy()
            self.config_callback()
        except Exception as e:
            print(f"Settings transition error: {e}")
        
    def fetch_live_news(self):
        """Fetch live news data from API in background thread"""
        def fetch_news():
            try:
                print(f"DEBUG: Fetching news for {self.settings['currency']} in {self.settings['session']} session")
                events = self.news_api.get_high_impact_news(
                    self.settings["currency"], 
                    self.settings["session"]
                )
                if events:
                    self.current_news_events = events
                    self.api_error_message = None
                    print(f"DEBUG: Successfully fetched {len(events)} news events")
                    # Update table only when new events are fetched
                    self.update_news_table()
                else:
                    self.current_news_events = []
                    self.api_error_message = None
                    print(f"DEBUG: No news events found, will use session fallback")
                    self.update_news_table()
            except Exception as e:
                self.api_error_message = f"API Error: {str(e)}"
                self.current_news_events = []
                print(f"DEBUG: News fetch error: {e}")
                
        # Run in background thread to avoid blocking UI
        thread = threading.Thread(target=fetch_news, daemon=True)
        thread.start()
        
    def get_next_news_event(self) -> Optional[Dict]:
        """Find the next available high-impact news event"""
        if self.current_news_events:
            now = datetime.datetime.now()
            upcoming_events = [e for e in self.current_news_events if e["datetime"] > now]
            
            if upcoming_events:
                return {
                    "datetime": upcoming_events[0]["datetime"],
                    "name": upcoming_events[0]["title"],
                    "currency": self.settings["currency"]
                }
        return None
        
    def is_selected_day_passed(self) -> bool:
        """Check if selected day has already passed this week"""
        now = datetime.datetime.now()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        selected_weekday = day_map.get(self.settings["day"], 0)
        
        return selected_weekday < current_weekday
        
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
        """Calculate accurate countdown to next high-impact news release in EST"""
        # Get current time in EST
        est_tz = pytz.timezone('US/Eastern')
        local_tz = pytz.timezone('UTC')  # Default to UTC if can't detect
        
        try:
            # Try to get local timezone
            import time
            local_tz = pytz.timezone(time.tzname[0])
        except:
            pass
            
        # Current time in EST
        now_local = datetime.datetime.now(local_tz)
        now_est = now_local.astimezone(est_tz)
        
        # Get next event for SELECTED DAY only
        selected_day = self.settings["day"]
        if self.current_news_events:
            # Filter events for selected day only
            selected_day_events = [e for e in self.current_news_events 
                                 if e.get("day_name", "") == selected_day]
            
            for event in selected_day_events:
                # News release time is already in EST
                news_release_est = event["datetime"].replace(tzinfo=est_tz)
                
                if news_release_est > now_est:
                    event_name = event["title"]
                    return news_release_est.replace(tzinfo=None), f"Next {selected_day}: {event_name}"
        
        # Fallback to session start
        selected_day = self.settings["day"]
        return self.get_next_session_start(), f"No high-impact news for {selected_day}. Next session start."
            
    def get_next_session_start(self) -> datetime.datetime:
        """Get the next session start time with fallback support"""
        now = datetime.datetime.now()
        session_name = self.settings["session"]
        
        # Use session start times for fallback
        session_time = self.session_start_times.get(session_name, "08:00")
        
        # Try today first
        today_start = datetime.datetime.combine(now.date(), 
                                               datetime.datetime.strptime(session_time, "%H:%M").time())
        
        if now < today_start:
            return today_start
        else:
            # Next day
            tomorrow = now + datetime.timedelta(days=1)
            return datetime.datetime.combine(tomorrow.date(), 
                                           datetime.datetime.strptime(session_time, "%H:%M").time())
            
    def get_current_times(self) -> Tuple[str, str]:
        """Get current local and EST times for display"""
        est_tz = pytz.timezone('US/Eastern')
        now_local = datetime.datetime.now()
        now_est = now_local.astimezone(est_tz) if hasattr(now_local, 'astimezone') else datetime.datetime.now()
        
        local_time_str = now_local.strftime("%H:%M:%S")
        est_time_str = now_est.strftime("%H:%M:%S EST")
        
        return local_time_str, est_time_str
    
    def update_timer(self):
        """Update countdown timer with accurate EST calculations"""
        try:
            if not hasattr(self, 'main_window') or not self.main_window.winfo_exists():
                return
        except:
            return
            
        try:
            next_trade_time, status_message = self.calculate_next_trade_time()
            
            # Use EST timezone for accurate calculation
            est_tz = pytz.timezone('US/Eastern')
            now_est = datetime.datetime.now(est_tz).replace(tzinfo=None)
            
            # Calculate time difference
            time_diff = next_trade_time - now_est
            
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
                

            
            # Update time display
            local_time, est_time = self.get_current_times()
            self.time_label.configure(text=f"Local: {local_time} | {est_time}")
            
            # Check if selected day has passed
            if self.is_selected_day_passed():
                self.timer_label.configure(text="EVENT PASSED", text_color='#ff4444')
                self.status_label.configure(text=f"{self.settings['day']} has already passed this week")
                return
                
        except Exception as e:
            print(f"Timer update error: {e}")
            try:
                self.timer_label.configure(text="ERROR", text_color='#ff4444')
                self.status_label.configure(text="Calculation error")
            except:
                pass
        
        # Schedule next update
        try:
            if hasattr(self, 'main_window') and self.main_window.winfo_exists():
                self.after_job = self.main_window.after(1000, self.update_timer)
        except Exception as e:
            print(f"Timer scheduling error: {e}")
            
    def update_news_table(self):
        """Update professional news table for selected day only"""
        try:
            # Clear existing table
            for widget in self.news_scroll.winfo_children():
                widget.destroy()
            
            if self.current_news_events:
                # Filter events for selected day only
                selected_day = self.settings["day"]
                selected_day_events = [e for e in self.current_news_events 
                                     if e.get("day_name", "") == selected_day]
                
                for i, event in enumerate(selected_day_events[:15]):
                    bg_color = '#2b2b2b' if i % 2 == 0 else '#333333'
                    row_frame = ctk.CTkFrame(self.news_scroll, fg_color=bg_color)
                    row_frame.pack(fill='x', pady=1, padx=2)
                    
                    # Configure grid weights (4 columns)
                    weights = [1, 1, 4, 1]
                    for j, weight in enumerate(weights):
                        row_frame.grid_columnconfigure(j, weight=weight)
                    
                    # Extract event data
                    time_str = event.get('time', 'N/A')
                    currency = event.get('currency', 'N/A')
                    title = event.get('title', event.get('name', 'Economic Event'))
                    impact = event.get('impact', 'Medium')
                    
                    # Create cells with borders for table structure
                    cells_data = [
                        (time_str, '#ffffff'),
                        (currency, '#ffffff'),
                        (title[:40] + '...' if len(title) > 40 else title, '#ffffff'),
                        ('🔴 High' if impact == 'High' else impact, '#ff4444' if impact == 'High' else '#ffaa00')
                    ]
                    
                    for j, (text, color) in enumerate(cells_data):
                        cell = ctk.CTkFrame(row_frame, fg_color='transparent', corner_radius=0)
                        cell.grid(row=0, column=j, padx=1, pady=1, sticky='nsew')
                        
                        label = ctk.CTkLabel(cell, text=text, font=('Inter', 11), 
                                           text_color=color, anchor='w')
                        label.pack(padx=8, pady=3, fill='x')
            if not self.current_news_events:
                ctk.CTkLabel(self.news_scroll, text="No events loaded. Click 'Refresh News' to fetch data.", 
                           font=('Inter', 12), text_color='#888888').pack(pady=30)
            elif not [e for e in self.current_news_events if e.get("day_name", "") == self.settings["day"]]:
                ctk.CTkLabel(self.news_scroll, text=f"No high-impact events found for {self.settings['day']}", 
                           font=('Inter', 12), text_color='#888888').pack(pady=30)
        except Exception as e:
            self.log_error(f"News table update error: {e}")
    
    def calculate_event_countdown(self, event) -> str:
        """Calculate countdown to event release"""
        try:
            if 'datetime' not in event:
                return 'N/A'
            
            est_tz = pytz.timezone('US/Eastern')
            now_est = datetime.datetime.now(est_tz)
            event_time = event['datetime']
            
            if isinstance(event_time, str):
                event_time = datetime.datetime.fromisoformat(event_time.replace('Z', '+00:00'))
            
            if event_time.tzinfo is None:
                event_time = est_tz.localize(event_time)
            
            time_diff = event_time - now_est
            
            if time_diff.total_seconds() <= 0:
                return 'PASSED'
            
            hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except Exception:
            return 'N/A'
    
    def refresh_news(self):
        """Manual refresh of news data"""
        print("DEBUG: Manual news refresh initiated")
        self.current_news_events = []
        self.fetch_live_news()
        self.save_news_cache()
    
    def load_cached_news(self):
        """Load cached news data"""
        try:
            cache_file = 'news_cache.json'
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cache_time = datetime.datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                    
                    # Use cache if less than 12 hours old
                    if (datetime.datetime.now() - cache_time).total_seconds() < 43200:
                        self.current_news_events = cache_data.get('events', [])
                        print(f"DEBUG: Loaded {len(self.current_news_events)} cached events")
                        # Update table when cached events are loaded
                        self.update_news_table()
                        return
            
            print("DEBUG: No valid cache found")
        except Exception as e:
            self.log_error(f"Cache loading error: {e}")
    
    def save_news_cache(self):
        """Save news data to cache"""
        try:
            cache_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'events': self.current_news_events
            }
            with open('news_cache.json', 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            self.log_error(f"Cache saving error: {e}")
    
    def log_error(self, message: str):
        """Log errors to file"""
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/app_errors.log', 'a') as f:
                timestamp = datetime.datetime.now().isoformat()
                f.write(f"[{timestamp}] {message}\n")
            print(f"ERROR: {message}")
        except:
            print(f"ERROR: {message}")
        
    def create_prop_firm_rules_panel(self, parent):
        """Create compact prop firm rules panel"""
        firm = self.settings['prop_firm']
        firm_data = self.prop_firms.get(firm, self.prop_firms['FTMO'])
        
        rules_container = ctk.CTkFrame(parent, corner_radius=8)
        rules_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Compact rules header
        rules_title = ctk.CTkLabel(rules_container, text=f"{firm} Rules", 
                                  font=('Inter', 12, 'bold'), 
                                  text_color='#ff6b35')
        rules_title.pack(pady=(10, 5))
        
        # Compact rules content
        rules_text = f"News Window:\n{firm_data.get('before', 0)} + {firm_data.get('after', 0)} min\n\n"
        rules_text += f"Max Daily: {firm_data.get('max_daily_loss', firm_data.get('max_daily_drawdown', 'N/A'))}%\n"
        rules_text += f"Max Overall: {firm_data.get('max_overall_loss', firm_data.get('max_overall_drawdown', 'N/A'))}%"
        
        rules_label = ctk.CTkLabel(rules_container, text=rules_text, 
                                  font=('Inter', 16), 
                                  text_color='#cccccc',
                                  justify='center')
        rules_label.pack(padx=5, pady=(0, 10))
    
    def open_trading_journal(self):
        """Open Trading Journal window"""
        journal = TradingJournalWindow()
        journal.show()
    
    def open_coffee_link(self):
        """Open Buy Me Coffee link in browser"""
        webbrowser.open('https://www.buymeacoffee.com/traderndumia')
        
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
            "account_size": 10000.0,
            "risk_percent": 1.0,
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
        # Professional prop firm rules based on real requirements
        self.prop_firms = {
            "FTMO": {
                "before": 2, "after": 2,
                "max_daily_loss": 5,
                "max_overall_loss": 10,
                "min_trading_days": 30,
                "description": "No trading 2 min before/after high impact news (4-min window)"
            },
            "MyForexFunds": {
                "before": 5, "after": 5,
                "max_daily_drawdown": 5,
                "max_overall_drawdown": 12,
                "weekend_holding": False,
                "description": "No trading 5 min before/after news (10-min window)"
            },
            "The Funded Trader": {
                "before": 8, "after": 8,
                "max_daily_drawdown": 5,
                "ea_allowed": True,
                "description": "No open trades 8 min before/after high-impact news"
            },
            "True Forex Funds": {
                "before": 10, "after": 10,
                "overnight_holding": True,
                "description": "No open trades 10 min before/after news"
            }
        }
        
        # Trading sessions (EST times)
        self.sessions = {
            "Asia": {"start": "19:00", "end": "04:00"},
            "London": {"start": "03:00", "end": "12:00"},
            "New York": {"start": "08:30", "end": "17:00"}
        }
        
        # Session start times for fallback (EST)
        self.session_start_times = {
            "London": "03:00",
            "New York": "08:30",  # Fixed to 8:30 AM EST
            "Tokyo": "19:00",
            "Sydney": "17:00"
        }
        
        # Mock high-impact news events
        self.mock_news = self.generate_mock_news()
        
    def generate_mock_news(self) -> List[Dict]:
        """Generate sample news events for demonstration"""
        today = datetime.datetime.now()
        news_events = []
        
        sample_events = [
            {"currency": "USD", "name": "FOMC Meeting", "impact": "high", "time": "14:00"},
            {"currency": "USD", "name": "NFP Release", "impact": "high", "time": "08:30"},
            {"currency": "EUR", "name": "ECB Rate Decision", "impact": "high", "time": "08:45"},
            {"currency": "GBP", "name": "BOE Meeting", "impact": "high", "time": "07:00"},
            {"currency": "JPY", "name": "BOJ Statement", "impact": "high", "time": "22:00"}
        ]
        
        for i in range(7):
            event_date = today + datetime.timedelta(days=i)
            for event in sample_events:
                if event_date.weekday() < 5:
                    news_events.append({
                        "date": event_date.strftime("%Y-%m-%d"),
                        "time": event["time"],
                        "currency": event["currency"],
                        "name": event["name"],
                        "impact": event["impact"]
                    })
        
        return news_events
        
    def run(self):
        """Start the application"""
        pass

if __name__ == "__main__":
    app = PropFireApp()
    app.run()