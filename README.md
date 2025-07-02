# PropFire

A professional trading timer and journal application designed for forex traders who demand precision in news event timing and comprehensive trade tracking. PropFire eliminates the guesswork in high-impact news trading by providing accurate EST-based countdown timers and maintains detailed trading records through an integrated journal system.

## Overview

PropFire addresses the critical challenge faced by forex traders: timing market entries around high-impact economic news releases. The application provides real-time countdown timers for selected trading days, comprehensive trade journaling with P&L tracking, and equity curve visualization. Built with a focus on reliability and professional-grade functionality, PropFire serves as an essential tool for systematic trading operations.

## Key Features

### Economic Calendar & Timing
- Accurate EST-based countdown timers for high-impact news events
- Configurable trading sessions (London, New York, Asia)
- Day-specific event filtering with manual news refresh
- Professional news table with time, currency, event, and impact columns

### Account Management & Equity Tracking
- Configurable starting balance with automatic equity curve generation
- Real-time P&L calculation and display
- Account reset functionality with data preservation options
- Visual equity progression tracking

### Trading Journal
- Calendar-based daily P&L entry system
- Chart image attachments for trade setups (PNG/JPEG support)
- Comprehensive trade details: entry price, stop-loss, take-profit
- Automatic risk/reward ratio calculations
- Monthly P&L aggregation and visualization

### User Interface
- Dark-themed, responsive design optimized for trading environments
- Resizable windows with dynamic content adaptation
- Professional typography using Inter font family
- Intuitive navigation with topmost window management

## Architecture & Technologies

### Design Patterns
PropFire implements a clean MVC architecture with clear separation of concerns:
- **Models**: Data structures for trades, account information, and news events
- **Views**: CustomTkinter-based UI components with responsive layouts
- **Controllers**: Business logic handlers and service layer abstractions

### Core Technologies
- **UI Framework**: CustomTkinter 5.2+ for modern, native-feeling interfaces
- **Database**: SQLite with direct SQL for optimal performance
- **Timezone Handling**: pytz for accurate EST conversions
- **Image Processing**: Pillow for chart image management
- **HTTP Requests**: requests library for news API integration

### Persistence Layer
- SQLite databases for trade entries and account data
- JSON configuration files for user preferences
- Organized image storage with automatic file management
- 12-hour news caching with timestamp validation

### Dependency Injection
Services are injected through constructor parameters, enabling:
- Clean separation between data access and business logic
- Simplified unit testing with mock implementations
- Flexible configuration management

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux operating system
- Minimum 4GB RAM, 100MB disk space

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/propfire.git
cd propfire
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python prop_fire.py
```

### First-Time Setup
1. Configure your preferred currency, trading day, and session
2. Set your starting account balance via "Set Account Size"
3. Begin logging trades through the Trading Journal

## Usage

### Account Configuration
Access account settings through the "Set Account Size" button. This establishes your starting balance and initializes the equity tracking system. Changing the account size will reset all existing trade data.

### Trading Journal Access
Click "Trading Journal" to open the calendar-based entry system. Each day cell displays the date and daily P&L. Click any day to enter trade details including entry/exit prices, stop-loss, take-profit levels, and attach chart screenshots.

### News Event Monitoring
The main dashboard displays high-impact news events for your selected trading day. Use "Refresh News" to manually update the event list. The system filters events based on your configured day preference, ignoring other days' events.

### Equity Curve Monitoring
The right panel displays real-time account equity, starting balance, and cumulative P&L. The display updates automatically as journal entries are added or modified.

## Development & Contribution

### Code Style
- Follow PEP 8 conventions with 4-space indentation
- Use type hints for all function parameters and return values
- Maintain comprehensive docstrings for all public methods
- Keep line length under 100 characters

### Testing Requirements
Run the test suite before submitting contributions:
```bash
python -m pytest tests/ -v
```

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for new features
- `feature/*`: Individual feature development
- `hotfix/*`: Critical bug fixes

### Contribution Process
1. Fork the repository and create a feature branch
2. Implement changes with appropriate test coverage
3. Ensure all tests pass and code follows style guidelines
4. Submit a pull request with detailed description of changes

## Roadmap & Future Enhancements

### Planned Features
- **Session Overlap Alerts**: Visual indicators for overlapping trading sessions
- **API Redundancy**: Multiple news source integration for reliability
- **Export Functionality**: CSV/PDF export for trade records and equity curves
- **Advanced Analytics**: Win rate, average R/R, and performance metrics
- **Mobile Companion**: Read-only mobile app for trade monitoring

### Performance Optimizations
- Lazy loading for large datasets
- Background threading for API calls
- Optimized database queries with proper indexing
- Memory usage optimization for extended runtime

## License & Acknowledgments

### License
This project is licensed under the MIT License. See LICENSE file for details.

### Third-Party Libraries
- CustomTkinter: Modern UI framework for Python
- Pillow: Python Imaging Library for image processing
- pytz: Timezone calculations and conversions
- requests: HTTP library for API integration

### Acknowledgments
PropFire was developed with insights from professional forex traders and incorporates best practices from commercial trading platforms. Special recognition to the open-source community for providing the foundational libraries that make this project possible.

---

**Disclaimer**: PropFire is a tool for trade timing and record-keeping. It does not provide trading signals or investment advice. Users are responsible for their own trading decisions and risk management.