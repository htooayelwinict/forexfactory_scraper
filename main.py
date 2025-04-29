from scraper import ForexFactoryScraper
import logging
from utils import clean_raw_data, save_raw_data
import pandas as pd
from data_refinary import DataRefinery
from pytz import timezone, all_timezones
import io
from tzlocal import get_localzone
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    scraper = ForexFactoryScraper()
    try:

        # Example: Scrape historical data with user input error handling
        while True:
            try:
                start_year = int(input("Enter the start year: "))
                if start_year < 0:
                    raise ValueError("Year cannot be negative")
                # Add validation for future years
                current_year = pd.Timestamp.now().year
                if start_year > current_year:
                    raise ValueError(f"Start year cannot be in the future (current year: {current_year})")
                break
            except ValueError as e:
                logging.warning(f"Invalid start year. {str(e)}")
        
        while True:
            try:
                start_month = int(input("Enter the start month: "))
                if start_month < 1 or start_month > 12:
                    raise ValueError("Month must be between 1 and 12")
                # Add validation for future months in current year
                if start_year == current_year and start_month > pd.Timestamp.now().month:
                    raise ValueError(f"Cannot scrape future months (current month: {pd.Timestamp.now().month})")
                break
            except ValueError as e:
                logging.warning(f"Invalid start month. {str(e)}")
        
        while True:
            try:
                end_year = int(input("Enter the end year: "))
                if end_year < start_year:
                    raise ValueError
                break
            except ValueError:
                logging.warning("Invalid end year. Please enter a year that is not before the start year.")
        
        while True:
            try:
                end_month = int(input("Enter the end month: "))
                if end_month < 1 or end_month > 12:
                    raise ValueError
                break
            except ValueError:
                logging.warning("Invalid end month. Please enter a number between 1 and 12.")
        raw_data = scraper.scrape_historical_data(start_year=start_year, start_month=start_month, end_year=end_year, end_month=end_month)
        
        if raw_data.empty:
            logging.warning("No data scraped. Exiting.")
            return
        
        # Perform basic cleaning
        cleaned_data = clean_raw_data(raw_data)
        if cleaned_data.empty:
            logging.warning("Data cleaning resulted in an empty DataFrame. Exiting.")
            return
        
        # Save raw data
        saved_raw_file = f'raw_scraped_data_from_{start_year}_{start_month}_to_{end_year}_{end_month}.csv'
        save_raw_data(cleaned_data, saved_raw_file)
        
        logging.info("Scraping and saving raw data completed successfully.")

        # Get IP-based timezone
        ip_timezone = DataRefinery.get_timezone_from_ip()
        system_timezone = str(get_localzone())
        logging.info(f"Your IP-based timezone is: {ip_timezone}")
        logging.info(f"Your system timezone is: {system_timezone}")
        logging.info("\nDisplaying available timezones for reference...")
        DataRefinery.display_available_timezones()
        
        while True:
            try:
                print("\nExample timezone format: 'Asia/Singapore', 'America/New_York', 'Europe/London'")
                print("Your IP-based timezone is: ", ip_timezone, "If you are not sure, use this website to check: https://ipapi.co/json/ ")
                print("Your system timezone is: ", system_timezone)
                local_timezone = input(f"Enter the local timezone (default: {ip_timezone}): ").strip()
                if not local_timezone:  # If empty, use IP-based timezone
                    local_timezone = ip_timezone
                target_timezone = input("Enter the target timezone: ").strip()
                
                # Validate timezones
                if local_timezone not in all_timezones:
                    raise ValueError(f"Invalid local timezone: {local_timezone}")
                if target_timezone not in all_timezones:
                    raise ValueError(f"Invalid target timezone: {target_timezone}")
                break
            except ValueError as e:
                logging.warning(f"{e}. Please enter a valid timezone from the list above.")
        
        refinery = DataRefinery(saved_raw_file)
        refinery.refine_data(local_timezone, target_timezone)
        refined_data = refinery.data

        # Save refined data
        saved_refined_file = f'refined_scraped_data_from_{start_year}_{start_month}_to_{end_year}_{end_month}.csv'
        refinery.save_refined_data(saved_refined_file)

    except Exception as e:
        logging.error(f"An error occurred in main: {e}")
    finally:
        scraper._stop_driver()


if __name__ == "__main__":
    main()
