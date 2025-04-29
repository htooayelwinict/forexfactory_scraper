# ForexFactory Scraper

Unlock the power of historical economic data with the ForexFactory Scraper! This Python bot, built with Selenium and BeautifulSoup, helps you gather and analyze historical forex calendar data from ForexFactory.

## System Architecture

The Forex Factory Scraper is designed with a modular architecture for maintainability and extensibility. Each component has a specific responsibility in the data scraping and processing pipeline.

### System Overview Diagram
```mermaid
flowchart TD
    %% Main Components
    User([User]) --> |"Run Script\nInput Parameters"| Main["main.py\n(Orchestrator)"]
    
    %% Main Script Flow
    Main --> |"Initialize"| Scraper["scraper.py\n(ForexFactoryScraper)"]
    Main --> |"Process Data"| Utils["utils.py\n(Data Cleaning Utilities)"]
    Main --> |"Refine Data"| Refinery["data_refinary.py\n(DataRefinery)"]
    
    %% Scraper Implementation
    Scraper --> |"Selenium WebDriver"| FF["ForexFactory Website"]
    Scraper --> |"Fetch Calendar Data"| FF
    FF --> |"Raw HTML"| Scraper
    Scraper --> |"BeautifulSoup\nParsing"| RawData[("Raw Data\n(DataFrame)")]
    
    %% Data Processing
    RawData --> |"clean_raw_data()"| Utils
    Utils --> |"Validation\nCleaning"| CleanData[("Cleaned Data\n(DataFrame)")]
    
    %% Data Storage
    CleanData --> |"save_raw_data()"| RawFile["Raw CSV File"]
    
    %% Data Refinement
    RawFile --> |"Load Data"| Refinery
    Refinery --> |"Timezone API"| IP["IP-based Timezone\nDetection"]
    Refinery --> |"refine_data()"| ProcessedData[("Refined Data\n(DataFrame)")]
    ProcessedData --> |"save_refined_data()"| RefinedFile["Refined CSV File"]
    
    %% Data Flow Styling
    classDef main fill:#f9f,stroke:#333,stroke-width:2px
    classDef component fill:#bbf,stroke:#33f,stroke-width:2px
    classDef data fill:#dfd,stroke:#080,stroke-width:1px
    classDef file fill:#ffd,stroke:#b80,stroke-width:1px
    classDef external fill:#eee,stroke:#aaa,stroke-width:1px
    
    class Main main
    class Scraper,Utils,Refinery component
    class RawData,CleanData,ProcessedData data
    class RawFile,RefinedFile file
    class FF,IP external
```

### Class Structure
```mermaid
classDiagram
    class ForexFactoryScraper {
        -driver: WebDriver
        -proxy: str
        +__init__(proxy=None)
        +_start_driver()
        +_stop_driver()
        +_wait_for_element(by, value, timeout=30)
        +_parse_row(row, current_date, year)
        +scroll_and_load(scroll_increment=500, scroll_pause=1)
        +scrape_data(url)
        +scrape_historical_data(start_year, start_month, end_year, end_month)
    }
    
    class Utilities {
        +save_raw_data(df, filename)
        +validate_columns(df, required_columns)
        +clean_raw_data(df)
    }
    
    class DataRefinery {
        -filename: str
        -data: DataFrame
        -_cached_timezone: str
        +__init__(filename)
        +refine_data(local_timezone, target_timezone)
        +display_refined_data()
        +save_refined_data(filename)
        +get_timezone_from_ip() [static]
        +display_available_timezones() [static]
    }
    
    class MainModule {
        +main()
    }
    
    MainModule --> ForexFactoryScraper : creates
    MainModule --> Utilities : uses
    MainModule --> DataRefinery : creates
    ForexFactoryScraper ..> "1" DataFrame : produces
    Utilities ..> DataFrame : processes
    DataRefinery ..> DataFrame : refines
```

