#!/usr/bin/env python
"""Test script for PrizePicks CAPTCHA handling functionality."""

import os
import sys
import time
from rich.console import Console

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nba_prizepicks.utils.prizepicks import PrizePicksData

console = Console()

def test_captcha_handling():
    """Test the CAPTCHA handling functionality in the PrizePicks scraper."""
    console.print("[bold blue]Testing PrizePicks CAPTCHA Handling[/]")
    console.print("[yellow]Note: This test will open a browser and attempt to handle any CAPTCHAs that appear[/]")
    console.print("[yellow]The test is configured to press and hold for ~10 seconds on CAPTCHA challenges[/]")
    
    # Create a PrizePicks data handler with sample data disabled (force live scraping)
    console.print("[blue]Initializing PrizePicks data handler...[/]")
    pp_data = PrizePicksData(use_sample_data=False)
    
    # Create a data directory for storing screenshots if it doesn't exist
    os.makedirs("data/prizepicks", exist_ok=True)
    
    # Call the get_todays_lines method to trigger scraping
    console.print("[bold blue]Starting scraping process - this may take longer if CAPTCHAs need to be solved...[/]")
    start_time = time.time()
    
    try:
        lines = pp_data.get_todays_lines()
        
        elapsed_time = time.time() - start_time
        console.print(f"[blue]Scraping completed in {elapsed_time:.2f} seconds[/]")
        
        if lines:
            console.print(f"[bold green]Successfully retrieved {len(lines)} lines![/]")
            
            # Display a sample of the retrieved lines
            console.print("[blue]Sample of retrieved lines:[/]")
            for line in lines[:5]:  # Show first 5 lines
                console.print(f"- {line['player_name']} ({line['team']}): {line['projection_type']} line {line['line']}")
            
            if len(lines) > 5:
                console.print(f"...and {len(lines) - 5} more.")
            
            # Check screenshots for evidence of CAPTCHA handling
            screenshot_paths = [
                "data/prizepicks/debug_screenshot_after_captcha.png",
                "data/prizepicks/debug_screenshot_after_recaptcha.png",
                "data/prizepicks/debug_screenshot_image_challenge.png"
            ]
            
            captcha_encountered = False
            for path in screenshot_paths:
                if os.path.exists(path):
                    captcha_encountered = True
                    console.print(f"[green]CAPTCHA handling evidence found: {path}[/]")
            
            if captcha_encountered:
                console.print("[bold green]✓ CAPTCHA handling was triggered and appears to have worked successfully![/]")
            else:
                console.print("[yellow]No CAPTCHA challenges were encountered during this test run.[/]")
                console.print("[yellow]This could mean either:[/]")
                console.print("  - The site didn't present a CAPTCHA challenge this time")
                console.print("  - The bot detection was bypassed successfully")
                console.print("  - The scraping method didn't require handling CAPTCHAs")
            
        else:
            console.print("[bold yellow]No data retrieved. Check logs for details.[/]")
            console.print("[yellow]The scraper may have fallen back to sample data if live scraping failed.[/]")
            console.print("[yellow]Check the screenshot files in data/prizepicks/ for evidence of CAPTCHA handling.[/]")
    
    except Exception as e:
        console.print(f"[bold red]Error during testing: {str(e)}[/]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/]")
    
    console.print("\n[bold blue]Test completed.[/]")
    console.print("[blue]Check the screenshots in data/prizepicks/ directory for visual evidence of the scraping process.[/]")

if __name__ == "__main__":
    test_captcha_handling() 