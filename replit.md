# Web Scraping Data Extraction Tool

## Overview

This is a Streamlit-based web application designed to scrape numerical data from websites. The application allows users to input URLs and extract numerical values from web pages using Beautiful Soup for HTML parsing and regular expressions for data extraction. The tool is built with Python and focuses on converting unstructured web content into structured numerical data that can be analyzed or exported.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - Chosen for rapid prototyping and ease of deployment
- **User Interface**: Simple web-based interface for URL input and data display
- **Data Presentation**: Built-in Streamlit components for displaying scraped data

### Backend Architecture
- **Language**: Python 3.x
- **Web Scraping**: requests library for HTTP requests, BeautifulSoup for HTML parsing
- **Data Processing**: pandas and numpy for data manipulation and analysis
- **Pattern Matching**: Regular expressions for numerical value extraction

### Data Processing Pipeline
1. URL validation using urllib.parse
2. HTTP request with browser-like headers to avoid blocking
3. HTML content parsing with BeautifulSoup
4. Numerical data extraction using regex patterns
5. Data structuring and presentation

## Key Components

### Core Modules
- **URL Validation (`is_valid_url`)**: Ensures proper URL format before processing
- **Number Extraction (`extract_numbers_from_text`)**: Uses regex to identify and extract numerical values from text
- **Web Scraper (`scrape_website_data`)**: Main scraping function with error handling and browser mimicking

### Data Processing Features
- Support for decimal and negative numbers
- Flexible CSS selector support for targeted scraping
- Timeout protection for web requests
- User-Agent spoofing to avoid bot detection

## Data Flow

1. User inputs URL through Streamlit interface
2. Application validates URL format
3. HTTP request sent with appropriate headers
4. HTML content parsed using BeautifulSoup
5. Numerical values extracted using regex patterns
6. Data processed and displayed in Streamlit interface
7. Results can be exported or further analyzed

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework
- **requests**: HTTP library for web scraping
- **beautifulsoup4**: HTML/XML parsing
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **urllib**: URL parsing utilities

### Web Technologies
- Targets standard HTML websites
- Handles CSS selectors for targeted extraction
- Compatible with various web page structures

## Deployment Strategy

### Local Development
- Streamlit development server for testing
- Standard Python virtual environment setup
- Requirements.txt for dependency management

### Production Considerations
- Streamlit Cloud or similar platform deployment
- Environment variable management for configuration
- Rate limiting considerations for web scraping
- Respect for robots.txt and website terms of service

## Changelog

- July 05, 2025. Initial setup
- July 05, 2025. Added Kapalıçarşı gold price integration with Has Altın calculation feature
- July 05, 2025. Enhanced with HTML table output for calculation results

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Features Added

### Complete Turkish Gold Price Calculator
- 5 different gold types: Quarter, Half, Full, Cumhuriyet, and 24 Ayar
- Real-time data from Kapalıçarşı and Canlı Altın Fiyatları websites
- Specific calculation formulas for each gold type
- Responsive 2x2 grid card layout with orange theme
- Professional styling with centered headers and clear pricing display

### Data Sources Integration
- Kapalıçarşı: Has Altın, Cumhuriyet Altın prices
- Canlı Altın Fiyatları: Gram Altın prices for 24 Ayar calculation
- Real-time price updates with error handling
- Multiple parsing strategies for reliable data extraction