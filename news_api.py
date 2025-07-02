import requests
from datetime import datetime
from typing import Dict, Optional, List
import time

class NewsAPI:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        self.base_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        
    def fetch_high_impact_events(self, currency: str, target_day: str) -> Optional[Dict]:
        """Fetch high-impact events using ForexFactory JSON API"""
        try:
            cache_key = f"{currency}-{datetime.now().strftime('%Y-%m-%d')}"
            
            # Check cache first
            if cache_key in self.cache:
                cache_time, cached_data = self.cache[cache_key]
                if (time.time() - cache_time) < self.cache_ttl:
                    print(f"DEBUG: Using cached data for {currency}")
                    return cached_data
            
            print(f"DEBUG: Fetching economic calendar from ForexFactory API for {currency}")
            
            # Fetch data from ForexFactory JSON API
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"DEBUG: Retrieved {len(data)} events from ForexFactory API")
            
            # Filter events
            matching_events = []
            now = datetime.now()
            
            for event in data:
                try:
                    # Filter by currency
                    event_currency = event.get('country', '')
                    if not event_currency or event_currency.upper() != currency.upper():
                        continue
                    
                    # Filter by high impact
                    impact = event.get('impact', '')
                    if impact != 'High':
                        continue
                    
                    # Parse event datetime
                    event_date_str = event.get('date', '')
                    event_time_str = event.get('time', '')
                    
                    if not event_date_str:
                        continue
                    
                    try:
                        # Handle ISO datetime format (2025-01-15T08:30:00-04:00)
                        if 'T' in event_date_str:
                            # Parse ISO format and extract date/time
                            date_part = event_date_str.split('T')[0]
                            time_part = event_date_str.split('T')[1].split('-')[0].split('+')[0]
                            
                            event_date = datetime.strptime(date_part, '%Y-%m-%d')
                            
                            if ':' in time_part:
                                hour, minute = map(int, time_part.split(':')[:2])
                                event_date = event_date.replace(hour=hour, minute=minute)
                        else:
                            # Fallback to simple date parsing
                            event_date = datetime.strptime(event_date_str, '%Y-%m-%d')
                            event_date = event_date.replace(hour=12, minute=0)
                            
                    except Exception as date_error:
                        print(f"DEBUG: Date parsing error for {event_date_str}: {date_error}")
                        continue
                    
                    # Only include future events
                    if event_date <= now:
                        continue
                    
                    event_data = {
                        "title": event.get('title', 'Economic Event'),
                        "date": event_date,
                        "datetime": event_date,
                        "currency": currency.upper(),
                        "actual": str(event.get('actual', '')),
                        "forecast": str(event.get('forecast', '')),
                        "previous": str(event.get('previous', '')),
                        "time": event_date.strftime("%H:%M"),
                        "impact": "High"
                    }
                    matching_events.append(event_data)
                    
                    print(f"DEBUG: Found matching event: {event_data['title']} at {event_data['time']}")
                    
                except Exception as e:
                    print(f"DEBUG: Error processing event: {e}")
                    continue
            
            # Cache results
            self.cache[cache_key] = (time.time(), matching_events)
            
            if matching_events:
                matching_events.sort(key=lambda x: x['datetime'])
                next_event = matching_events[0]
                print(f"DEBUG: Returning next event: {next_event['title']} for {currency}")
                return next_event
            else:
                print(f"DEBUG: No matching high-impact events found for {currency}")
                return None
                
        except Exception as e:
            print(f"DEBUG: ForexFactory API fetch failed: {str(e)}")
            print(f"DEBUG: Falling back to session timing")
            return None
            
    def get_high_impact_news(self, currency: str, session: str) -> List[Dict]:
        """Get all high-impact events for the session"""
        try:
            cache_key = f"{currency}-{datetime.now().strftime('%Y-%m-%d')}"
            
            if cache_key in self.cache:
                cache_time, cached_data = self.cache[cache_key]
                if (time.time() - cache_time) < self.cache_ttl:
                    return cached_data
            
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            matching_events = []
            now = datetime.now()
            
            for event in data:
                try:
                    if event.get('country', '').upper() != currency.upper():
                        continue
                    if event.get('impact', '') != 'High':
                        continue
                    
                    event_date_str = event.get('date', '')
                    if not event_date_str:
                        continue
                    
                    if 'T' in event_date_str:
                        date_part = event_date_str.split('T')[0]
                        time_part = event_date_str.split('T')[1].split('-')[0].split('+')[0]
                        event_date = datetime.strptime(date_part, '%Y-%m-%d')
                        if ':' in time_part:
                            hour, minute = map(int, time_part.split(':')[:2])
                            event_date = event_date.replace(hour=hour, minute=minute)
                    else:
                        event_date = datetime.strptime(event_date_str, '%Y-%m-%d')
                        event_date = event_date.replace(hour=12, minute=0)
                    
                    if event_date <= now:
                        continue
                    
                    event_data = {
                        "title": event.get('title', 'Economic Event'),
                        "datetime": event_date,
                        "currency": currency.upper(),
                        "time": event_date.strftime("%H:%M"),
                        "day_name": event_date.strftime("%A"),
                        "impact": "High"
                    }
                    matching_events.append(event_data)
                    
                except Exception:
                    continue
            
            matching_events.sort(key=lambda x: x['datetime'])
            self.cache[cache_key] = (time.time(), matching_events)
            return matching_events
            
        except Exception:
            return []
    
    def fetch_high_impact_news(self, currency_code: str, session: str) -> Optional[Dict]:
        """Main method - delegates to ecocal Calendar"""
        return self.fetch_high_impact_events(currency_code, session)