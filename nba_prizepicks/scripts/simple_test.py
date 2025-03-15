#!/usr/bin/env python
"""Simplified test script for PrizePicks scraper.

This script provides a basic test of the PrizePicks scraper without user confirmations.
"""

import os
import sys
import json
from pathlib import Path
from rich.console import Console

# Add the parent directory to sys.path to allow imports from the package
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from nba_prizepicks.utils.prizepicks import PrizePicksData

console = Console()


def main():
    """Run the simplified PrizePicks scraper test."""
    console.print("[bold blue]Starting PrizePicks NBA Scraper Test[/]")
    
    # Create a data directory for test results
    data_dir = project_root / "data" / "test"
    os.makedirs(data_dir, exist_ok=True)
    
    console.print(f"[green]Test data will be saved to: {data_dir}[/]")
    
    # Initialize the PrizePicksData class with use_sample_data=False to force scraping
    console.print("\n[bold blue]Initializing PrizePicksData...[/]")
    prizepicks = PrizePicksData(data_dir=str(data_dir), use_sample_data=False)
    
    # Get the lines
    console.print("\n[bold blue]Attempting to get today's lines...[/]")
    lines = prizepicks.get_todays_lines()
    
    # Display the results
    if lines:
        console.print(f"\n[bold green]Successfully retrieved {len(lines)} lines![/]")
        
        # Group lines by player name to see how many unique players we found
        players = {}
        for line in lines:
            player_name = line.get('player_name', 'Unknown')
            if player_name not in players:
                players[player_name] = []
            players[player_name].append(line)
        
        console.print(f"[green]Found projections for {len(players)} unique players[/]")
        
        # Display a few player names as a sample
        sample_players = list(players.keys())[:5]
        console.print("[green]Sample players:[/]")
        for player in sample_players:
            console.print(f"[cyan]- {player}[/]")
        
        # Save the lines to a file for reference
        output_file = data_dir / "prizepicks_lines.json"
        with open(output_file, 'w') as f:
            json.dump(lines, f, indent=2)
            
        console.print(f"\n[green]Saved lines to: {output_file}[/]")
    else:
        console.print("\n[bold red]Failed to retrieve any lines![/]")
        console.print("[yellow]The scraper fell back to sample data.[/]")
    
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