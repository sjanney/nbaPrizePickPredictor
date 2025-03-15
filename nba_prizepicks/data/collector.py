"""NBA data collector module."""

import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from nba_api.stats.endpoints import playergamelog, commonplayerinfo, leaguegamefinder

console = Console()


class NBADataCollector:
    """Collects and processes NBA data for predictions."""

    def __init__(self, data_dir="data"):
        """Initialize the NBA data collector.
        
        Args:
            data_dir: Directory to store collected data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.season = self._get_current_season()
        
    def _get_current_season(self):
        """Get the current NBA season string.
        
        Returns:
            str: Current season in format "YYYY-YY"
        """
        today = datetime.now()
        # NBA season typically starts in October
        if today.month >= 10:
            return f"{today.year}-{str(today.year + 1)[-2:]}"
        else:
            return f"{today.year - 1}-{str(today.year)[-2:]}"
            
    def collect_player_data(self, player_id, days_back=30):
        """Collect game log data for a specific player.
        
        Args:
            player_id: NBA API player ID
            days_back: Number of days back to collect data
            
        Returns:
            DataFrame: Player game data
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Collecting player data..."),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading...", total=100)
            
            try:
                # Get player info
                player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                player_info_df = player_info.get_data_frames()[0]
                progress.update(task, advance=20)
                
                # Get player game logs
                game_logs = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=self.season,
                    season_type_all_star="Regular Season"
                )
                game_logs_df = game_logs.get_data_frames()[0]
                progress.update(task, advance=80)
                
                # Save data
                os.makedirs(f"{self.data_dir}/players", exist_ok=True)
                game_logs_df.to_csv(f"{self.data_dir}/players/{player_id}_games.csv", index=False)
                
                # Add delay to avoid hitting API rate limits
                time.sleep(1)
                
                return game_logs_df
                
            except Exception as e:
                console.print(f"[bold red]Error collecting data for player {player_id}:[/] {str(e)}")
                return None
                
    def collect_recent_games(self, days_back=7):
        """Collect recent NBA games data.
        
        Args:
            days_back: Number of days back to collect data
            
        Returns:
            DataFrame: Recent games data
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]Collecting recent games..."),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading...", total=100)
            
            try:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                
                # Format dates for NBA API
                start_date_str = start_date.strftime("%m/%d/%Y")
                end_date_str = end_date.strftime("%m/%d/%Y")
                
                # Get recent games
                games = leaguegamefinder.LeagueGameFinder(
                    date_from_nullable=start_date_str,
                    date_to_nullable=end_date_str,
                    league_id_nullable="00"  # NBA
                )
                games_df = games.get_data_frames()[0]
                progress.update(task, advance=100)
                
                # Save data
                games_df.to_csv(f"{self.data_dir}/recent_games.csv", index=False)
                
                return games_df
                
            except Exception as e:
                console.print(f"[bold red]Error collecting recent games:[/] {str(e)}")
                return None
                
    def get_player_stats(self, player_name, player_id=None):
        """Get a player's stats by name or ID.
        
        Args:
            player_name: Name of the player
            player_id: Optional NBA API player ID (if available)
            
        Returns:
            DataFrame: Player stats data
        """
        try:
            # If player_id is provided, use it directly
            if player_id:
                console.print(f"[green]Fetching data for player ID: {player_id}[/]")
                return self.collect_player_data(player_id)
            
            # Otherwise try to find player ID from name
            players_file = f"{self.data_dir}/players.json"
            
            if os.path.exists(players_file):
                with open(players_file, 'r') as f:
                    players_dict = json.load(f)
                
                if player_name.lower() in [name.lower() for name in players_dict.keys()]:
                    for name, pid in players_dict.items():
                        if name.lower() == player_name.lower():
                            player_id = pid
                            break
                        
                    console.print(f"[green]Found player ID: {player_id}[/]")
                    return self.collect_player_data(player_id)
            
            # If we couldn't find the player ID, try using the NBA API directly
            try:
                from nba_api.stats.static import players
                player_info = players.find_players_by_full_name(player_name)
                
                if player_info and len(player_info) > 0:
                    # Use the first match (should be most relevant)
                    player_id = player_info[0]['id']
                    console.print(f"[green]Found player ID using NBA API: {player_id}[/]")
                    return self.collect_player_data(player_id)
            except Exception as e:
                console.print(f"[yellow]Error searching NBA API: {str(e)}[/]")
            
            # If we still can't find the player, return None
            console.print(f"[yellow]Player {player_name} not found in database.[/]")
            return None
            
        except Exception as e:
            console.print(f"[bold red]Error getting player stats:[/] {str(e)}")
            return None

    def collect_comprehensive_data(self, season=None, days_back=60, season_type="Regular Season"):
        """Collect comprehensive game data from NBA players for better model training.
        
        This method uses player game logs to get data from multiple players,
        providing a much more robust dataset for training prediction models.
        
        Args:
            season: NBA season in format "YYYY-YY" (default: current season)
            days_back: Number of days back to collect data if not specifying full season
            season_type: "Regular Season", "Playoffs", or "All"
            
        Returns:
            DataFrame: Comprehensive game data for all players
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Collecting comprehensive NBA data..."),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading...", total=100)
            
            try:
                # Use current season if not specified
                if not season:
                    season = self.season
                
                console.print(f"[bold]Collecting data for {season} season...[/]")
                
                # We'll collect data for top players - in a production app
                # you would want to get a more complete list of players
                sample_players = [
                    # Sample of players from different positions
                    # MVP candidates
                    {"id": 2544, "name": "LeBron James"},
                    {"id": 201939, "name": "Stephen Curry"},
                    {"id": 201142, "name": "Kevin Durant"},
                    {"id": 203507, "name": "Giannis Antetokounmpo"},
                    {"id": 203999, "name": "Nikola Jokic"},
                    {"id": 1629029, "name": "Luka Doncic"},
                    {"id": 1628369, "name": "Jayson Tatum"},
                    {"id": 1628378, "name": "Donovan Mitchell"},
                    {"id": 203081, "name": "Damian Lillard"},
                    {"id": 202681, "name": "Kyrie Irving"},
                    # Centers
                    {"id": 203954, "name": "Joel Embiid"},
                    {"id": 1626164, "name": "Devin Booker"},
                    {"id": 1628384, "name": "Bam Adebayo"},
                    {"id": 1627783, "name": "Pascal Siakam"},
                    {"id": 1629627, "name": "Ja Morant"},
                    # Guards
                    {"id": 1627936, "name": "Dejounte Murray"},
                    {"id": 201950, "name": "Jrue Holiday"},
                    {"id": 1628973, "name": "Trae Young"},
                    {"id": 1627750, "name": "Jamal Murray"},
                    {"id": 203078, "name": "Anthony Davis"},
                    # Young stars
                    {"id": 1629639, "name": "Zion Williamson"},
                    {"id": 1629027, "name": "Shai Gilgeous-Alexander"},
                    {"id": 1631093, "name": "Paolo Banchero"},
                    {"id": 1630162, "name": "Anthony Edwards"},
                    {"id": 1630224, "name": "LaMelo Ball"},
                ]
                
                progress.update(task, advance=10)
                
                all_player_data = []
                
                # Use date range if specified
                if days_back:
                    # Calculate date range for messages (actual date filtering is done by NBA API)
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days_back)
                    start_date_str = start_date.strftime("%m/%d/%Y")
                    end_date_str = end_date.strftime("%m/%d/%Y")
                    console.print(f"Date range: {start_date_str} to {end_date_str}")
                
                # Collect data for each player
                total_players = len(sample_players)
                for i, player in enumerate(sample_players):
                    progress.update(task, description=f"Collecting data for {player['name']}...")
                    
                    try:
                        # Get player game log
                        gamelog = playergamelog.PlayerGameLog(
                            player_id=player['id'],
                            season=season,
                            season_type_all_star=season_type
                        )
                        player_df = gamelog.get_data_frames()[0]
                        
                        if player_df is not None and not player_df.empty:
                            # Add player name for easier identification
                            player_df['PLAYER_NAME'] = player['name']
                            all_player_data.append(player_df)
                        
                        # Add delay to avoid hitting API rate limits
                        time.sleep(0.6)
                    except Exception as e:
                        console.print(f"[yellow]Error collecting data for {player['name']}: {str(e)}[/]")
                    
                    # Update progress
                    progress.update(task, advance=80/total_players)
                
                if not all_player_data:
                    console.print("[yellow]No player data collected.[/]")
                    return None
                
                # Combine all player data
                comprehensive_df = pd.concat(all_player_data)
                
                # Save the data
                os.makedirs(f"{self.data_dir}/comprehensive", exist_ok=True)
                filename = f"{self.data_dir}/comprehensive/{season}_{season_type.replace(' ', '_')}.csv"
                comprehensive_df.to_csv(filename, index=False)
                
                console.print(f"[bold green]Successfully collected data for {len(comprehensive_df)} game entries from {len(all_player_data)} players![/]")
                progress.update(task, advance=10)
                
                return comprehensive_df
                
            except Exception as e:
                console.print(f"[bold red]Error collecting comprehensive data:[/] {str(e)}")
                return None

    def get_training_data(self, seasons=None, use_cached=True):
        """Get comprehensive training data for model training.
        
        This method fetches data for multiple seasons to provide a robust
        training dataset for our prediction models.
        
        Args:
            seasons: List of seasons to include (default: current + previous season)
            use_cached: Whether to use cached data if available
            
        Returns:
            DataFrame: Combined training data from specified seasons
        """
        try:
            if not seasons:
                # Default to current and previous season
                current_year = int(self.season.split('-')[0])
                prev_season = f"{current_year-1}-{str(current_year)[-2:]}"
                seasons = [self.season, prev_season]
            
            console.print(f"[bold]Collecting training data for seasons: {', '.join(seasons)}[/]")
            
            all_data = []
            for season in seasons:
                filename = f"{self.data_dir}/comprehensive/{season}_Regular_Season.csv"
                
                # Check if we have cached data
                if use_cached and os.path.exists(filename):
                    console.print(f"[green]Loading cached data for {season}[/]")
                    season_data = pd.read_csv(filename)
                else:
                    console.print(f"[blue]Fetching new data for {season}[/]")
                    season_data = self.collect_comprehensive_data(season=season, days_back=None)
                
                if season_data is not None and not season_data.empty:
                    all_data.append(season_data)
            
            if not all_data:
                console.print("[yellow]No training data could be collected.[/]")
                return None
            
            # Combine all seasons
            combined_data = pd.concat(all_data)
            console.print(f"[bold green]Successfully prepared training dataset with {len(combined_data)} entries![/]")
            
            return combined_data
            
        except Exception as e:
            console.print(f"[bold red]Error getting training data:[/] {str(e)}")
            return None 