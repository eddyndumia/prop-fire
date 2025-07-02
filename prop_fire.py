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
        
        # Debug: Log button visibility
        print(f"DEBUG: Submit button created and packed in scrollable frame")
        
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
        self.fetch_live_news()
        self.update_timer()
        
    def setup_main_window(self):
        """Configure borderless main window"""
        self.main_window.title("PropFire Timer")
        
        # Dynamic sizing based on screen
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()
        
        window_width = min(400, int(screen_width * 0.3))
        window_height = min(600, int(screen_height * 0.7))
        
        # Position on screen
        x = 50
        y = 50
        
        self.main_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.main_window.resizable(True, True)
        self.main_window.minsize(350, 500)
        self.main_window.attributes('-topmost', True)
        self.main_window.overrideredirect(True)
        
    def create_main_widgets(self):
        """Create main countdown interface"""
        # Main container with border effect
        main_container = ctk.CTkFrame(self.main_window, corner_radius=12)
        main_container.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Header with title and control buttons (fixed positioning)
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=50)
        header_frame.pack(fill='x', padx=15, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, text="PropFire", 
                                  font=('Inter', 20, 'bold'), 
                                  text_color='#ff6b35')
        title_label.pack(side='left', pady=10)
        
        # Control buttons container with consistent positioning
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side='right', pady=7)
        
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
        
        # Timer display with enhanced styling
        timer_container = ctk.CTkFrame(main_container, corner_radius=10)
        timer_container.pack(fill='x', padx=20, pady=15)
        
        self.timer_label = ctk.CTkLabel(timer_container, text="00:00:00", 
                                       font=('Inter', 32, 'bold'), 
                                       text_color='#00ff00')
        self.timer_label.pack(pady=20)
        
        # Status with better spacing
        self.status_label = ctk.CTkLabel(main_container, text="Calculating...", 
                                        font=('Inter', 13, 'bold'), 
                                        text_color='#ffaa00',
                                        wraplength=340)
        self.status_label.pack(pady=(5, 15))
        
        # Settings info panel
        info_container = ctk.CTkFrame(main_container, corner_radius=8)
        info_container.pack(fill='x', padx=20, pady=(0, 15))
        
        info_text = f"{self.settings['currency']} | {self.settings['prop_firm']} | {self.settings['day']} | {self.settings['session']}"
        info_label = ctk.CTkLabel(info_container, text=info_text, 
                                 font=('Inter', 13, 'bold'))
        info_label.pack(pady=(12, 8))
        
        # Prop firm rules
        rules = self.prop_firms[self.settings['prop_firm']]
        rules_text = f"Rules: {rules['before']}min before | {rules['after']}min after"
        rules_label = ctk.CTkLabel(info_container, text=rules_text, 
                                  font=('Inter', 11), 
                                  text_color='#aaaaaa')
        rules_label.pack(pady=(0, 12))
        
        # News event info with better styling
        news_container = ctk.CTkFrame(main_container, corner_radius=8)
        news_container.pack(fill='x', padx=20, pady=(0, 15))
        
        self.news_label = ctk.CTkLabel(news_container, text="No upcoming news", 
                                      font=('Inter', 12), 
                                      wraplength=340)
        self.news_label.pack(pady=15)
        
        # Risk calculation display
        risk_container = ctk.CTkFrame(main_container, corner_radius=8)
        risk_container.pack(fill='x', padx=20, pady=(0, 15))
        
        account_size = self.settings.get("account_size", 10000)
        risk_percent = self.settings.get("risk_percent", 1.0)
        risk_amount = (account_size * risk_percent) / 100
        
        risk_text = f"Account: ${account_size:,.0f} | Risk: {risk_percent}% (${risk_amount:,.2f})"
        risk_label = ctk.CTkLabel(risk_container, text=risk_text, 
                                 font=('Inter', 12, 'bold'))
        risk_label.pack(pady=12)
        
        # Motivational quote
        motivation_label = ctk.CTkLabel(main_container, 
                                       text="💪 Stay focused. Trust your plan.", 
                                       font=('Inter', 11, 'italic'), 
                                       text_color='#999999',
                                       wraplength=340)
        motivation_label.pack(pady=(5, 10))
        
        # User credit
        credit_label = ctk.CTkLabel(main_container, text="Made by traderndumia", 
                                   font=('Inter', 10), 
                                   text_color='#777777')
        credit_label.pack(pady=(0, 15))
        
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
                result = self.news_api.fetch_high_impact_news(
                    self.settings["currency"], 
                    self.settings["session"]
                )
                if result:
                    self.current_news_event = result
                    self.api_error_message = None
                    print(f"DEBUG: Successfully fetched news event: {result['title']} at {result['time']} EST")
                else:
                    self.current_news_event = None
                    self.api_error_message = None
                    print(f"DEBUG: No news events found, will use session fallback")
            except Exception as e:
                self.api_error_message = f"API Error: {str(e)}"
                self.current_news_event = None
                print(f"DEBUG: News fetch error: {e}")
                
        # Run in background thread to avoid blocking UI
        thread = threading.Thread(target=fetch_news, daemon=True)
        thread.start()
        
    def get_next_news_event(self) -> Optional[Dict]:
        """Find the next relevant news event from live data"""
        # Return live news event if available
        if self.current_news_event:
            return {
                "datetime": self.current_news_event["datetime"],
                "name": self.current_news_event["title"],
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
            session_name = self.settings["session"]
            return self.get_next_session_start(), f"No high-impact news. Countdown to {session_name} Session start."
            
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
            
    def update_timer(self):
        """Update countdown timer and status"""
        # Check if window still exists before proceeding
        try:
            if not hasattr(self, 'main_window') or not self.main_window.winfo_exists():
                return
        except:
            return
            
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
                
            # Update news information
            if self.current_news_event:
                news_text = f"📰 {self.current_news_event['title']}\n{self.current_news_event['datetime'].strftime('%Y-%m-%d %H:%M UTC')}"
                self.news_label.configure(text=news_text, text_color='#ffffff')
            elif self.api_error_message:
                self.news_label.configure(text=f"⚠️ Network Error\nUsing session timing", text_color='#ffaa00')
            else:
                self.news_label.configure(text="📰 No major news — preparing for session open", text_color='#888888')
                
        except Exception as e:
            print(f"Timer update error: {e}")
            try:
                self.timer_label.configure(text="ERROR", text_color='#ff4444')
                self.status_label.configure(text="Calculation error")
            except:
                pass
            
        # Schedule next update with proper cleanup
        try:
            if hasattr(self, 'main_window') and self.main_window.winfo_exists():
                self.after_job = self.main_window.after(1000, self.update_timer)
        except Exception as e:
            print(f"Timer scheduling error: {e}")
        
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
        
        # Session start times for fallback
        self.session_start_times = {
            "London": "08:00",
            "New York": "13:00",
            "Tokyo": "00:00",
            "Sydney": "22:00"
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