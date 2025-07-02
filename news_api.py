import requests
import datetime
import xml.etree.ElementTree as ET
from typing import Dict, Optional

class NewsAPI:
    def __init__(self):
        self.xml_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
        
    def fetch_high_impact_news(self, currency_code: str, target_day: str) -> Optional[Dict]:
        """Fetch high-impact news from Forex Factory XML feed"""
        try:
            # Download XML feed
            response = requests.get(self.xml_url, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Convert day name to weekday number
            day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
            target_weekday = day_map.get(target_day)
            
            if target_weekday is None:
                return None
                
            now = datetime.datetime.now()
            relevant_events = []
            
            # Parse each event
            for event in root.findall('.//event'):
                try:
                    # Extract event data
                    title = event.find('title')
                    country = event.find('country')
                    impact = event.find('impact')
                    date = event.find('date')
                    forecast = event.find('forecast')
                    previous = event.find('previous')
                    
                    # Skip if required fields are missing
                    if None in [title, country, impact, date]:
                        continue
                        
                    title_text = title.text or ""
                    country_text = country.text or ""
                    impact_text = impact.text or ""
                    date_text = date.text or ""
                    forecast_text = forecast.text if forecast is not None else ""
                    previous_text = previous.text if previous is not None else ""
                    
                    # Filter by currency, impact, and future date
                    if (country_text == currency_code and 
                        impact_text == "High" and 
                        date_text):
                        
                        # Parse date (format: "YYYY-MM-DD HH:MM:SS")
                        try:
                            event_datetime = datetime.datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # Try alternative format if first fails
                            try:
                                event_datetime = datetime.datetime.strptime(date_text, "%d-%m-%Y %H:%M:%S")
                            except ValueError:
                                continue
                        
                        # Check if event is in future and on target day
                        if (event_datetime > now and 
                            event_datetime.strftime("%A") == target_day):
                            
                            relevant_events.append({
                                "title": title_text,
                                "date": event_datetime,
                                "datetime": event_datetime,
                                "event_name": title_text,
                                "time": event_datetime.strftime("%H:%M"),
                                "impact": impact_text,
                                "country": country_text,
                                "forecast": forecast_text,
                                "previous": previous_text
                            })
                            
                except (ValueError, AttributeError) as e:
                    continue
                    
            # Return earliest relevant event
            if relevant_events:
                return min(relevant_events, key=lambda x: x["datetime"])
                
            return None
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(error_msg)
            return None
        except ET.ParseError as e:
            error_msg = f"XML parsing error: {str(e)}"
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return None