### Process Flow
```mermaid
sequenceDiagram
    actor User
    participant Main as main.py
    participant Scraper as ForexFactoryScraper
    participant Selenium as Selenium WebDriver
    participant BS as BeautifulSoup
    participant Utils as utils.py
    participant Refinery as DataRefinery
    participant API as Timezone API
    
    User->>Main: Run script
    Main->>User: Prompt for start_year
    User->>Main: Enter start_year
    Main->>User: Prompt for start_month
    User->>Main: Enter start_month
    Main->>User: Prompt for end_year
    User->>Main: Enter end_year
    Main->>User: Prompt for end_month
    User->>Main: Enter end_month
    
    Main->>Scraper: Create scraper instance
    
    Main->>Scraper: scrape_historical_data(start_year, start_month, end_year, end_month)
    activate Scraper
    
    loop For each month in date range
        Scraper->>Selenium: Initialize WebDriver
        Scraper->>Selenium: Navigate to URL with month/year
        Scraper->>Selenium: Wait for calendar table
        Scraper->>Selenium: Scroll to load content
        Selenium-->>Scraper: Page content
        Scraper->>BS: Parse HTML
        BS-->>Scraper: Soup object
        Scraper->>BS: Extract calendar data
        BS-->>Scraper: Calendar rows
        
        loop For each row in calendar table
            Scraper->>Scraper: _parse_row()
        end
        
        Scraper->>Selenium: Close WebDriver
    end
    
    Scraper-->>Main: raw_data (DataFrame)
    deactivate Scraper
    
    Main->>Utils: clean_raw_data(raw_data)
    activate Utils
    Utils->>Utils: validate_columns()
    Utils->>Utils: Replace empty strings with NaN
    Utils->>Utils: Fill NaN with 'N/A'
    Utils-->>Main: cleaned_data (DataFrame)
    deactivate Utils
    
    Main->>Utils: save_raw_data(cleaned_data, filename)
    Utils->>Utils: Save to CSV
    
    Main->>Refinery: Create DataRefinery instance with raw data file
    
    Main->>API: Get IP-based timezone
    API-->>Main: IP timezone
    
    Main->>User: Display timezone information
    User->>Main: Enter local_timezone
    User->>Main: Enter target_timezone
    
    Main->>Refinery: refine_data(local_timezone, target_timezone)
    activate Refinery
    Refinery->>Refinery: Convert date format
    Refinery->>Refinery: Convert time zones
    Refinery->>Refinery: Format data
    Refinery-->>Main: refined_data (DataFrame)
    deactivate Refinery
    
    Main->>Refinery: save_refined_data(filename)
    Refinery->>Refinery: Save to CSV
    
    Main-->>User: Notify completion
```

### Data Flow
```mermaid
flowchart TD
    subgraph Input
        UserInput["User Input Parameters:
        - start_year
        - start_month
        - end_year
        - end_month
        - local_timezone
        - target_timezone"]
    end
    
    subgraph WebSources
        FF["Forex Factory Calendar
        https://www.forexfactory.com/calendar"]
        IPAPI["IP Geolocation API
        - get.geojs.io
        - ipapi.co/timezone"]
    end
    
    subgraph DataTransformation
        RawDF["Raw DataFrame
        - year: int
        - date: str
        - time: str
        - currency: str
        - impact: str
        - event: str
        - actual: str
        - forecast: str
        - previous: str"]
        
        CleanDF["Cleaned DataFrame
        - Empty strings → NaN → 'N/A'
        - Validated columns"]
        
        RefinedDF["Refined DataFrame
        - Reformatted date (month-day)
        - Timezone converted times
        - Timezone converted dates
        - Forward filled missing values"]
    end
    
    subgraph DataStorage
        RawCSV["Raw CSV File
        raw_scraped_data_from_{start_year}_{start_month}_to_{end_year}_{end_month}.csv"]
        
        RefinedCSV["Refined CSV File
        refined_scraped_data_from_{start_year}_{start_month}_to_{end_year}_{end_month}.csv"]
    end
    
    %% Flow Connections
    UserInput -->|"Input parameters"| FF
    FF -->|"HTML data"| RawDF
    UserInput -->|"Date range"| RawDF
    IPAPI -->|"Timezone data"| RefinedDF
    
    RawDF -->|"clean_raw_data()"| CleanDF
    CleanDF -->|"save_raw_data()"| RawCSV
    RawCSV -->|"Load in DataRefinery"| RefinedDF
    UserInput -->|"timezone parameters"| RefinedDF
    RefinedDF -->|"save_refined_data()"| RefinedCSV
    
    %% Styling
    classDef input fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    classDef source fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    classDef transform fill:#c8e6c9,stroke:#43a047,stroke-width:2px
    classDef storage fill:#ffecb3,stroke:#ff8f00,stroke-width:2px
    
    class UserInput input
    class FF,IPAPI source
    class RawDF,CleanDF,RefinedDF transform
    class RawCSV,RefinedCSV storage
```

## Key Components

### 1. ForexFactoryScraper (scraper.py)
The core web scraping component:
- Uses Selenium WebDriver with anti-detection measures (random user agents, headless mode)
- Implements explicit waits for reliable element loading
- Extracts calendar data with BeautifulSoup parsing
- Supports month-by-month scraping over a date range
- Handles pagination and dynamic content loading

### 2. Data Cleaning Utilities (utils.py)
Handles data validation and cleaning:
- Validates required columns exist in the DataFrame
- Cleans raw data by converting empty strings to NaN
- Fills missing values with 'N/A' for consistency
- Provides functions to save raw data to CSV

