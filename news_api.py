import requests
import datetime
from typing import Dict, List, Optional

class NewsAPI:
    def __init__(self):
        self.api_key = "A387iziwZA/GzOzAmY7sPw==JeQiCm920WelbRP7"
        self.base_url = "https://api.api-ninjas.com/v1/economiccalendar"
        self.headers = {"X-Api-Key": self.api_key}
        
    def fetch_high_impact_news(self, currency_code: str, target_day: str) -> Optional[Dict]:
        """Fetch high-impact news for specific currency and day"""
        try:
            # Map currency codes to country codes for API
            currency_map = {
                "USD": "US", "EUR": "EU", "GBP": "GB", 
                "JPY": "JP", "AUD": "AU", "CAD": "CA"
            }
            
            country = currency_map.get(currency_code, "US")
            
            # Make API request
            params = {
                "country": country,
                "importance": "high"
            }
            
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                return self._filter_events_by_day(events, target_day)
            else:
                print(f"API Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
            
    def _filter_events_by_day(self, events: List[Dict], target_day: str) -> Optional[Dict]:
        """Filter events by target day and return next relevant event"""
        if not events:
            return None
            
        # Convert day name to weekday number
        day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        target_weekday = day_map.get(target_day)
        
        if target_weekday is None:
            return None
            
        now = datetime.datetime.now()
        relevant_events = []
        
        for event in events:
            try:
                # Parse event datetime
                event_time = datetime.datetime.strptime(event.get("time", ""), "%Y-%m-%d %H:%M:%S")
                
                # Check if event is on target day and in future
                if event_time.weekday() == target_weekday and event_time > now:
                    relevant_events.append({
                        "event_name": event.get("event", "Unknown Event"),
                        "time": event_time.strftime("%H:%M"),
                        "datetime": event_time,
                        "impact": event.get("importance", "high"),
                        "country": event.get("country", ""),
                        "actual": event.get("actual", ""),
                        "forecast": event.get("forecast", ""),
                        "previous": event.get("previous", "")
                    })
            except (ValueError, TypeError):
                continue
                
        # Return earliest relevant event
        if relevant_events:
            return min(relevant_events, key=lambda x: x["datetime"])
        
        return None