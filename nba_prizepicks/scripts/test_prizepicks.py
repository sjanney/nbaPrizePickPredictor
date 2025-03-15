#!/usr/bin/env python
"""Test script for PrizePicks scraper.

This script tests the enhanced PrizePicks scraper functionality,
particularly focusing on scraping NBA data.
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

# Add the parent directory to sys.path to allow imports from the package
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from nba_prizepicks.utils.prizepicks import PrizePicksData

console = Console()


def main():
    """Run the PrizePicks scraper test."""
    console.print(Panel("PrizePicks NBA Scraper Test", style="bold blue"))
    
    # Create a data directory for test results
    data_dir = project_root / "data" / "test"
    os.makedirs(data_dir, exist_ok=True)
    
    console.print(f"[green]Test data will be saved to: {data_dir}[/]")
    
    # Confirm before proceeding
    console.print("\n[yellow]This test will attempt to scrape data from PrizePicks.com.[/]")
    console.print("[yellow]It will use Selenium to automate a Chrome browser.[/]")
    
    if not Confirm.ask("Continue with the test?"):
        console.print("[yellow]Test cancelled.[/]")
        return
    
    # Initialize the PrizePicksData class with use_sample_data=False to force scraping
    console.print("\n[bold blue]Initializing PrizePicksData...[/]")
    prizepicks = PrizePicksData(data_dir=str(data_dir), use_sample_data=False)
    
    # Get the lines
    console.print("\n[bold blue]Attempting to get today's lines...[/]")
    lines = prizepicks.get_todays_lines()
    
    # Display the results
    if lines:
        console.print(f"\n[bold green]Successfully retrieved {len(lines)} lines![/]")
        
        # Group by projection type
        grouped_lines = {}
        for line in lines:
            proj_type = line.get('projection_type', 'Unknown')
            if proj_type not in grouped_lines:
                grouped_lines[proj_type] = []
            grouped_lines[proj_type].append(line)
        
        # Display a summary of lines by projection type
        summary_table = Table(title="Summary of Retrieved Lines")
        summary_table.add_column("Projection Type", style="cyan")
        summary_table.add_column("Count", style="green")
        
        for proj_type, type_lines in grouped_lines.items():
            summary_table.add_row(proj_type, str(len(type_lines)))
            
        console.print(summary_table)
        
        # Display a sample of each projection type
        for proj_type, type_lines in grouped_lines.items():
            console.print(f"\n[bold]Sample of {proj_type} Projections:[/]")
            
            sample_table = Table(title=f"{proj_type} Projections (First 5)")
            sample_table.add_column("Player", style="cyan")
            sample_table.add_column("Team", style="blue")
            sample_table.add_column("Line", style="green")
            sample_table.add_column("Opponent", style="red")
            
            # Show at most 5 lines as a sample
            for line in type_lines[:5]:
                sample_table.add_row(
                    line.get('player_name', 'Unknown'),
                    line.get('team', 'Unknown'),
                    str(line.get('line', 'Unknown')),
                    line.get('opponent', 'Unknown')
                )
                
            console.print(sample_table)
        
        # Save the lines to a file for reference
        output_file = data_dir / "prizepicks_lines.json"
        with open(output_file, 'w') as f:
            json.dump(lines, f, indent=2)
            
        console.print(f"\n[green]Saved lines to: {output_file}[/]")
    else:
        console.print("\n[bold red]Failed to retrieve any lines![/]")
        console.print("[yellow]Check the output above for error messages.[/]")
    
    console.print("\n[bold blue]Test completed.[/]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Test cancelled by user.[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/]")
        sys.exit(1) 