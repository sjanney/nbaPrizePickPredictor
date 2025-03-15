"""PrizePicks data utilities module."""

import os
import json
import requests
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from rich.console import Console
from bs4 import BeautifulSoup
import traceback

# Add selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Autoinstall chromedriver
import chromedriver_autoinstaller

console = Console()


class PrizePicksData:
    """Handles PrizePicks data retrieval and processing."""

    def __init__(self, data_dir="data", use_sample_data=False, manual_captcha=False):
        """Initialize the PrizePicks data handler.
        
        Args:
            data_dir: Directory to store PrizePicks data
            use_sample_data: Whether to use sample data instead of scraping
            manual_captcha: Whether to allow manual solving of CAPTCHAs
        """
        self.data_dir = data_dir
        os.makedirs(f"{data_dir}/prizepicks", exist_ok=True)
        self.use_sample_data = use_sample_data
        self.manual_captcha = manual_captcha
        
        # For demonstration, we'll also create sample data as a fallback
        self._ensure_sample_data()
        
        # URLs for scraping
        self.base_url = "https://app.prizepicks.com/"
        self.api_url = "https://api.prizepicks.com/projections"  # This is a guess, we'd need to find the actual API endpoint
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',  # Prefer JSON if available
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
    def _ensure_sample_data(self):
        """Ensure sample PrizePicks data exists."""
        sample_file = f"{self.data_dir}/prizepicks/sample_lines.json"
        
        if not os.path.exists(sample_file):
            # Create sample data
            sample_data = [
                {
                    "player_name": "LeBron James",
                    "team": "LAL",
                    "opponent": "BOS",
                    "projection_type": "Points",
                    "line": 25.5,
                    "game_time": "2023-11-15T19:30:00"
                },
                {
                    "player_name": "LeBron James",
                    "team": "LAL",
                    "opponent": "BOS",
                    "projection_type": "Rebounds",
                    "line": 8.5,
                    "game_time": "2023-11-15T19:30:00"
                },
                {
                    "player_name": "LeBron James",
                    "team": "LAL",
                    "opponent": "BOS",
                    "projection_type": "Assists",
                    "line": 7.5,
                    "game_time": "2023-11-15T19:30:00"
                },
                {
                    "player_name": "LeBron James",
                    "team": "LAL",
                    "opponent": "BOS",
                    "projection_type": "PRA",
                    "line": 41.5,
                    "game_time": "2023-11-15T19:30:00"
                },
                {
                    "player_name": "Kevin Durant",
                    "team": "PHX",
                    "opponent": "DAL",
                    "projection_type": "Points",
                    "line": 27.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Kevin Durant",
                    "team": "PHX",
                    "opponent": "DAL",
                    "projection_type": "Rebounds",
                    "line": 7.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Kevin Durant",
                    "team": "PHX",
                    "opponent": "DAL",
                    "projection_type": "Assists",
                    "line": 4.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Kevin Durant",
                    "team": "PHX",
                    "opponent": "DAL",
                    "projection_type": "PRA",
                    "line": 39.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Stephen Curry",
                    "team": "GSW",
                    "opponent": "MIN",
                    "projection_type": "Points",
                    "line": 29.5,
                    "game_time": "2023-11-15T22:00:00"
                },
                {
                    "player_name": "Stephen Curry",
                    "team": "GSW",
                    "opponent": "MIN",
                    "projection_type": "Rebounds",
                    "line": 5.5,
                    "game_time": "2023-11-15T22:00:00"
                },
                {
                    "player_name": "Stephen Curry",
                    "team": "GSW",
                    "opponent": "MIN",
                    "projection_type": "Assists",
                    "line": 6.5,
                    "game_time": "2023-11-15T22:00:00"
                },
                {
                    "player_name": "Stephen Curry",
                    "team": "GSW",
                    "opponent": "MIN",
                    "projection_type": "Three-Pointers",
                    "line": 4.5,
                    "game_time": "2023-11-15T22:00:00"
                },
                {
                    "player_name": "Giannis Antetokounmpo",
                    "team": "MIL",
                    "opponent": "CLE",
                    "projection_type": "Points",
                    "line": 31.5,
                    "game_time": "2023-11-15T19:00:00"
                },
                {
                    "player_name": "Giannis Antetokounmpo",
                    "team": "MIL",
                    "opponent": "CLE",
                    "projection_type": "Rebounds",
                    "line": 12.5,
                    "game_time": "2023-11-15T19:00:00"
                },
                {
                    "player_name": "Giannis Antetokounmpo",
                    "team": "MIL",
                    "opponent": "CLE",
                    "projection_type": "Assists",
                    "line": 5.5,
                    "game_time": "2023-11-15T19:00:00"
                },
                {
                    "player_name": "Luka Doncic",
                    "team": "DAL",
                    "opponent": "PHX",
                    "projection_type": "Points",
                    "line": 32.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Luka Doncic",
                    "team": "DAL",
                    "opponent": "PHX",
                    "projection_type": "Rebounds",
                    "line": 8.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Luka Doncic",
                    "team": "DAL",
                    "opponent": "PHX",
                    "projection_type": "Assists",
                    "line": 9.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Luka Doncic",
                    "team": "DAL",
                    "opponent": "PHX",
                    "projection_type": "PRA",
                    "line": 50.5,
                    "game_time": "2023-11-15T20:00:00"
                },
                {
                    "player_name": "Nikola Jokic",
                    "team": "DEN",
                    "opponent": "SAC",
                    "projection_type": "Points",
                    "line": 26.5,
                    "game_time": "2023-11-15T21:00:00"
                },
                {
                    "player_name": "Nikola Jokic",
                    "team": "DEN",
                    "opponent": "SAC",
                    "projection_type": "Rebounds",
                    "line": 12.5,
                    "game_time": "2023-11-15T21:00:00"
                },
                {
                    "player_name": "Nikola Jokic",
                    "team": "DEN",
                    "opponent": "SAC",
                    "projection_type": "Assists",
                    "line": 9.5,
                    "game_time": "2023-11-15T21:00:00"
                }
            ]
            
            with open(sample_file, 'w') as f:
                json.dump(sample_data, f, indent=2)
                
    def _handle_captcha(self, driver):
        """Handle CAPTCHA challenges.
        
        This method detects CAPTCHAs and either handles them automatically or
        allows the user to solve them manually, depending on the setting.
        
        Args:
            driver: The Selenium WebDriver instance
            
        Returns:
            bool: True if captcha was handled successfully, False otherwise
        """
        try:
            console.print("[blue]Checking for CAPTCHA challenges...[/]")
            
            # Wait a moment for any CAPTCHA to appear
            time.sleep(2)
            
            # Common patterns for identifying press-and-hold CAPTCHAs
            captcha_selectors = [
                ".px-captcha-error-button",                 # Common selector for the press & hold button
                "div.px-captcha-error-button",              # Class-based selection
                "div[class*='captcha-button']",             # Partial class match for the button
                "//div[contains(text(), 'Press & Hold')]",  # XPath for text content
                "//div[text()='Press & Hold']",             # Exact text match
                ".px-captcha-container div:nth-child(3)",   # Hierarchical selection
                "#px-captcha-wrapper .px-captcha-container div:nth-child(3)",  # More specific hierarchy
                "div.px-captcha-button",                    # Another potential class
                "button[class*='captcha']",                 # Any button with captcha in class
                "//button[contains(text(), 'Press')]"       # Buttons containing "Press" text
            ]
            
            # Also check for reCAPTCHA and similar checkbox-style CAPTCHAs
            recaptcha_selectors = [
                "iframe[src*='recaptcha']",
                "iframe[title*='recaptcha']",
                "iframe[src*='captcha']",
                "iframe[title*='checkbox']",
                "div.g-recaptcha",
                "div[class*='recaptcha']",
                ".recaptcha-checkbox",
                "#recaptcha-anchor"
            ]
            
            # If manual CAPTCHA solving is enabled
            if self.manual_captcha:
                # Look for any CAPTCHA elements
                captcha_found = self._detect_any_captcha(driver, captcha_selectors, recaptcha_selectors)
                
                if captcha_found:
                    return self._handle_manual_captcha(driver)
                else:
                    console.print("[blue]No CAPTCHA challenge detected.[/]")
                    return False
            else:
                # Try to handle press-and-hold CAPTCHA
                if self._handle_press_and_hold_captcha(driver, captcha_selectors):
                    return True
                    
                # Try to handle checkbox-style reCAPTCHA
                if self._handle_checkbox_captcha(driver, recaptcha_selectors):
                    return True
                    
                console.print("[blue]No CAPTCHA challenge detected.[/]")
                return False
                
        except Exception as captcha_error:
            console.print(f"[yellow]Error handling CAPTCHA: {str(captcha_error)}[/]")
            console.print(f"[dim]{traceback.format_exc()}[/]")
            return False
    
    def _detect_any_captcha(self, driver, captcha_selectors, recaptcha_selectors):
        """Detect if any type of CAPTCHA is present.
        
        Args:
            driver: The Selenium WebDriver instance
            captcha_selectors: List of selectors for press-and-hold CAPTCHAs
            recaptcha_selectors: List of selectors for checkbox CAPTCHAs
            
        Returns:
            bool: True if any CAPTCHA is detected, False otherwise
        """
        # Check for press-and-hold CAPTCHA
        captcha_element = self._find_captcha_element(driver, captcha_selectors)
        if captcha_element:
            return True
        
        # Check for reCAPTCHA iframes
        for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
            try:
                iframe_src = iframe.get_attribute("src") or ""
                iframe_title = iframe.get_attribute("title") or ""
                
                if ("recaptcha" in iframe_src.lower() or 
                    "recaptcha" in iframe_title.lower() or
                    "captcha" in iframe_src.lower() or 
                    "checkbox" in iframe_title.lower()):
                    return True
            except:
                pass
        
        # Check for any element containing CAPTCHA-related text
        page_source = driver.page_source.lower()
        captcha_keywords = ['captcha', 'human', 'bot', 'verify', 'press & hold', 'not a robot']
        for keyword in captcha_keywords:
            if keyword in page_source:
                return True
                
        return False
    
    def _handle_manual_captcha(self, driver):
        """Allow the user to manually solve a CAPTCHA.
        
        Args:
            driver: The Selenium WebDriver instance
            
        Returns:
            bool: True if user indicated they solved the CAPTCHA, False otherwise
        """
        console.print("[bold green]CAPTCHA detected![/]")
        console.print("[bold yellow]Please manually solve the CAPTCHA in the opened browser window.[/]")
        console.print("[yellow]- The browser window should be visible on your screen now")
        console.print("[yellow]- Interact with the CAPTCHA elements to solve it")
        console.print("[yellow]- Take your time - the script will wait until you indicate completion")
        
        # Take a screenshot to help identify what needs to be solved
        screenshot_path = f"{self.data_dir}/prizepicks/captcha_to_solve.png"
        driver.save_screenshot(screenshot_path)
        console.print(f"[blue]Saved a screenshot of the CAPTCHA at: {screenshot_path}[/]")
        
        # Wait for user to solve CAPTCHA
        max_wait_time = 300  # 5 minutes
        wait_interval = 15   # Check every 15 seconds
        
        for i in range(0, max_wait_time, wait_interval):
            seconds_left = max_wait_time - i
            console.print(f"[blue]Waiting for you to solve the CAPTCHA. {seconds_left} seconds remaining.[/]")
            
            # Ask user if they've completed the CAPTCHA
            user_input = input("Have you solved the CAPTCHA? Enter 'y' if solved, or press Enter to wait longer: ")
            if user_input.lower() == 'y':
                console.print("[bold green]User indicated CAPTCHA is solved![/]")
                
                # Take a screenshot after the user solved the CAPTCHA
                screenshot_path = f"{self.data_dir}/prizepicks/post_manual_captcha.png"
                driver.save_screenshot(screenshot_path)
                console.print(f"[blue]Saved post-CAPTCHA screenshot to {screenshot_path}[/]")
                
                # Give a bit of time for any post-CAPTCHA processes to complete
                time.sleep(3)
                return True
                
            # Wait before asking again
            time.sleep(wait_interval)
        
        console.print("[bold yellow]CAPTCHA solving timeout reached. Continuing with the process...[/]")
        return False
    
    def _handle_press_and_hold_captcha(self, driver, captcha_selectors):
        """Handle press-and-hold style CAPTCHA.
        
        Args:
            driver: The Selenium WebDriver instance
            captcha_selectors: List of selectors to try
            
        Returns:
            bool: True if captcha was handled successfully, False otherwise
        """
        captcha_found = False
        captcha_element = None
        
        # First, check if captcha is in an iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                iframe_id = iframe.get_attribute("id") or ""
                iframe_src = iframe.get_attribute("src") or ""
                
                if ("captcha" in iframe_id.lower() or "challenge" in iframe_id.lower() or
                    "captcha" in iframe_src.lower()):
                    console.print(f"[yellow]Found potential CAPTCHA iframe: {iframe_id}[/]")
                    driver.switch_to.frame(iframe)
                    
                    # Look for the press & hold button inside iframe
                    captcha_element = self._find_captcha_element(driver, captcha_selectors)
                    if captcha_element:
                        captcha_found = True
                
                    driver.switch_to.default_content()
                    if captcha_found:
                        break
            except Exception as iframe_error:
                console.print(f"[yellow]Error checking iframe: {str(iframe_error)}[/]")
                driver.switch_to.default_content()
        
        # If not found in iframes, check main page
        if not captcha_found:
            captcha_element = self._find_captcha_element(driver, captcha_selectors)
            captcha_found = captcha_element is not None
        
        if captcha_found and captcha_element:
            console.print("[bold green]Found press-and-hold CAPTCHA challenge! Attempting to solve...[/]")
            
            # Create an action chain to perform the press-and-hold action
            action = webdriver.ActionChains(driver)
            
            # Move to the element
            action.move_to_element(captcha_element)
            
            # Press and hold for around 10 seconds
            # Using a slight randomization to appear more human-like
            hold_duration = random.uniform(9.5, 10.5)
            console.print(f"[blue]Holding button for {hold_duration:.2f} seconds...[/]")
            
            # Click and hold, then pause, then release
            action.click_and_hold(captcha_element)
            action.pause(hold_duration)
            action.release()
            
            # Perform the action
            action.perform()
            
            # Wait longer for challenge to be verified after a long press
            console.print("[blue]Waiting for verification...[/]")
            time.sleep(7)  # Increased waiting time after the longer press
            
            # Take a screenshot after CAPTCHA attempt
            screenshot_path = f"{self.data_dir}/prizepicks/debug_screenshot_after_captcha.png"
            driver.save_screenshot(screenshot_path)
            console.print(f"[blue]Saved post-CAPTCHA screenshot to {screenshot_path}[/]")
            
            return True
        
        return False
    
    def _handle_checkbox_captcha(self, driver, recaptcha_selectors):
        """Handle checkbox-style reCAPTCHA.
        
        Args:
            driver: The Selenium WebDriver instance
            recaptcha_selectors: List of selectors to try
            
        Returns:
            bool: True if captcha was handled successfully, False otherwise
        """
        # First look for reCAPTCHA iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        recaptcha_iframe = None
        
        for iframe in iframes:
            try:
                iframe_src = iframe.get_attribute("src") or ""
                iframe_title = iframe.get_attribute("title") or ""
                
                if ("recaptcha" in iframe_src.lower() or 
                    "recaptcha" in iframe_title.lower() or
                    "captcha" in iframe_src.lower() or 
                    "checkbox" in iframe_title.lower()):
                    recaptcha_iframe = iframe
                    console.print(f"[yellow]Found potential reCAPTCHA iframe: {iframe_title}[/]")
                    break
            except Exception as e:
                console.print(f"[dim]Error checking iframe for reCAPTCHA: {str(e)}[/]")
        
        if recaptcha_iframe:
            try:
                # Switch to the reCAPTCHA iframe
                driver.switch_to.frame(recaptcha_iframe)
                
                # Look for the checkbox or anchor element
                checkbox_selectors = [
                    "div.recaptcha-checkbox-border",
                    "div.recaptcha-checkbox-checkmark",
                    "span.recaptcha-checkbox-border",
                    "span.recaptcha-checkbox",
                    "#recaptcha-anchor",
                    "//div[@role='presentation']",
                    "//div[@class='recaptcha-checkbox-border']",
                    "//span[@id='recaptcha-anchor']"
                ]
                
                checkbox = None
                for selector in checkbox_selectors:
                    try:
                        if selector.startswith("//"):
                            elements = driver.find_elements(By.XPATH, selector)
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for element in elements:
                            if element.is_displayed():
                                checkbox = element
                                console.print(f"[green]Found reCAPTCHA checkbox with selector: {selector}[/]")
                                break
                    except Exception as e:
                        console.print(f"[dim]Error with selector {selector}: {str(e)}[/]")
                
                if checkbox:
                    console.print("[bold green]Found reCAPTCHA checkbox! Clicking...[/]")
                    
                    # Random delays to simulate human behavior
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    # Move to the element with slight randomness
                    action = webdriver.ActionChains(driver)
                    action.move_to_element_with_offset(
                        checkbox, 
                        random.randint(-5, 5),  # Random X offset
                        random.randint(-3, 3)   # Random Y offset
                    )
                    action.pause(random.uniform(0.1, 0.5))
                    action.click()
                    action.perform()
                    
                    console.print("[blue]Waiting for verification...[/]")
                    time.sleep(3)
                    
                    # Check if we need to solve an image challenge
                    if self._check_for_image_challenge(driver):
                        console.print("[yellow]Image challenge detected. This requires human intervention.[/]")
                        console.print("[yellow]Taking a screenshot and pausing for a moment...[/]")
                        
                        # Return to main content to take screenshot
                        driver.switch_to.default_content()
                        
                        # Take screenshot for debugging
                        screenshot_path = f"{self.data_dir}/prizepicks/debug_screenshot_image_challenge.png"
                        driver.save_screenshot(screenshot_path)
                        console.print(f"[blue]Saved image challenge screenshot to {screenshot_path}[/]")
                        
                        # Wait a bit longer to give the impression that we're solving it
                        time.sleep(10)
                        return False
                    
                    # Return to main content
                    driver.switch_to.default_content()
                    
                    # Take screenshot after CAPTCHA attempt
                    screenshot_path = f"{self.data_dir}/prizepicks/debug_screenshot_after_recaptcha.png"
                    driver.save_screenshot(screenshot_path)
                    console.print(f"[blue]Saved post-reCAPTCHA screenshot to {screenshot_path}[/]")
                    
                    return True
                
                # Return to main content if no checkbox found
                driver.switch_to.default_content()
                    
            except Exception as recaptcha_error:
                console.print(f"[yellow]Error handling reCAPTCHA: {str(recaptcha_error)}[/]")
                driver.switch_to.default_content()
        
        return False
    
    def _check_for_image_challenge(self, driver):
        """Check if an image challenge is present after clicking reCAPTCHA checkbox.
        
        Args:
            driver: The Selenium WebDriver instance
            
        Returns:
            bool: True if an image challenge is detected, False otherwise
        """
        # Return to default content to check for image challenge iframe
        driver.switch_to.default_content()
        
        # Look for the image challenge iframe
        try:
            challenge_iframe_selectors = [
                "iframe[title*='challenge']",
                "iframe[src*='bframe']",
                "iframe[name='c-']"
            ]
            
            for selector in challenge_iframe_selectors:
                challenge_iframes = driver.find_elements(By.CSS_SELECTOR, selector)
                if challenge_iframes:
                    console.print(f"[yellow]Found potential image challenge iframe with selector: {selector}[/]")
                    return True
        except Exception as e:
            console.print(f"[dim]Error checking for image challenge: {str(e)}[/]")
        
        return False
    
    def _find_captcha_element(self, driver, selectors):
        """Find CAPTCHA element using multiple selectors.
        
        Args:
            driver: The Selenium WebDriver instance
            selectors: List of selectors to try
            
        Returns:
            WebElement or None: The found CAPTCHA element or None
        """
        for selector in selectors:
            try:
                if selector.startswith("//"):  # XPath selector
                    elements = driver.find_elements(By.XPATH, selector)
                else:  # CSS selector
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        element_text = element.text.lower()
                        # Check for common CAPTCHA text patterns
                        if ("press" in element_text and "hold" in element_text) or \
                           "captcha" in element_text or \
                           "human" in element_text or \
                           "bot" in element_text or \
                           "verify" in element_text:
                            console.print(f"[green]Found CAPTCHA element with text: {element.text}[/]")
                            return element
            except Exception as e:
                console.print(f"[dim]Error with selector {selector}: {str(e)}[/]")
        
        return None

    def _scrape_prizepicks_data(self) -> List[Dict[str, Any]]:
        """Scrape PrizePicks website for current NBA projections using Selenium.
        
        This method navigates to the PrizePicks website, clicks on the NBA category,
        and scrapes the player projections using browser automation.
        
        Returns:
            List of projection dictionaries
        """
        try:
            console.print("[bold blue]Attempting to fetch PrizePicks data...[/]")
            
            # First, try the direct API approach (if there is a public API)
            try:
                console.print("[bold blue]Trying API approach...[/]")
                
                # Make a request to what might be their API endpoint
                response = requests.get(self.api_url, headers=self.headers)
                
                # If successful, parse the JSON response
                if response.status_code == 200:
                    api_data = response.json()
                    
                    # Process the data based on actual API response structure
                    # This is a placeholder - we'd need to study the actual API response format
                    projections = []
                    
                    # Example of processing API data - structure would need to be adjusted
                    if "projections" in api_data:
                        for proj in api_data["projections"]:
                            if proj.get("sport") == "NBA":
                                projections.append({
                                    "player_name": proj.get("player_name", "Unknown"),
                                    "team": proj.get("team", "Unknown"),
                                    "opponent": proj.get("opponent", "Unknown"),
                                    "projection_type": proj.get("stat_type", "Unknown"),
                                    "line": float(proj.get("line", 0)),
                                    "game_time": proj.get("game_time", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
                                })
                    
                    if projections:
                        console.print(f"[bold green]Successfully retrieved {len(projections)} projections via API![/]")
                        return projections
                    
                console.print("[yellow]API approach did not yield results, trying Selenium...[/]")
            except Exception as api_e:
                console.print(f"[yellow]API request failed: {str(api_e)}[/]")
                console.print("[yellow]Falling back to Selenium approach...[/]")
            
            # If API approach fails, use Selenium for browser automation
            console.print("[bold blue]Using Selenium browser automation...[/]")
            
            # Auto-install ChromeDriver
            try:
                console.print("[blue]Checking ChromeDriver installation...[/]")
                chromedriver_path = chromedriver_autoinstaller.install()
                console.print(f"[green]ChromeDriver installed at: {chromedriver_path}[/]")
            except Exception as driver_install_error:
                console.print(f"[yellow]ChromeDriver auto-installation failed: {str(driver_install_error)}[/]")
                console.print("[yellow]Will try to use system ChromeDriver...[/]")
            
            # Set up Chrome options based on manual CAPTCHA setting
            chrome_options = Options()
            
            # Don't use headless mode if manual CAPTCHA solving is enabled
            if not self.manual_captcha:
                chrome_options.add_argument("--headless")  # Run in headless mode
                
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
            
            # Some sites detect headless browsers, so we'll try to mimic a regular browser
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Initialize the WebDriver
            driver = None
            try:
                driver = webdriver.Chrome(options=chrome_options)
                console.print("[green]Browser started successfully[/]")
            except Exception as driver_error:
                console.print(f"[bold red]Failed to start browser: {str(driver_error)}[/]")
                console.print("[yellow]Make sure Chrome and ChromeDriver are properly installed.[/]")
                console.print("[yellow]Trying direct HTML parsing as last resort...[/]")
                return self._fallback_html_parsing()
            
            try:
                # Set page load timeout
                driver.set_page_load_timeout(30)
                
                # Navigate to PrizePicks
                console.print(f"[blue]Navigating to {self.base_url}[/]")
                driver.get(self.base_url)
                
                # Add a custom script to override navigator.webdriver
                # This helps avoid detection as a bot
                driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                """)
                
                # Wait for the page to load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                console.print("[green]Page loaded successfully[/]")
                
                # Check for and handle any CAPTCHA challenges
                self._handle_captcha(driver)
                
                # Wait for a bit to let any initial content load
                time.sleep(5)
                
                # Take a screenshot for debugging - comment this out in production
                screenshot_path = f"{self.data_dir}/prizepicks/debug_screenshot_initial.png"
                driver.save_screenshot(screenshot_path)
                console.print(f"[blue]Saved initial screenshot to {screenshot_path}[/]")
                
                # Wait for any initial popups to load and dismiss them if present
                try:
                    # Look for common popup/overlay elements and close them
                    popup_selectors = [
                        ".modal-close", ".close-button", ".popup-close", 
                        "[data-testid='close-button']", ".close-icon", 
                        "button[aria-label='Close']"
                    ]
                    
                    for selector in popup_selectors:
                        popups = driver.find_elements(By.CSS_SELECTOR, selector)
                        for popup in popups:
                            if popup.is_displayed():
                                popup.click()
                                console.print(f"[green]Closed a popup using selector: {selector}[/]")
                                time.sleep(1)
                                
                                # Check for CAPTCHA after closing popup
                                self._handle_captcha(driver)
                except Exception as popup_error:
                    console.print(f"[yellow]Error handling popups: {str(popup_error)}[/]")
                
                # Find and click on the NBA category
                console.print("[blue]Looking for NBA category...[/]")
                nba_found = False
                
                # Trying various methods to find and click the NBA option
                methods_to_try = [
                    self._try_find_nba_by_selector,
                    self._try_find_nba_by_xpath,
                    self._try_find_nba_by_text,
                    self._try_find_nba_by_navigation
                ]
                
                for method in methods_to_try:
                    if method(driver):
                        nba_found = True
                        break
                
                if not nba_found:
                    console.print("[yellow]Could not find NBA category. Scraping all available projections.[/]")
                else:
                    # Wait after clicking NBA to let content load
                    time.sleep(5)
                    console.print("[green]Waiting for NBA projections to load...[/]")
                
                # Check for CAPTCHA again after clicking NBA (sometimes it appears after navigation)
                self._handle_captcha(driver)
                
                # Take another screenshot after navigation
                screenshot_path = f"{self.data_dir}/prizepicks/debug_screenshot_after_nba.png"
                driver.save_screenshot(screenshot_path)
                console.print(f"[blue]Saved post-navigation screenshot to {screenshot_path}[/]")
                
                # Now find all player projections
                console.print("[blue]Looking for player projections...[/]")
                
                # Give the projections plenty of time to load
                time.sleep(3)  # Additional wait for dynamic content
                
                # Try to find projection elements. These selectors are based on typical patterns, 
                # but the actual ones would need to be determined by inspecting the site's HTML.
                projection_selectors = [
                    # Try various selectors that might indicate projection cards
                    "div[data-testid='projection-presentational']",
                    ".projection-card", ".player-card", ".stat-card",
                    "div[data-testid='selection-card']",
                    "[data-test='game-card']",
                    ".entry-pick", ".pick-container",
                    "div.flex.w-full.flex-col", # Generic flexbox containers that might contain projections
                    "div[role='button']", # Clickable divs often used for selection cards
                    ".player-projection"
                ]
                
                all_elements = []
                for selector in projection_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            console.print(f"[green]Found {len(elements)} elements with selector: {selector}[/]")
                            all_elements.extend(elements)
                    except Exception as selector_error:
                        console.print(f"[yellow]Error with selector {selector}: {str(selector_error)}[/]")
                
                console.print(f"[blue]Found a total of {len(all_elements)} potential projection elements[/]")
                
                # If we found elements, process them
                if all_elements:
                    # Extract visible text from each element for debugging
                    for i, element in enumerate(all_elements[:5]):  # Show first 5 for debugging
                        try:
                            console.print(f"[dim]Element {i+1} text: {element.text}[/]")
                        except:
                            pass
                
                # Check for CAPTCHA again after interacting with elements
                time.sleep(2)
                self._handle_captcha(driver)
                
                # Get the page source after JavaScript has loaded the content
                page_source = driver.page_source
                
                # Save the HTML for analysis
                html_path = f"{self.data_dir}/prizepicks/page_source.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                console.print(f"[blue]Saved page source to {html_path} for analysis[/]")
                
                # Close the browser
                driver.quit()
                
                # Parse the source with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract projection data - try multiple approaches
                projections = []
                
                # 1. Try to find projection cards
                console.print("[blue]Attempting to extract projections from HTML elements...[/]")
                projection_extraction_methods = [
                    self._extract_projections_method1,
                    self._extract_projections_method2,
                    self._extract_projections_method3
                ]
                
                for method in projection_extraction_methods:
                    extracted = method(soup)
                    if extracted:
                        projections = extracted
                        console.print(f"[green]Successfully extracted {len(projections)} projections![/]")
                        break
                
                # 2. If that didn't work, try to find embedded JSON data
                if not projections:
                    console.print("[yellow]Could not extract projections from HTML elements, trying embedded JSON...[/]")
                    projections = self._extract_json_from_html(page_source)
                
                # If we found projections through any method, save and return them
                if projections:
                    console.print(f"[bold green]Successfully extracted {len(projections)} projections![/]")
                    
                    # Filter to keep only NBA projections if possible
                    nba_projections = []
                    for proj in projections:
                        # Check various fields that might indicate NBA
                        is_nba = False
                        
                        # Check league/sport field if it exists
                        league = proj.get('league', proj.get('sport', '')).lower()
                        if 'nba' in league or 'basketball' in league:
                            is_nba = True
                        
                        # Check team names for NBA teams
                        team = proj.get('team', '').upper()
                        nba_teams = ['LAL', 'BOS', 'GSW', 'PHI', 'MIL', 'DAL', 'MIA', 'PHX', 'DEN', 'BKN', 
                                    'CHI', 'ATL', 'LAC', 'TOR', 'NYK', 'CLE', 'MEM', 'MIN', 'NOP', 'POR',
                                    'SAC', 'SAS', 'ORL', 'WAS', 'DET', 'CHA', 'IND', 'OKC', 'HOU', 'UTA']
                        if team in nba_teams:
                            is_nba = True
                        
                        # If we couldn't determine, include it anyway
                        if is_nba or not nba_found:
                            nba_projections.append(proj)
                    
                    # If we filtered and found NBA projections, use those
                    if nba_projections:
                        console.print(f"[green]Filtered to {len(nba_projections)} NBA projections[/]")
                        projections = nba_projections
                    
                    # Save the scraped data
                    scraped_file = f"{self.data_dir}/prizepicks/scraped_lines.json"
                    with open(scraped_file, 'w') as f:
                        json.dump(projections, f, indent=2)
                        
                    return projections
                
                # If we still couldn't find projections, try the fallback method
                console.print("[yellow]Could not extract projections using Selenium. Trying direct HTML parsing...[/]")
                return self._fallback_html_parsing()
                
            except Exception as selenium_error:
                console.print(f"[bold yellow]Selenium error: {str(selenium_error)}[/]")
                # Print traceback for debugging
                console.print(f"[dim]{traceback.format_exc()}[/]")
                
            finally:
                # Make sure the browser is closed
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        
            # If all Selenium approaches failed, try direct HTML parsing as a last resort
            return self._fallback_html_parsing()
            
        except Exception as e:
            console.print(f"[bold red]Error scraping PrizePicks data: {str(e)}[/]")
            console.print(f"[dim]{traceback.format_exc()}[/]")
            return []
    
    def _try_find_nba_by_selector(self, driver):
        """Try to find NBA category using CSS selectors."""
        try:
            # Wait for the sports categories to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    ".sport-container, .category-list, [data-sport='NBA'], .sport-tab, .league-badge"))
            )
            
            # Try different selector strategies to find the NBA category
            nba_selectors = [
                "[data-sport='NBA']", 
                "[data-testid='NBA']",
                "button:contains('NBA')",
                ".sport-badge:contains('NBA')",
                ".league-badge:contains('NBA')",
                "[data-league='NBA']",
                ".category-item:contains('NBA')",
                "div[role='tab']:contains('NBA')"
            ]
            
            for selector in nba_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if "NBA" in element.text or element.get_attribute("data-sport") == "NBA":
                            element.click()
                            console.print(f"[green]Found and clicked NBA using selector: {selector}[/]")
                            
                            # Check for CAPTCHA right after clicking
                            time.sleep(2)  # Wait for potential CAPTCHA to appear
                            self._handle_captcha(driver)
                            
                            return True
                except Exception as e:
                    console.print(f"[dim]Selector {selector} failed: {str(e)}[/]")
            
            return False
        except Exception as e:
            console.print(f"[yellow]Error in _try_find_nba_by_selector: {str(e)}[/]")
            return False
    
    def _try_find_nba_by_xpath(self, driver):
        """Try to find NBA category using XPath expressions."""
        try:
            # Try different XPath expressions
            xpath_expressions = [
                "//button[contains(text(), 'NBA')]",
                "//div[contains(text(), 'NBA')]",
                "//*[contains(text(), 'NBA') and (local-name()='button' or local-name()='div')]",
                "//div[@role='tab' and contains(., 'NBA')]",
                "//div[contains(@class, 'sport') and contains(., 'NBA')]"
            ]
            
            for xpath in xpath_expressions:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.is_displayed() and "NBA" in element.text:
                            element.click()
                            console.print(f"[green]Found and clicked NBA using xpath: {xpath}[/]")
                            
                            # Check for CAPTCHA right after clicking
                            time.sleep(2)  # Wait for potential CAPTCHA to appear
                            self._handle_captcha(driver)
                            
                            return True
                except Exception as e:
                    console.print(f"[dim]XPath {xpath} failed: {str(e)}[/]")
            
            return False
        except Exception as e:
            console.print(f"[yellow]Error in _try_find_nba_by_xpath: {str(e)}[/]")
            return False
    
    def _try_find_nba_by_text(self, driver):
        """Try to find NBA category using text content."""
        try:
            # Get all visible elements
            elements = driver.find_elements(By.CSS_SELECTOR, "*")
            
            nba_elements = []
            for element in elements:
                try:
                    if element.is_displayed() and "NBA" in element.text and len(element.text) < 20:
                        nba_elements.append(element)
                except:
                    continue
            
            if nba_elements:
                for element in nba_elements:
                    if element.is_displayed():
                        element.click()
                        console.print("[green]Found and clicked NBA by text content[/]")
                        
                        # Check for CAPTCHA right after clicking
                        time.sleep(2)  # Wait for potential CAPTCHA to appear
                        self._handle_captcha(driver)
                        
                        return True
            return False
        except Exception as e:
            console.print(f"[yellow]Error in _try_find_nba_by_text: {str(e)}[/]")
            return False
    
    def _try_find_nba_by_navigation(self, driver):
        """Try to navigate to NBA content through URL manipulation."""
        try:
            # First try to find any sport/league navigation elements
            nav_selectors = [
                ".sports-nav", ".league-nav", ".categories", 
                "nav", "[role='tablist']", ".sport-list"
            ]
            
            for selector in nav_selectors:
                try:
                    nav_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if nav_elements:
                        console.print(f"[blue]Found potential navigation with selector: {selector}[/]")
                        
                        # Look for NBA within this navigation
                        for nav in nav_elements:
                            items = nav.find_elements(By.CSS_SELECTOR, "*")
                            for item in items:
                                if "NBA" in item.text and len(item.text) < 20:
                                    item.click()
                                    console.print(f"[green]Found and clicked NBA within navigation: '{item.text}'[/]")
                                    return True
                except:
                    continue
            
            # If that fails, try just clicking elements that look like tabs/buttons
            button_selectors = ["button", "[role='tab']", "[role='button']", ".tab", ".icon-button"]
            for selector in button_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and len(button.text) < 20:
                            # Click buttons that might lead to sports selection
                            button.click()
                            time.sleep(1)
                            
                            # After clicking, check if NBA is now visible
                            if self._try_find_nba_by_text(driver):
                                return True
                except:
                    continue
                
            # Option 1: Try to navigate to a URL pattern that might lead to NBA
            try:
                console.print("[blue]Trying to navigate directly to NBA section...[/]")
                driver.get(f"{self.base_url}nba")
                time.sleep(3)
                
                # Check for CAPTCHA after navigating
                self._handle_captcha(driver)
                
                # Check if we have successfully reached NBA content
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if "nba" in body_text and ("player" in body_text or "projection" in body_text):
                    console.print("[green]Successfully navigated to NBA section[/]")
                    return True
            except Exception as e:
                console.print(f"[yellow]Error in _try_find_nba_by_navigation: {str(e)}[/]")
            
            return False
        except Exception as e:
            console.print(f"[yellow]Error in _try_find_nba_by_navigation: {str(e)}[/]")
            return False
    
    def _extract_projections_method1(self, soup):
        """Extract projections using method 1: looking for specific card structure."""
        try:
            projections = []
            
            # Look for elements that might be projection cards
            projection_elements = soup.select(".projection-card, .player-card, .prop-container, [data-testid='projection']")
            
            for element in projection_elements:
                try:
                    # Extract data from the element - these selectors are guesses
                    player_element = element.select_one(".player-name, .name")
                    team_element = element.select_one(".team")
                    opponent_element = element.select_one(".opponent")
                    projection_type_element = element.select_one(".stat-type, .projection-type")
                    line_element = element.select_one(".line, .value")
                    
                    if player_element and line_element:
                        projection = {
                            "player_name": player_element.text.strip(),
                            "team": team_element.text.strip() if team_element else "Unknown",
                            "opponent": opponent_element.text.strip() if opponent_element else "Unknown",
                            "projection_type": projection_type_element.text.strip() if projection_type_element else "Unknown",
                            "line": float(line_element.text.strip().replace('O', '').replace('U', '')),
                            "game_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                        }
                        projections.append(projection)
                except Exception as element_error:
                    # Skip elements that don't have the expected structure
                    continue
            
            return projections if projections else None
        except Exception as e:
            console.print(f"[yellow]Error in extraction method 1: {str(e)}[/]")
            return None
    
    def _extract_projections_method2(self, soup):
        """Extract projections using method 2: looking for structural patterns in the HTML."""
        try:
            projections = []
            
            # Try to identify elements that contain player names
            player_elements = soup.select("h3, h4, .player-name, .name, [class*='player'], [class*='name']")
            
            for player_element in player_elements:
                try:
                    player_name = player_element.text.strip()
                    
                    # If it looks like a player name (not too short, not too long)
                    if 3 <= len(player_name) <= 30 and ' ' in player_name:
                        # Look for nearby elements that might contain projection info
                        parent = player_element.parent
                        
                        # Look up to 3 levels up for container that might have all the info
                        for _ in range(3):
                            if parent:
                                # Look for projection value
                                line_elements = parent.select(".line, .value, .total, [class*='line'], [class*='value'], [class*='total']")
                                
                                if line_elements:
                                    line_text = line_elements[0].text.strip()
                                    # Extract numbers from text
                                    import re
                                    numbers = re.findall(r'\d+\.?\d*', line_text)
                                    if numbers:
                                        # Look for team/opponent info
                                        team = "Unknown"
                                        opponent = "Unknown"
                                        team_elements = parent.select(".team, [class*='team']")
                                        if team_elements:
                                            team = team_elements[0].text.strip()
                                        
                                        # Look for projection type
                                        proj_type = "Unknown"
                                        type_elements = parent.select(".stat, .type, [class*='stat'], [class*='type']")
                                        if type_elements:
                                            proj_type = type_elements[0].text.strip()
                                        
                                        projection = {
                                            "player_name": player_name,
                                            "team": team,
                                            "opponent": opponent,
                                            "projection_type": proj_type,
                                            "line": float(numbers[0]),
                                            "game_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                                        }
                                        projections.append(projection)
                                        break
                                
                                parent = parent.parent
                except Exception as player_error:
                    continue
            
            return projections if projections else None
        except Exception as e:
            console.print(f"[yellow]Error in extraction method 2: {str(e)}[/]")
            return None
    
    def _extract_projections_method3(self, soup):
        """Extract projections using method 3: looking for text patterns."""
        try:
            projections = []
            
            # Get all visible text and look for patterns
            text_elements = soup.find_all(text=True)
            
            # NBA team abbreviations to look for
            nba_teams = ['LAL', 'BOS', 'GSW', 'PHI', 'MIL', 'DAL', 'MIA', 'PHX', 'DEN', 'BKN', 
                        'CHI', 'ATL', 'LAC', 'TOR', 'NYK', 'CLE', 'MEM', 'MIN', 'NOP', 'POR',
                        'SAC', 'SAS', 'ORL', 'WAS', 'DET', 'CHA', 'IND', 'OKC', 'HOU', 'UTA']
            
            # Common stat types
            stat_types = ['Points', 'Rebounds', 'Assists', 'Pts+Rebs+Asts', 'Pts + Reb + Ast',
                        'PRA', 'Points + Rebounds + Assists', 'Pts+Reb+Ast', 
                        'Three Pointers Made', '3PT', '3-Pointers', 'Threes', '3PM', 'Blocks', 'Steals']
            
            # Get all elements with text
            elements = soup.find_all()
            
            # This method tries to find elements near each other that match the pattern
            # of a player's projection (name, stat type, value)
            for element in elements:
                if not element.text.strip():
                    continue
                    
                # If this element looks like it might contain a player name
                text = element.text.strip()
                
                # Skip very short or very long text
                if len(text) < 3 or len(text) > 30:
                    continue
                    
                # If there's a space, it might be a name
                if ' ' in text:
                    # Now look at siblings and nearby elements for possible projection info
                    container = element.parent
                    
                    # Check if this element and its siblings together form a projection
                    siblings = list(container.contents)
                    all_text = ' '.join(sib.text.strip() if hasattr(sib, 'text') else '' 
                                    for sib in siblings)
                    
                    # Look for patterns in the combined text
                    has_team = any(team in all_text for team in nba_teams)
                    has_stat_type = any(stat in all_text for stat in stat_types)
                    
                    # Look for a number pattern (potential line value)
                    import re
                    numbers = re.findall(r'\d+\.?\d*', all_text)
                    
                    if has_team and has_stat_type and numbers:
                        # Determine the player name, team, stat type, and line
                        player_name = text
                        
                        # Find team
                        team = "Unknown"
                        for nba_team in nba_teams:
                            if nba_team in all_text:
                                team = nba_team
                                break
                        
                        # Find stat type
                        stat_type = "Unknown"
                        for stat in stat_types:
                            if stat in all_text:
                                stat_type = stat
                                break
                        
                        # Get the line value (first number)
                        line = float(numbers[0])
                        
                        projection = {
                            "player_name": player_name,
                            "team": team,
                            "opponent": "Unknown",  # Hard to determine opponent reliably with this method
                            "projection_type": stat_type,
                            "line": line,
                            "game_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                        }
                        projections.append(projection)
            
            return projections if projections else None
        except Exception as e:
            console.print(f"[yellow]Error in extraction method 3: {str(e)}[/]")
            return None
    
    def _extract_json_from_html(self, html_content):
        """Extract JSON data from HTML content, often found in script tags."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            script_tags = soup.find_all('script')
            
            projections = []
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Look for patterns that might indicate projection data
                    json_patterns = [
                        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                        r'window\.__REDUX_STATE__\s*=\s*({.*?});',
                        r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
                        r'window\.APP_DATA\s*=\s*({.*?});'
                    ]
                    
                    for pattern in json_patterns:
                        import re
                        match = re.search(pattern, script_content, re.DOTALL)
                        if match:
                            try:
                                data = json.loads(match.group(1))
                                
                                # Navigate through the data to find projections
                                # This requires knowledge of the actual data structure
                                # Here's a generic approach that tries various common paths
                                candidates = []
                                candidates.append(data.get('projections', []))
                                candidates.append(data.get('data', {}).get('projections', []))
                                candidates.append(data.get('props', []))
                                candidates.append(data.get('entries', []))
                                
                                for candidate in candidates:
                                    if isinstance(candidate, list) and len(candidate) > 0:
                                        # Examine the first item to detect the structure
                                        item = candidate[0]
                                        
                                        # Check if this looks like a projection
                                        if isinstance(item, dict) and ('player' in item or 'line' in item or 'projection' in item):
                                            for proj in candidate:
                                                # Try to extract relevant fields based on common patterns
                                                player_name = None
                                                if 'player' in proj:
                                                    if isinstance(proj['player'], str):
                                                        player_name = proj['player']
                                                    elif isinstance(proj['player'], dict):
                                                        player_name = proj['player'].get('name', None)
                                                
                                                if player_name:
                                                    projection = {
                                                        "player_name": player_name,
                                                        "team": proj.get('team', proj.get('teamAbbreviation', "Unknown")),
                                                        "opponent": proj.get('opponent', proj.get('opponentAbbreviation', "Unknown")),
                                                        "projection_type": proj.get('statType', proj.get('stat', proj.get('type', "Unknown"))),
                                                        "line": float(proj.get('line', proj.get('value', 0))),
                                                        "game_time": proj.get('gameTime', proj.get('gameDate', datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
                                                    }
                                                    projections.append(projection)
                            except Exception as e:
                                console.print(f"[yellow]Error parsing JSON from script: {str(e)}[/]")
                                continue
            
            if projections:
                console.print(f"[bold green]Successfully extracted {len(projections)} projections from embedded JSON![/]")
                return projections
                
            return []
        except Exception as e:
            console.print(f"[yellow]Error extracting JSON from HTML: {str(e)}[/]")
            return []
    
    def _fallback_html_parsing(self):
        """Attempt to parse HTML directly as a last resort."""
        try:
            console.print("[bold blue]Trying direct HTML parsing...[/]")
            
            # Make a request to the base URL
            response = requests.get(self.base_url, headers=self.headers)
            
            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for script tags that might contain the data
            script_tags = soup.find_all('script')
            
            projections = []
            
            for script in script_tags:
                script_content = script.string
                if script_content and ('projections' in script_content or 'prizepicks' in script_content):
                    try:
                        # Look for JSON-like content in the script
                        start_idx = script_content.find('{')
                        end_idx = script_content.rfind('}') + 1
                        
                        if start_idx >= 0 and end_idx > start_idx:
                            json_str = script_content[start_idx:end_idx]
                            data = json.loads(json_str)
                            
                            # Process the data - structure would depend on actual content
                            # This is just an example of how we might extract data
                            if 'projections' in data:
                                for proj in data['projections']:
                                    projections.append({
                                        "player_name": proj.get("playerName", "Unknown"),
                                        "team": proj.get("team", "Unknown"),
                                        "opponent": proj.get("opponent", "Unknown"),
                                        "projection_type": proj.get("statType", "Unknown"),
                                        "line": float(proj.get("line", 0)),
                                        "game_time": proj.get("gameTime", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
                                    })
                    except Exception as script_e:
                        console.print(f"[yellow]Error parsing script content: {str(script_e)}[/]")
                        continue
            
            # If we found projections, return them
            if projections:
                console.print(f"[bold green]Successfully extracted {len(projections)} projections from HTML![/]")
                
                # Save the scraped data
                scraped_file = f"{self.data_dir}/prizepicks/scraped_lines.json"
                with open(scraped_file, 'w') as f:
                    json.dump(projections, f, indent=2)
                    
                return projections
                
            # If we still don't have projections, give up and inform user
            console.print("[yellow]Could not extract projection data using direct HTML parsing.[/]")
            console.print("[yellow]The site may require JavaScript to load data, which is beyond the capability of this scraper.[/]")
            console.print("[yellow]Consider using the official PrizePicks API or a browser automation tool like Selenium.[/]")
            
            return []
            
        except Exception as e:
            console.print(f"[bold red]Error in fallback HTML parsing: {str(e)}[/]")
            return []
                
    def get_todays_lines(self) -> List[Dict[str, Any]]:
        """Get today's PrizePicks lines.
        
        Returns:
            List: PrizePicks lines data
        """
        # Always ensure we have sample data available as fallback
        self._ensure_sample_data()
        sample_file = f"{self.data_dir}/prizepicks/sample_lines.json"
            
        try:
            # Check if user wants to use sample data
            if self.use_sample_data:
                console.print("[yellow]Using sample data instead of scraping.[/]")
                with open(sample_file, 'r') as f:
                    lines = json.load(f)
                return lines
                
            # Try to scrape real data
            console.print("[bold blue]Attempting to get live PrizePicks data...[/]")
            lines = self._scrape_prizepicks_data()
            
            # If scraping failed or no lines were found, fall back to sample data
            if not lines:
                console.print("[bold yellow]Web scraping failed or no lines found.[/]")
                console.print("[bold yellow]This is normal if the website structure has changed or if you're offline.[/]")
                console.print("[bold green]Falling back to sample data to keep the application running.[/]")
                
                with open(sample_file, 'r') as f:
                    lines = json.load(f)
                
                # Let the user know we're using fallback data
                console.print(f"[green]Successfully loaded {len(lines)} sample projection lines.[/]")
                    
            return lines
            
        except Exception as e:
            console.print(f"[bold red]Error getting PrizePicks lines: {str(e)}[/]")
            console.print("[bold yellow]Don't worry! Using sample data instead.[/]")
            
            # Emergency fallback - if anything goes wrong, use sample data
            try:
                with open(sample_file, 'r') as f:
                    lines = json.load(f)
                return lines
            except Exception as sample_error:
                # Ultimate fallback - if even reading sample data fails, create minimal data
                console.print(f"[bold red]Error reading sample data: {str(sample_error)}[/]")
                console.print("[bold green]Creating minimal dataset to keep application running.[/]")
                
                # Return minimal set of lines to prevent application from crashing
                return [
                    {
                        "player_name": "LeBron James",
                        "team": "LAL",
                        "opponent": "BOS",
                        "projection_type": "Points",
                        "line": 25.5,
                        "game_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    }
                ]
                
    def get_player_line(self, player_name: str, projection_type: str) -> Optional[Dict[str, Any]]:
        """Get a specific player's line for a projection type.
        
        Args:
            player_name: Name of the player
            projection_type: Type of projection (e.g., "Points", "PRA")
            
        Returns:
            Dict: Line data or None if not found
        """
        if not player_name:
            console.print("[yellow]Player name not provided.[/]")
            return None
            
        try:
            # Get all lines - this already has fallback mechanisms
            lines = self.get_todays_lines()
            
            if not lines:
                console.print("[yellow]No lines available to search through.[/]")
                return None
                
            # Normalize projection type for comparison
            if projection_type.lower() == "points":
                proj_type = "Points"
            elif projection_type.lower() == "rebounds":
                proj_type = "Rebounds"
            elif projection_type.lower() == "assists":
                proj_type = "Assists"
            elif projection_type.lower() in ["three-pointers", "threes", "3pt"]:
                proj_type = "Three-Pointers"
            elif projection_type.lower() in ["pts+reb+ast", "pra"]:
                proj_type = "PRA"
            else:
                proj_type = projection_type.capitalize()
                
            # Find matching line
            for line in lines:
                if (line.get('player_name', '').lower() == player_name.lower() and
                        line.get('projection_type', '') == proj_type):
                    return line
                    
            console.print(f"[yellow]No line found for {player_name} - {proj_type}.[/]")
            return None
            
        except Exception as e:
            console.print(f"[bold red]Error getting player line: {str(e)}[/]")
            console.print("[yellow]This shouldn't affect the rest of the application.[/]")
            return None
            
    def get_player_lines(self, player_name: str) -> List[Dict[str, Any]]:
        """Get all lines for a specific player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            List: All lines for the player
        """
        if not player_name:
            console.print("[yellow]Player name not provided.[/]")
            return []
            
        try:
            # Get all lines - this already has fallback mechanisms
            lines = self.get_todays_lines()
            
            if not lines:
                console.print("[yellow]No lines available to search through.[/]")
                return []
                
            # Filter lines for the player
            player_lines = [
                line for line in lines
                if line.get('player_name', '').lower() == player_name.lower()
            ]
            
            if not player_lines:
                console.print(f"[yellow]No lines found for player: {player_name}[/]")
                
            return player_lines
            
        except Exception as e:
            console.print(f"[bold red]Error getting player lines: {str(e)}[/]")
            console.print("[yellow]This shouldn't affect the rest of the application.[/]")
            return [] 