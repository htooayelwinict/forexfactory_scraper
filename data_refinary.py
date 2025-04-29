import pandas as pd
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone, all_timezones
from tzlocal import get_localzone
import requests
import logging

# Define a class for data refinement
class DataRefinery:
    # Initialize the class with a filename
    def __init__(self, filename):
        self.filename = filename
        self.data = pd.read_csv(filename)

    # Method to refine the data
    def refine_data(self, local_timezone, target_timezone):
        # Ensure 'year' column is of type int
        self.data['year'] = self.data['year'].astype(pd.Int64Dtype())

        # Function to convert date format
        def format_date(date_str):
            if pd.isna(date_str) or date_str == "N/A":
                return date_str
            else:
                try:
                    # Assuming the format is 'Day Month Day_number'
                    date_name, month_name, day_number = date_str.split()
                    # Convert month name to number
                    month_number = pd.to_datetime(month_name, format='%b').month
                    # Format the new date string as "month-day"
                    return f"{month_number}-{int(day_number)}"
                except ValueError:  # Handle unexpected formats
                    return "Invalid Date"

        # Apply the date formatting function
        self.data['date'] = self.data['date'].apply(format_date)

        # Function to convert time zones
        def convert_to_timezone(year, date_str, time_str, target_timezone):
            try:
                # Combine year, date, and time into a single datetime object
                datetime_str = f"{year}-{date_str} {time_str}"
                # Create a datetime object assuming Singapore timezone
                local_tz = timezone(local_timezone)
                local_dt = local_tz.localize(datetime.strptime(datetime_str, '%Y-%m-%d %I:%M%p'))
                # Convert to the target timezone
                target_tz = timezone(target_timezone)
                target_dt = local_dt.astimezone(target_tz)
                return target_dt.strftime('%Y-%m-%d %I:%M %p')
            except Exception as e:
                return f"Conversion error: {e}"

        converted_time = self.data.apply(lambda row: convert_to_timezone(row['year'], row['date'], row['time'], target_timezone), axis=1)

        # Function to split converted_time into separate columns
        def split_converted_time(converted_time_str):
            if "Conversion error" in converted_time_str or converted_time_str == "N/A":
                return None, None, None
            try:
                converted_dt = datetime.strptime(converted_time_str, '%Y-%m-%d %I:%M %p')
                return converted_dt.year, converted_dt.strftime('%m-%d'), converted_dt.strftime('%I:%M %p')
            except ValueError:
                return None, None, None

        # Apply the split function
        self.data[['year', 'date', 'time']] = converted_time.apply(
            lambda x: pd.Series(split_converted_time(x)))

        # Convert converted_year to integer type explicitly
        self.data['year'] = self.data['year'].astype(pd.Int64Dtype())

        # This line of code is using the forward fill method to replace missing values in the 'year', 'date', and 'time' columns.
        # The forward fill method replaces missing values with the value from the previous row. This is useful for filling gaps in time series data.
        # For example, if there's a missing 'date' value in a row, it will be replaced with the 'date' value from the previous row.
        self.data[['year', 'date', 'time']] = self.data[['year', 'date', 'time']].apply(lambda x: x.ffill())

        # after forward filling, we need to convert the 'year' column to integer type explicitly and remove the 'N/A' values in the event column
        self.data['year'] = self.data['year'].astype(pd.Int64Dtype())
        self.data = self.data[self.data['event'] != 'N/A']

    # Method to display the refined data
    def display_refined_data(self):
        print(self.data)

    # Method to save the refined data to a file
    def save_refined_data(self, filename):
        self.data.to_csv(filename, index=False)

    _cached_timezone = None
    
    @classmethod
    def get_timezone_from_ip(cls, max_retries=3, timeout=5, retry_delay=1):
        """Get timezone based on IP address with multiple API fallbacks and retry logic
        
        Args:
            max_retries (int): Maximum number of retries per API endpoint
            timeout (int): Timeout in seconds for API requests
            retry_delay (int): Delay in seconds between retries
            
        Returns:
            str: Timezone string
        """
        # Return cached result if available
        if cls._cached_timezone:
            return cls._cached_timezone
            
        # List of API endpoints to try, ordered by reliability and rate limits
        api_endpoints = [
            # GeoJS base URL returns text with timezone info
            ('https://get.geojs.io', lambda r: r.text.split('Timezone: ')[-1].split('\n')[0].strip()),
            # Fallback to ipapi.co which has stricter rate limits
            ('https://ipapi.co/timezone', lambda r: r.text.strip())
        ]
        
        import time
        
        for endpoint, parser in api_endpoints:
            for attempt in range(max_retries):
                try:
                    response = requests.get(endpoint, timeout=timeout)
                    
                    # Handle rate limits
                    if response.status_code == 429:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                            logging.warning(
                                f"Rate limited by {endpoint}. "
                                f"Waiting {wait_time}s before retry {attempt + 1}/{max_retries}"
                            )
                            time.sleep(wait_time)
                        continue
                        
                    if response.status_code == 200:
                        timezone_str = parser(response)
                        if timezone_str and timezone_str in all_timezones:
                            cls._cached_timezone = timezone_str
                            return timezone_str
                    
                    # If we get here, either status code wasn't 200 or timezone was invalid
                    if attempt < max_retries - 1:
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {endpoint}. "
                            f"Status: {response.status_code}. Retrying in {retry_delay}s..."
                        )
                        time.sleep(retry_delay)
                        
                except requests.RequestException as e:
                    if attempt < max_retries - 1:
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {endpoint}. "
                            f"Error: {str(e)}. Retrying in {retry_delay}s..."
                        )
                        time.sleep(retry_delay)
                    continue
            
            # Add delay between different API endpoints
            if endpoint != api_endpoints[-1][0]:  # Don't sleep after last endpoint
                time.sleep(retry_delay)
            logging.warning(f"All attempts failed for {endpoint}. Trying next API...")
        
        # Cache and return system timezone as last resort
        system_tz = str(get_localzone())
        cls._cached_timezone = system_tz
        logging.error("All API endpoints failed to detect timezone. Using system timezone as last resort.")
        return system_tz

    @classmethod
    def display_available_timezones(cls):
        """Display all available timezones in a formatted way"""
        # Get timezone only if not already cached
        if not cls._cached_timezone:
            ip_timezone = cls.get_timezone_from_ip()
        else:
            ip_timezone = cls._cached_timezone
            
        system_timezone = str(get_localzone())
        print(f"\nYour IP-based timezone is: {ip_timezone}")
        print(f"Your system timezone is: {system_timezone}")
        print("\nAvailable timezones by region:")
        
        # Get current time to calculate offsets
        now = datetime.now()
        
        # Group timezones by region and calculate GMT offset
        regions = {}
        for tz_name in all_timezones:
            region = tz_name.split('/')[0]
            if region not in regions:
                regions[region] = []
                
            # Calculate GMT offset
            tz = timezone(tz_name)
            offset = tz.utcoffset(now)
            if offset is not None:
                hours = int(offset.total_seconds() / 3600)
                minutes = int((offset.total_seconds() % 3600) / 60)
                
                # Format the GMT offset string
                if minutes == 0:
                    gmt_str = f"(GMT{'+' if hours >= 0 else ''}{hours:02d}:00)"
                else:
                    gmt_str = f"(GMT{'+' if hours >= 0 else ''}{hours:02d}:{minutes:02d})"
                    
                # Get the city name (last part of timezone string)
                city = tz_name.split('/')[-1].replace('_', ' ')
                
                regions[region].append((tz_name, f"{gmt_str} {city}"))
        
        # Print timezones sorted by region and offset
        for region, timezones in sorted(regions.items()):
            print(f"\n{region}:")
            # Sort by GMT offset and city name
            timezones.sort(key=lambda x: x[1])  # Sort by the formatted string
            for tz_name, formatted_name in timezones:
                print(formatted_name)

# Example usage
if __name__ == "__main__":
    DataRefinery.display_available_timezones()
    target_timezone = input("Enter the target timezone: ")
    refinery = DataRefinery('raw_scraped_data_from_2021_12_to_2023_2.csv')
    refinery.refine_data('Asia/Rangoon', target_timezone)
    refinery.display_refined_data()
    refinery.save_refined_data('processed_data_with_converted_time.csv')
