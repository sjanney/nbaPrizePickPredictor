"""Player search UI component."""

import json
import os
from typing import Dict, List, Optional
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.spinner import Spinner
from nba_api.stats.static import players


class PlayerSearchUI:
    """UI for searching NBA players."""

    def __init__(self, data_dir="data"):
        """Initialize the player search UI.
        
        Args:
            data_dir: Directory containing player data
        """
        self.console = Console()
        self.data_dir = data_dir
        self.players_cache = None
        
    def _load_players(self) -> List[Dict]:
        """Load player data from NBA API or cache.
        
        Returns:
            List: Player data dictionaries
        """
        # If we already loaded players, use the cached version
        if self.players_cache is not None:
            return self.players_cache
            
        try:
            # Attempt to get all players from NBA API
            self.console.print("[blue]Loading NBA player database...[/]")
            self.players_cache = players.get_players()
            return self.players_cache
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load player data from NBA API: {str(e)}[/]")
            
            # Fall back to sample players if API fails
            self._ensure_sample_data()
            players_file = f"{self.data_dir}/players.json"
            
            try:
                with open(players_file, 'r') as f:
                    player_dict = json.load(f)
                    
                # Convert dictionary to list format like NBA API
                sample_players = [
                    {"full_name": name, "id": int(pid), "is_active": True} 
                    for name, pid in player_dict.items()
                ]
                self.players_cache = sample_players
                return sample_players
            except (FileNotFoundError, json.JSONDecodeError):
                self.console.print("[yellow]Warning: Could not load sample player data.[/]")
                return []
    
    def _ensure_sample_data(self):
        """Ensure sample player data exists."""
        players_file = f"{self.data_dir}/players.json"
        
        if not os.path.exists(players_file):
            # Create sample player data
            os.makedirs(self.data_dir, exist_ok=True)
            
            sample_players = {
                "LeBron James": "2544",
                "Kevin Durant": "201142",
                "Stephen Curry": "201939",
                "Giannis Antetokounmpo": "203507",
                "Luka Doncic": "1629029",
                "Nikola Jokic": "203999",
                "Joel Embiid": "203954",
                "Trae Young": "1629027",
                "Damian Lillard": "203081",
                "Jayson Tatum": "1628369"
            }
            
            with open(players_file, 'w') as f:
                json.dump(sample_players, f)
                
    def search_player(self) -> Optional[Dict[str, str]]:
        """Search for and select a player.
        
        Returns:
            Dict: Selected player data or None if canceled
        """
        all_players = self._load_players()
        
        if not all_players:
            self.console.print("[yellow]No player data available.[/]")
            return None
            
        # Get search term from user
        search_term = Prompt.ask("\nEnter player name (or part of name)")
        search_term_lower = search_term.lower()
        
        # Display spinner while searching
        with self.console.status("[bold blue]Searching for players...[/]", spinner="dots"):
            # Filter players by search term - include both active and inactive
            matches = [
                player for player in all_players
                if search_term_lower in player.get('full_name', '').lower()
            ]
            
            # Sort matches to show active players first, then alphabetically
            matches.sort(key=lambda x: (not x.get('is_active', False), x.get('full_name', '')))
            
            # Limit results to avoid overwhelming the user
            if len(matches) > 20:
                self.console.print(f"[yellow]Found {len(matches)} matches. Showing first 20 results.[/]")
                matches = matches[:20]
        
        if not matches:
            self.console.print("[yellow]No players found matching that search.[/]")
            return None
            
        # Display results
        self.console.print("\n[bold]Search Results:[/]")
        
        results_table = Table(title="Matching Players")
        results_table.add_column("#", style="cyan")
        results_table.add_column("Player Name", style="green")
        results_table.add_column("Status", style="yellow")
        
        for i, player in enumerate(matches, 1):
            status = "[green]Active[/]" if player.get('is_active', False) else "[red]Inactive[/]"
            results_table.add_row(str(i), player.get('full_name', ''), status)
            
        self.console.print(results_table)
        
        # Let user select a player
        if len(matches) == 1:
            choice = 1
        else:
            choice = Prompt.ask(
                "Select a player by number (or 0 to cancel)",
                choices=["0"] + [str(i) for i in range(1, len(matches) + 1)],
                default="1"
            )
            
        if choice == "0":
            return None
            
        # Get the selected player
        selected_player = matches[int(choice) - 1]
        
        return {
            "name": selected_player.get('full_name', ''),
            "id": str(selected_player.get('id', ''))
        } 