# 🔥 Prop Fire - Trading Timer & News Tracker

A live countdown timer application designed for prop firm traders to avoid trading during restricted news windows.

## What Prop Fire Does

Prop Fire helps prop firm traders by:
- **Displaying countdown timers** until the next safe trading opportunity
- **Tracking high-impact news events** that affect your chosen currency pairs
- **Applying prop firm-specific rules** (e.g., FTMO's 2-minute restriction before/after red news)
- **Showing session status** for different trading sessions (Asia, London, New York)
- **Staying on top** of your screen as a floating overlay for constant visibility

## Features

### Core Functionality
- ⏰ **Live Countdown Timer** - Shows time until next trade opportunity
- 📰 **News Event Tracking** - Displays upcoming high-impact news
- 🏢 **Prop Firm Rules** - Supports FTMO, MyForexFunds, The5ers, FundedNext
- 🌍 **Multi-Session Support** - Asia, London, New York trading sessions
- 💱 **Currency Pairs** - USD, EUR, GBP, JPY, AUD, CAD

### User Interface
- 🎨 **Modern Dark Theme** - Easy on the eyes during long trading sessions
- 📌 **Always On Top** - Stays visible while you work on other applications
- 💾 **Persistent Settings** - Remembers your preferences between sessions
- 📱 **Compact Design** - Minimal screen real estate usage

## How to Run

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Installation & Usage
1. **Clone or download** the project files
2. **Navigate** to the project directory
3. **Run the application**:
   ```bash
   python prop_fire.py
   ```

### First Time Setup
1. Select your **currency pair** (e.g., USD, EUR)
2. Choose your **prop firm** (FTMO, MyForexFunds, etc.)
3. Pick your **trading day** (Monday-Friday)
4. Select your **preferred session** (Asia, London, New York)

The application will automatically save your settings for future use.

## How the Timer Logic Works

### News Event Detection
1. **Fetches news events** for your selected currency and trading day
2. **Filters high-impact events** that fall within your chosen session
3. **Identifies the next relevant event** that could affect trading

### Prop Firm Rule Application
Each prop firm has different restriction windows:
- **FTMO**: 2 minutes before/after high-impact news
- **MyForexFunds**: 5 minutes before/after high-impact news  
- **The5ers**: 3 minutes before/after high-impact news
- **FundedNext**: 2 minutes before, 3 minutes after high-impact news

### Timer Calculation
The app calculates your next trading opportunity by:

1. **If no news during session**: Countdown to session start
2. **If news exists**:
   - **Before restriction window**: Shows time until trading must stop
   - **During restriction window**: Shows time until trading can resume
   - **After restriction window**: Shows "TRADE NOW" or next restriction

### Visual Indicators
- 🟢 **Green Timer**: Safe to trade (>15 minutes until restriction)
- 🟡 **Yellow Timer**: Caution (5-15 minutes until restriction)  
- 🔴 **Red Timer**: Danger zone (<5 minutes until restriction)

## File Structure

```
Propfire/
├── prop_fire.py           # Main application
├── README.md             # This documentation
└── propfire_settings.json # Auto-generated settings file
```

## Customization

### Adding New Prop Firms
Edit the `prop_firms` dictionary in `prop_fire.py`:
```python
self.prop_firms = {
    "YourFirm": {"before": 3, "after": 2},  # 3 min before, 2 min after
    # ... existing firms
}
```

### Modifying Trading Sessions
Update the `sessions` dictionary with your preferred UTC times:
```python
self.sessions = {
    "YourSession": {"start": "09:00", "end": "18:00"},
    # ... existing sessions
}
```

## Data Sources

### Live Economic Calendar API
Prop Fire now integrates with **API Ninjas Economic Calendar** for real-time high-impact news:
- **Endpoint**: `https://api.api-ninjas.com/v1/economiccalendar`
- **Filters**: High-impact events for selected currency and trading day
- **Fallback**: Graceful degradation when API is unavailable
- **Error Handling**: Network issues, rate limits, and invalid responses

### API Features
- ✅ **Live Data**: Real economic events from API Ninjas
- ✅ **Currency Filtering**: USD, EUR, GBP, JPY, AUD, CAD
- ✅ **Impact Level**: High-impact events only
- ✅ **Session Filtering**: Events within selected trading sessions
- ✅ **Error Recovery**: Falls back to session-based timing when API fails

## Troubleshooting

### Common Issues
- **Timer shows "ERROR"**: Check your system time and date settings
- **Window not staying on top**: Some window managers may override the topmost setting
- **Settings not saving**: Ensure the application has write permissions in its directory

### Performance
- The application updates every second for accurate countdown timing
- Memory usage is minimal (~10-20MB)
- CPU usage is negligible during normal operation

## Motivation

*"Trade with discipline — consistency builds equity."*

Prop Fire was built to help traders maintain discipline by providing clear visual cues about when it's safe to trade, helping you avoid costly mistakes during high-impact news events.

---

**Disclaimer**: This tool is for educational and informational purposes. Always verify news times and prop firm rules independently. Trading involves risk.