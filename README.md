# NBA PrizePicks Predictor

A machine learning application to predict NBA PrizePicks selections with high accuracy, featuring a beautiful terminal UI built with Rich.

## Features

- Real-time NBA data fetching using NBA API
- Machine learning models for accurate predictions of player performance
- Beautiful and interactive terminal UI using Rich
- Comprehensive testing suite
- Performance tracking to improve model accuracy
- Enhanced web scraping capability for PrizePicks data

## Installation

There are two ways to install the application:

### Option 1: Using the installation script (Recommended)

Run the installation script which will set up a virtual environment and install all dependencies:

```
python install.py
```

If you're not already in a virtual environment, the script will create one and prompt you to activate it.

### Option 2: Manual installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Install the required packages:
   ```
   pip install -e ".[scraper,tests]"
   ```

## Usage

Run the application:
```
python run.py
```

### Prediction Modes

The application offers two modes for making predictions:

#### Predictions-Only Mode
- Makes predictions based on player stats without comparing to PrizePicks lines
- Works completely offline - no internet connection required
- Faster performance with no web scraping
- Great for getting pure statistical predictions

#### PrizePicks Comparison Mode
- Fetches live data from PrizePicks to compare with your model's predictions
- Provides betting recommendations (OVER/UNDER) with confidence ratings
- Requires an internet connection
- May be slower due to web scraping
- Could potentially violate PrizePicks' terms of service (use at your own risk)
- Web scraping may fail if the site structure changes

### CAPTCHA Handling

When using PrizePicks comparison mode, the application includes advanced CAPTCHA handling capabilities:

#### Automatic CAPTCHA Solving
- Automatically handles "Press & Hold" CAPTCHA challenges with a 10-second hold duration
- Attempts to solve simple "I'm not a robot" checkbox CAPTCHAs
- Takes screenshots of CAPTCHAs it encounters for debugging purposes
- Falls back to predictions-only mode if CAPTCHA solving fails

#### Manual CAPTCHA Solving (Recommended)
- When enabled, opens a visible browser window when scraping data
- Allows you to manually solve any CAPTCHA that appears
- Waits for your confirmation that the CAPTCHA has been solved
- More reliable than automatic solving, especially for complex CAPTCHAs

To test the automatic CAPTCHA handling functionality:

```bash
# Run the dedicated automatic CAPTCHA test script
python nba_prizepicks/scripts/test_captcha_handling.py
```

To test the manual CAPTCHA solving functionality:

```bash
# Run the dedicated manual CAPTCHA test script
python nba_prizepicks/scripts/test_manual_captcha.py
```

This will open a visible browser window and allow you to interact with any CAPTCHAs that appear. The script will wait for your confirmation after you've solved the CAPTCHA.

You can also enable manual CAPTCHA solving in the main application by selecting "Toggle PrizePicks comparison" from the menu and choosing "yes" when asked about manual CAPTCHA solving.

**Enhanced Web Scraping:**

Our application now includes a powerful Selenium-based web scraper for PrizePicks data:

1. **Automated Browser Control**: Uses Selenium to automate a Chrome browser, enabling the scraper to handle JavaScript-heavy websites like PrizePicks
2. **Multiple Detection Methods**: Employs various techniques to locate and extract NBA data, including CSS selectors, XPath, and pattern matching
3. **Intelligent NBA Filtering**: Automatically detects and filters for NBA-specific projections
4. **Automatic ChromeDriver Installation**: Includes chromedriver-autoinstaller to simplify setup
5. **Anti-Detection Measures**: Implements techniques to avoid bot detection
6. **Comprehensive Error Handling**: Multiple fallback methods if one approach fails
7. **Debug Information**: Saves screenshots and HTML content during scraping for easy troubleshooting

**Robust Fallback Mechanism:**

Don't worry about web scraping failures! The application includes a robust fallback system:

1. When using live data mode, the application first attempts to fetch data from the PrizePicks website using several advanced methods:
   - Direct API access attempt
   - Selenium browser automation
   - HTML content extraction
   - Pattern matching in embedded JSON
2. If all web scraping approaches fail, the application automatically falls back to sample data
3. All application features will continue to work normally with the sample data
4. You'll see clear console messages informing you when fallback occurs

### Testing the Web Scraper

To test the PrizePicks web scraper independently:

```
python nba_prizepicks/scripts/simple_test.py
```

This will run the scraper in test mode and output detailed information about the process. If successful, it will save the scraped data to `data/test/prizepicks_lines.json`.

For more detailed testing with interactive confirmation:

```
python nba_prizepicks/scripts/test_prizepicks.py
```

## Testing

Run the test suite:
```
pytest
```

Generate coverage report:
```
pytest --cov=nba_prizepicks
```

The test suite includes specific tests to verify the fallback mechanism works correctly.