### 3. DataRefinery (data_refinary.py)
Processes and transforms the scraped data:
- Reformats dates for consistency (month-day format)
- Converts timestamps between timezones
- Detects user's timezone from IP using geolocation APIs
- Handles missing values with forward filling
- Saves the refined data to CSV files

### 4. Main Script (main.py)
Orchestrates the entire process:
- Validates user input parameters
- Handles the execution flow
- Coordinates between components
- Provides error handling and user feedback

## Requirements
- **Python 3.7+**: Because we believe in staying up-to-date!
- **Google Chrome**: The fastest way to browse the web.
- **ChromeDriver**: The magic behind the data scraping journey.
- **Internet connection for IP-based timezone detection**: This is necessary for the bot to detect your IP-based timezone and automatically configure the data scraping process.

## Installation
Getting started is a breeze! Follow these simple steps and you're on your way to mastering forex insights.

1. **Clone the Repository**: Begin your journey by cloning the repository.
```bash
git clone https://github.com/htooayelwinict/forexfactory_scraper.git
cd forexfactory_scraper
```

2. **Create a Python Virtual Environment**: Ensure you have a clean and isolated Python environment for your project.
```bash
python -m venv forex_factory_scraper_venv
source forex_factory_scraper_venv/bin/activate  # On Windows: forex_factory_scraper_venv\Scripts\activate
```

3. **Install Dependencies**: We've made the process seamless with a single command.
```bash
pip install -r requirements.txt 
``` 
or fix with chatgpt :P 

4. **Set Up Chrome Browser**: Ensure you have the latest version of Chrome installed.

## How to Use

1. **Run the Bot**: Let the adventure begin!
```bash
python main.py
```

2. **Input Data Range**: Select the start and end years and months for your data.
   - **Start Year**: Enter the start year (validates against future years)
   - **Start Month**: Enter the start month (1-12, validates against future months)
   - **End Year**: Enter the end year (must not be before start year)
   - **End Month**: Enter the end month (1-12)

3. **Configure Timezones**:
   - **Local Timezone**: The script automatically detects:
     - Your IP-based timezone
     - Your system timezone
   - **Target Timezone**: You can choose:
     - Local timezone (defaults to IP-based if left empty)
     - Target timezone for data conversion

4. **Output Files**:
Two CSV files will be generated:
   - `raw_scraped_data_from_YYYY_MM_to_YYYY_MM.csv` (original data)
   - `refined_scraped_data_from_YYYY_MM_to_YYYY_MM.csv` (timezone-adjusted data)

## Data Structure

### Raw Data Columns
- **year**: Year of the event
- **date**: Date in "Day Month Day_number" format (e.g., "Mon Jan 1")
- **time**: Time of the event in local timezone
- **currency**: Currency code affected by the event
- **impact**: Expected impact level (High, Medium, Low)
- **event**: Economic event name
- **actual**: Actual value reported
- **forecast**: Forecasted value
- **previous**: Previous reported value

### Refined Data Columns
- **year**: Year of the event (in target timezone)
- **date**: Date in "month-day" format (e.g., "1-15")
- **time**: Time converted to target timezone in 12-hour format
- **currency**: Currency code affected by the event
- **impact**: Expected impact level (High, Medium, Low)
- **event**: Economic event name
- **actual**: Actual value reported
- **forecast**: Forecasted value
- **previous**: Previous reported value

## Technical Features

1. **Robust Web Scraping**:
   - Anti-bot detection mechanisms
   - Scroll-and-wait strategy for dynamic content
   - Error handling for network issues

2. **Smart Timezone Management**:
   - Multiple fallback API endpoints for timezone detection
   - Error handling for API rate limits
   - Comprehensive timezone validation

3. **Data Quality Assurance**:
   - Input validation to prevent errors
   - Consistent handling of missing values
   - Error recovery mechanisms

## Important Notes
- The scraper only works with historical data (cannot scrape future dates)
- Timezone format examples: 'Asia/Singapore', 'America/New_York', 'Europe/London'
- For timezone verification, you can use: https://ipapi.co/json/

## Error Handling
The script includes comprehensive error handling for:
- Invalid date inputs
- Future date validation
- Timezone validation
- Data scraping and processing errors
- Network connection issues
- API rate limiting

## Acknowledgements
A big shoutout to Tech With Tim for the inspiration and guiding me through the art of web scraping.

## Get in Touch
We love hearing from fellow traders and tech enthusiasts! Connect with me:

- ***telegram*** @htooayelwin
- ***telegram*** @lewisaeofburma

## License
This project is licensed under the GNU General Public License v3.0, because we believe in open source and ensuring that no one uses this project for their benefit.

## Shoutout to KweeBoss and the 1BullBear Family!
We raise our hats to KweeBoss and the incredible 1BullBear Family for inspiring this project. May this tool serve you well as you navigate the exciting seas of forex trading! 🚀
