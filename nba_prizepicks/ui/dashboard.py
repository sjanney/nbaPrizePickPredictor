"""Dashboard for NBA PrizePicks Predictor."""

import time
import sys
import pandas as pd
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.padding import Padding

from nba_prizepicks.data.collector import NBADataCollector
from nba_prizepicks.data.processor import NBADataProcessor
from nba_prizepicks.models.predictor import NBAPredictor
from nba_prizepicks.ui.player_search import PlayerSearchUI
from nba_prizepicks.utils.prizepicks import PrizePicksData


class Dashboard:
    """Main dashboard UI for NBA PrizePicks Predictor."""

    def __init__(self):
        """Initialize the dashboard."""
        self.console = Console()
        self.collector = NBADataCollector()
        self.processor = NBADataProcessor()
        self.predictor = NBAPredictor()
        self.player_search = PlayerSearchUI()
        
        # By default, don't fetch PrizePicks data
        self.compare_with_prizepicks = False
        # By default, use automated CAPTCHA solving
        self.manual_captcha = False
        self.prizepicks = PrizePicksData(use_sample_data=not self.compare_with_prizepicks, manual_captcha=self.manual_captcha)
        
        # Available prediction types
        self.prediction_types = {
            "points": "PTS",
            "rebounds": "REB",
            "assists": "AST",
            "three-pointers": "FG3M",
            "steals": "STL",
            "blocks": "BLK",
            "pts+reb+ast": "PRA"  # Custom combo stat
        }
        
    def _create_layout(self) -> Layout:
        """Create the main dashboard layout.
        
        Returns:
            Layout: Rich layout object
        """
        layout = Layout(name="root")
        
        # Split into header, main content, and footer
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Configure header
        header_text = Text("NBA PrizePicks Predictor", style="bold blue")
        header_text.append("\n")
        header_text.append("Powered by Machine Learning", style="italic cyan")
        
        layout["header"].update(
            Panel(
                Align.center(header_text),
                style="blue",
                border_style="blue"
            )
        )
        
        # Configure footer
        layout["footer"].update(
            Panel(
                Align.center(
                    Text("Press Ctrl+C to exit | Created with ❤️ using Rich and ML", 
                         style="italic")
                ),
                style="blue",
                border_style="blue"
            )
        )
        
        return layout
        
    def display_menu(self) -> str:
        """Display the main menu and get user selection.
        
        Returns:
            str: Selected menu option
        """
        self.console.clear()
        
        # Display data source indicator with more information
        if self.compare_with_prizepicks:
            data_source = "[bold green]WITH PRIZEPICKS COMPARISONS[/]"
            source_note = "[dim](predictions will be compared against PrizePicks lines)[/dim]"
        else:
            data_source = "[yellow]PREDICTIONS ONLY[/]"
            source_note = "[dim](predictions without PrizePicks comparison)[/dim]"
            
        self.console.print(f"\nMode: {data_source} {source_note}")
        
        menu_table = Table(show_header=False, box=None)
        menu_table.add_column(style="cyan")
        menu_table.add_column(style="white")
        
        # Update menu option text to be more descriptive
        menu_items = [
            ("1", "Search for a player"),
            ("2", "View today's PrizePicks lines") if self.compare_with_prizepicks else ("2", "Make prediction for a player"),
            ("3", "Make a prediction"),
            ("4", "Train model with recent data"),
            ("5", "View prediction history"),
            ("6", f"Toggle PrizePicks comparison (current: {'ON' if self.compare_with_prizepicks else 'OFF'})"),
            ("7", "Exit")
        ]
        
        for key, desc in menu_items:
            menu_table.add_row(f"[{key}]", desc)
            
        panel = Panel(
            menu_table,
            title="[bold]Main Menu[/]",
            border_style="blue"
        )
        
        self.console.print("\n")
        self.console.print(panel)
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7"])
        return choice
        
    def run(self):
        """Run the dashboard application."""
        try:
            self.console.clear()
            
            # Display welcome message
            layout = self._create_layout()
            
            with Live(layout, refresh_per_second=4, screen=True):
                time.sleep(2)
            
            while True:
                choice = self.display_menu()
                
                try:
                    if choice == "1":
                        self.search_player()
                    elif choice == "2":
                        self.view_prizepicks_lines()
                    elif choice == "3":
                        self.make_prediction()
                    elif choice == "4":
                        self.train_model()
                    elif choice == "5":
                        self.view_history()
                    elif choice == "6":
                        self.toggle_data_source()
                    elif choice == "7":
                        self.console.print("\n[bold green]Thank you for using NBA PrizePicks Predictor![/]")
                        break
                except ValueError as e:
                    if "Unknown format code" in str(e):
                        self.console.print(f"\n[bold red]Error in formatting:[/] {str(e)}")
                        self.console.print("[yellow]This may be due to unexpected data type. The application will continue.[/]")
                    else:
                        self.console.print(f"\n[bold red]Error:[/] {str(e)}")
                except Exception as e:
                    self.console.print(f"\n[bold red]An error occurred:[/] {str(e)}")
                    self.console.print("[yellow]The application will continue running.[/]")
                    
                # Pause to let user read the output
                self.console.print("\nPress Enter to continue...")
                input()
                
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Application terminated by user.[/]")
            sys.exit(0)
            
    def search_player(self):
        """Search for a player and display their stats."""
        self.console.clear()
        
        self.console.print("[bold]Player Search[/]", style="blue")
        self.console.print("Search for an NBA player to view their stats and make predictions.\n")
        
        # Use the player search UI
        player = self.player_search.search_player()
        
        if player:
            self.console.print(f"\n[bold green]Found player:[/] {player['name']}")
            
            # Display spinner while loading data
            with self.console.status("[bold blue]Loading player data...[/]", spinner="dots"):
                player_df = self.collector.get_player_stats(player['name'], player_id=player['id'])
                
            if player_df is not None and not player_df.empty:
                self.console.print("\n[bold]Recent Games:[/]")
                
                # Process player data
                processed_df = self.processor.process_player_data(player_df)
                
                # Display recent games
                recent_games = processed_df.head(5)
                
                table = Table(title=f"Recent Games for {player['name']}")
                
                # Add columns based on available data
                key_columns = ["GAME_DATE", "MATCHUP", "WL", "MIN", "PTS", "REB", "AST", "STL", "BLK", "FG3M", "TOV", "+/-"]
                
                for col in key_columns:
                    if col in recent_games.columns:
                        table.add_column(col, style="cyan")
                
                # Add rows
                for _, row in recent_games.iterrows():
                    values = [str(row[col]) if col in row.index else "N/A" for col in key_columns]
                    table.add_row(*values)
                    
                self.console.print(table)
                
                # Display season averages
                self.console.print("\n[bold]Season Averages:[/]")
                
                avg_table = Table(title=f"Season Averages for {player['name']}")
                
                # Add stat columns
                stat_cols = ["PTS", "REB", "AST", "STL", "BLK", "FG3M", "MIN"]
                avg_table.add_column("Stat", style="blue")
                avg_table.add_column("Value", style="green")
                
                for stat in stat_cols:
                    if stat in processed_df.columns:
                        avg_value = processed_df[stat].mean()
                        # Use the safer formatting method
                        avg_table.add_row(stat, self._format_value(avg_value))
                        
                self.console.print(avg_table)
                
                # Ask if user wants to make a prediction
                if Confirm.ask("\nWould you like to make a prediction for this player?"):
                    self.make_prediction(player['name'], player['id'])
            else:
                self.console.print("[yellow]No data available for this player.[/]")
        else:
            self.console.print("[yellow]No player found.[/]")
            
    def view_prizepicks_lines(self):
        """View today's PrizePicks lines."""
        self.console.clear()
        
        if not self.compare_with_prizepicks:
            self.console.print("[bold yellow]PrizePicks comparison mode is not enabled.[/]")
            self.console.print("To view PrizePicks lines, go to the main menu and toggle PrizePicks comparison ON.")
            return
            
        self.console.print("[bold]Today's PrizePicks Lines[/]", style="blue")
        
        with self.console.status("[bold blue]Fetching PrizePicks data...[/]", spinner="dots"):
            lines = self.prizepicks.get_todays_lines()
            
        if lines:
            # Debug: Show what data we got in more detail
            self.console.print(f"[dim]Retrieved {len(lines)} PrizePicks lines[/]")
            if lines and len(lines) > 0:
                self.console.print(f"[dim]Sample line: {lines[0]}[/]")
                # Print the keys in the first line to understand structure
                self.console.print(f"[dim]Keys in data: {', '.join(lines[0].keys())}[/]")
            
            # Define valid NBA projection types to filter out non-NBA data
            nba_projection_types = [
                "Points", "Rebounds", "Assists", "PRA", "Three-Pointers",
                "points", "rebounds", "assists", "pra", "three-pointers",
                "three pointers", "pts", "reb", "ast"
            ]
            
            # Force all data to have non-empty fields
            for line in lines:
                if 'player_name' not in line or not line['player_name'] or line['player_name'] == 'Unknown':
                    line['player_name'] = "Sample Player"
                if 'team' not in line or not line['team'] or line['team'] == 'Unknown':
                    line['team'] = "TEAM"
                if 'opponent' not in line or not line['opponent'] or line['opponent'] == 'Unknown':
                    line['opponent'] = "OPP"
                if 'projection_type' not in line or not line['projection_type'] or line['projection_type'] == 'Unknown':
                    line['projection_type'] = "Points"
                if 'line' not in line or not line['line']:
                    line['line'] = 20.5
            
            # Filter to only include NBA projection types
            nba_lines = []
            for line in lines:
                proj_type = line.get('projection_type', '')
                if isinstance(proj_type, str) and any(nba_type.lower() in proj_type.lower() for nba_type in nba_projection_types):
                    nba_lines.append(line)
            
            if not nba_lines:
                self.console.print("[yellow]No NBA-specific lines found in the data.[/]")
                self.console.print("[yellow]Using all data and attempting to filter by projection type.[/]")
                nba_lines = lines
            
            self.console.print(f"[dim]Filtered to {len(nba_lines)} NBA-relevant lines[/]")
            
            # Standardize projection types for grouping
            for line in nba_lines:
                proj_type = line.get('projection_type', 'Points')
                if isinstance(proj_type, str):
                    # Standardize projection type naming
                    if "point" in proj_type.lower() or proj_type.lower() == "pts":
                        line['projection_type'] = "Points"
                    elif "rebound" in proj_type.lower() or proj_type.lower() == "reb":
                        line['projection_type'] = "Rebounds"
                    elif "assist" in proj_type.lower() or proj_type.lower() == "ast":
                        line['projection_type'] = "Assists"
                    elif "three" in proj_type.lower() or "3pt" in proj_type.lower():
                        line['projection_type'] = "Three-Pointers"
                    elif "pra" in proj_type.lower() or all(x in proj_type.lower() for x in ["pts", "reb", "ast"]):
                        line['projection_type'] = "PRA"
                else:
                    line['projection_type'] = "Points"
            
            # Group by projection type
            grouped_lines = {}
            for line in nba_lines:
                proj_type = line.get('projection_type', 'Points')
                if proj_type not in grouped_lines:
                    grouped_lines[proj_type] = []
                grouped_lines[proj_type].append(line)
            
            # Debug: Show how many grouped categories we have
            self.console.print(f"[dim]Grouped into {len(grouped_lines)} projection types: {', '.join(grouped_lines.keys())}[/]")
                
            # Display only NBA-specific projection types
            for proj_type, type_lines in grouped_lines.items():
                # Skip displaying any obviously non-NBA categories
                if proj_type.lower() in ["unknown", "goals", "shots", "saves", "hits", "shots on goal"]:
                    continue
                    
                # Check if we have any valid data for this category
                valid_lines = [line for line in type_lines if all(line.get(key) for key in ['player_name', 'team', 'line', 'opponent'])]
                if not valid_lines:
                    self.console.print(f"[yellow]No valid data for {proj_type} - skipping display[/]")
                    continue
                
                table = Table(title=f"{proj_type} Projections")
                
                table.add_column("Player", style="cyan")
                table.add_column("Team", style="blue")
                table.add_column("Line", style="green")
                table.add_column("Opponent", style="red")
                
                # Debug: Check first line in each group
                if type_lines:
                    self.console.print(f"[dim]First line in {proj_type}: {type_lines[0]}[/]")
                
                # Display log of what's being added to the table
                self.console.print(f"[dim]Adding {len(valid_lines)} rows to the {proj_type} table[/]")
                
                for line in valid_lines:
                    player_name = line.get('player_name', 'Sample Player')
                    team = line.get('team', 'TEAM')
                    line_value = str(line.get('line', 0.0))
                    opponent = line.get('opponent', 'OPP')
                    
                    # Log each row we're adding for debugging
                    self.console.print(f"[dim]Adding row: {player_name} | {team} | {line_value} | {opponent}[/]")
                    
                    table.add_row(
                        player_name,
                        team,
                        line_value,
                        opponent
                    )
                    
                # Only display tables that have actual rows
                if len(table.rows) > 0:
                    self.console.print(table)
                    self.console.print("\n")
                else:
                    self.console.print(f"[yellow]No data to display for {proj_type}[/]")
        else:
            self.console.print("[yellow]No PrizePicks lines available or could not fetch data.[/]")
            
    def _format_value(self, value, format_spec=":.1f"):
        """Safely format a value to a float with specified format.
        
        Args:
            value: The value to format
            format_spec: Format specification string (default: ":.1f")
            
        Returns:
            str: The formatted value
        """
        try:
            # If value is already a string but not a numeric string, just return it
            if isinstance(value, str) and not value.replace('.', '', 1).isdigit():
                return value
                
            # Convert to float and format
            return f"{float(value):{format_spec}}"
        except (ValueError, TypeError):
            # If conversion fails, return as string
            return str(value)

    def make_prediction(self, player_name=None, player_id=None):
        """Make a prediction for a player.
        
        Args:
            player_name: Optional player name (if already selected)
            player_id: Optional player ID (if already selected)
        """
        self.console.clear()
        
        self.console.print("[bold]Make a Prediction[/]", style="blue")
        
        # Get player if not provided
        if not player_name:
            self.console.print("Search for a player to predict their performance.\n")
            player = self.player_search.search_player()
            
            if player:
                player_name = player['name']
                player_id = player['id']
            else:
                self.console.print("[yellow]No player selected.[/]")
                return
                
        self.console.print(f"\n[bold green]Making prediction for:[/] {player_name}")
        
        # Get player data
        with self.console.status(f"[bold blue]Loading data for {player_name}...[/]", spinner="dots"):
            player_df = self.collector.get_player_stats(player_name, player_id=player_id)
            
        if player_df is None or player_df.empty:
            self.console.print("[yellow]No data available for this player.[/]")
            return
            
        # Process player data
        processed_df = self.processor.process_player_data(player_df)
        
        # Let user choose what to predict
        self.console.print("\n[bold]What would you like to predict?[/]")
        
        options = list(self.prediction_types.keys())
        for i, option in enumerate(options, 1):
            self.console.print(f"[{i}] {option.title()}")
            
        choice = Prompt.ask(
            "Select prediction type",
            choices=[str(i) for i in range(1, len(options) + 1)]
        )
        
        # Get stat to predict
        selected_type = options[int(choice) - 1]
        stat_code = self.prediction_types[selected_type]
        
        # Check if it's a composite stat
        if stat_code == "PRA":
            # For composite stats like PTS+REB+AST, we need to predict each component
            # and then add them up
            pra_stats = ["PTS", "REB", "AST"]
            predictions = {}
            
            for stat in pra_stats:
                # Prepare data for prediction
                pred_data = self.processor.prepare_prediction_data(processed_df, stat)
                
                if pred_data is not None:
                    # Make prediction
                    with self.console.status(f"[bold blue]Predicting {stat}...[/]", spinner="dots"):
                        prediction = self.predictor.predict(pred_data, stat)
                        
                    if prediction is not None:
                        predictions[stat] = prediction
                    else:
                        self.console.print(f"[yellow]Could not make prediction for {stat}.[/]")
                        predictions[stat] = 0
                else:
                    self.console.print(f"[yellow]Insufficient data to predict {stat}.[/]")
                    predictions[stat] = 0
                    
            # Calculate composite prediction
            total_prediction = sum(predictions.values())
            
            # Display prediction
            self.console.print("\n[bold]Prediction Results:[/]")
            
            result_table = Table(title=f"Prediction for {player_name}")
            result_table.add_column("Stat", style="blue")
            result_table.add_column("Predicted Value", style="green")
            
            for stat, value in predictions.items():
                result_table.add_row(stat, f"[bold]{self._format_value(value)}[/]")
                
            result_table.add_row("PTS+REB+AST", f"[bold]{self._format_value(total_prediction)}[/]")
            
            self.console.print(result_table)
            
            # Get PrizePicks line for comparison if PrizePicks comparison is enabled
            if self.compare_with_prizepicks:
                self.console.print("\nChecking PrizePicks line...")
                line = self.prizepicks.get_player_line(player_name, "PRA")
                
                if line:
                    pp_value = line.get('line', 0)
                    
                    self.console.print(f"\nPrizePicks line: [bold]{pp_value}[/]")
                    
                    # Recommendation
                    diff = total_prediction - pp_value
                    confidence = abs(diff) / pp_value * 100 if pp_value else 0
                    
                    if diff > 0:
                        recommendation = Panel(
                            f"Predicted: {self._format_value(total_prediction)}\nPrizePicks Line: {pp_value}\nDifference: {self._format_value(diff)}\n\nRecommendation: OVER\nConfidence: {self._format_value(confidence, ':.1f')}%",
                            title="Recommendation",
                            border_style="green"
                        )
                    else:
                        recommendation = Panel(
                            f"Predicted: {self._format_value(total_prediction)}\nPrizePicks Line: {pp_value}\nDifference: {self._format_value(diff)}\n\nRecommendation: UNDER\nConfidence: {self._format_value(confidence, ':.1f')}%",
                            title="Recommendation",
                            border_style="red"
                        )
                        
                    self.console.print(recommendation)
                else:
                    self.console.print("[yellow]No PrizePicks line found for comparison.[/]")
            else:
                # In predictions-only mode, just show the prediction without comparison
                prediction_panel = Panel(
                    f"Predicted PTS+REB+AST: [bold]{self._format_value(total_prediction)}[/]",
                    title="Prediction Result",
                    border_style="blue"
                )
                self.console.print(prediction_panel)
        else:
            # Single stat prediction
            # Prepare data for prediction
            pred_data = self.processor.prepare_prediction_data(processed_df, stat_code)
            
            if pred_data is not None:
                # Make prediction
                with self.console.status(f"[bold blue]Making prediction...[/]", spinner="dots"):
                    prediction = self.predictor.predict(pred_data, stat_code)
                    
                if prediction is not None:
                    # Display prediction
                    self.console.print("\n[bold]Prediction Results:[/]")
                    
                    result_table = Table(title=f"Prediction for {player_name}")
                    result_table.add_column("Stat", style="blue")
                    result_table.add_column("Predicted Value", style="green")
                    
                    result_table.add_row(selected_type.title(), f"[bold]{self._format_value(prediction)}[/]")
                    
                    self.console.print(result_table)
                    
                    # Get PrizePicks line for comparison if PrizePicks comparison is enabled
                    if self.compare_with_prizepicks:
                        self.console.print("\nChecking PrizePicks line...")
                        line = self.prizepicks.get_player_line(player_name, selected_type)
                        
                        if line:
                            pp_value = line.get('line', 0)
                            
                            self.console.print(f"\nPrizePicks line: [bold]{pp_value}[/]")
                            
                            # Recommendation
                            diff = prediction - pp_value
                            confidence = abs(diff) / pp_value * 100 if pp_value else 0
                            
                            if diff > 0:
                                recommendation = Panel(
                                    f"Predicted: {self._format_value(prediction)}\nPrizePicks Line: {pp_value}\nDifference: {self._format_value(diff)}\n\nRecommendation: OVER\nConfidence: {self._format_value(confidence, ':.1f')}%",
                                    title="Recommendation",
                                    border_style="green"
                                )
                            else:
                                recommendation = Panel(
                                    f"Predicted: {self._format_value(prediction)}\nPrizePicks Line: {pp_value}\nDifference: {self._format_value(diff)}\n\nRecommendation: UNDER\nConfidence: {self._format_value(confidence, ':.1f')}%",
                                    title="Recommendation",
                                    border_style="red"
                                )
                                
                            self.console.print(recommendation)
                        else:
                            self.console.print("[yellow]No PrizePicks line found for comparison.[/]")
                    else:
                        # In predictions-only mode, just show the prediction without comparison
                        prediction_panel = Panel(
                            f"Predicted {selected_type.title()}: [bold]{self._format_value(prediction)}[/]",
                            title="Prediction Result",
                            border_style="blue"
                        )
                        self.console.print(prediction_panel)
                else:
                    self.console.print("[yellow]Could not make prediction. Need to train model first.[/]")
            else:
                self.console.print("[yellow]Insufficient data to make prediction.[/]")
                
    def train_model(self):
        """Train prediction models with recent data."""
        self.console.clear()
        
        self.console.print("[bold]Train Prediction Models[/]", style="blue")
        self.console.print("This will train machine learning models for different NBA stat predictions.\n")
        
        # Confirm training
        if not Confirm.ask("This may take some time. Proceed with training?"):
            return
            
        # Choose what to train
        self.console.print("\n[bold]Select stats to train models for:[/]")
        
        options = list(self.prediction_types.items())
        selected_stats = []
        
        for i, (name, code) in enumerate(options, 1):
            if code != "PRA":  # Skip composite stats
                if Confirm.ask(f"Train model for {name.title()}?"):
                    selected_stats.append((name, code))
                    
        if not selected_stats:
            self.console.print("[yellow]No stats selected for training.[/]")
            return
        
        # Choose data collection method
        use_comprehensive = Confirm.ask(
            "\n[bold]Use comprehensive NBA data?[/] (Recommended for better accuracy)\n"
            "This will collect data from all NBA players and games instead of just a few players"
        )
            
        # For each selected stat, collect data and train model
        for stat_name, stat_code in selected_stats:
            self.console.print(f"\n[bold]Training model for {stat_name.title()}...[/]")
            
            if use_comprehensive:
                # Use the new comprehensive data collection
                with self.console.status(f"[bold blue]Collecting comprehensive NBA data for {stat_name.title()}...[/]", spinner="dots"):
                    # Get data for current and previous season
                    training_data = self.collector.get_training_data()
                    
                if training_data is None or training_data.empty:
                    self.console.print(f"[yellow]Could not collect comprehensive training data for {stat_name}.[/]")
                    # Fall back to sample players if comprehensive data collection fails
                    use_comprehensive = False
                else:
                    self.console.print(f"[green]Successfully collected {len(training_data)} game entries for training![/]")
            
            if not use_comprehensive:
                # Fallback to original method with sample players
                with self.console.status(f"[bold blue]Collecting training data for {stat_name} from sample players...[/]", spinner="dots"):
                    # This is a placeholder - in reality we'd collect data for many players
                    player_names = ["LeBron James", "Kevin Durant", "Stephen Curry", "Giannis Antetokounmpo", "Luka Doncic"]
                    training_data_list = []
                    
                    for player in player_names:
                        player_df = self.collector.get_player_stats(player)
                        if player_df is not None and not player_df.empty:
                            processed_df = self.processor.process_player_data(player_df)
                            if processed_df is not None and not processed_df.empty:
                                training_data_list.append(processed_df)
                    
                    if not training_data_list:
                        self.console.print(f"[yellow]No training data available for {stat_name}.[/]")
                        continue
                    
                    # Combine all player data
                    training_data = pd.concat(training_data_list)
            
            # Process the data for training
            with self.console.status(f"[bold blue]Processing data for {stat_name.title()}...[/]", spinner="dots"):
                if use_comprehensive:
                    # Process the comprehensive data differently than player-specific data
                    processed_data = self.processor.process_comprehensive_data(training_data)
                else:
                    # Already processed if using the original method
                    processed_data = training_data
                
                if processed_data is None or processed_data.empty:
                    self.console.print(f"[yellow]Error processing data for {stat_name}.[/]")
                    continue
            
            # Extract features and target
            X, y = self.processor.extract_features(processed_data, stat_code)
            
            if X is not None and y is not None and not X.empty and len(y) > 0:
                # Train the model with progress indicator
                with self.console.status(f"[bold blue]Training model for {stat_name.title()}...[/]", spinner="dots"):
                    metrics = self.predictor.train(X, y, stat_code)
                
                if metrics:
                    self.console.print(f"[bold green]Successfully trained model for {stat_name.title()}![/]")
                    
                    # Display training metrics
                    metrics_table = Table(title=f"Training Metrics for {stat_name.title()}")
                    metrics_table.add_column("Metric", style="cyan")
                    metrics_table.add_column("Value", style="green")
                    
                    for metric, value in metrics.items():
                        metrics_table.add_row(metric, f"{value:.2f}")
                    
                    self.console.print(metrics_table)
                else:
                    self.console.print(f"[yellow]Failed to train model for {stat_name}.[/]")
            else:
                self.console.print(f"[yellow]Insufficient data to train model for {stat_name}.[/]")
                
        self.console.print("\n[bold green]Training complete![/]")
        
    def view_history(self):
        """View prediction history and performance."""
        self.console.clear()
        
        self.console.print("[bold]Prediction History[/]", style="blue")
        self.console.print("View your past predictions and their accuracy.\n")
        
        # Placeholder - in a real app we would store predictions in a database
        self.console.print("[yellow]Prediction history feature coming soon.[/]")
        
    def toggle_data_source(self):
        """Toggle between predictions-only and PrizePicks comparison modes."""
        self.console.clear()
        
        current_mode = "WITH PRIZEPICKS COMPARISONS" if self.compare_with_prizepicks else "PREDICTIONS ONLY"
        new_mode = "PREDICTIONS ONLY" if self.compare_with_prizepicks else "WITH PRIZEPICKS COMPARISONS"
        
        self.console.print(f"[bold]Toggle Prediction Mode[/]", style="blue")
        self.console.print(f"Currently in [bold]{current_mode}[/] mode.")
        
        if new_mode == "WITH PRIZEPICKS COMPARISONS":
            self.console.print("\n[yellow]NOTE:[/] PrizePicks comparison mode requires internet connection and web scraping.")
            self.console.print("[yellow]This may be slower and could potentially violate PrizePicks' terms of service.[/]")
            self.console.print("[yellow]Use at your own risk and only for educational purposes.[/]")
            self.console.print("\n[bold yellow]IMPORTANT NOTE ABOUT WEB SCRAPING:[/]")
            self.console.print("1. First, the app tries to access the PrizePicks API directly")
            self.console.print("2. If that fails, it attempts to extract data from the HTML")
            self.console.print("3. If both fail, it automatically falls back to predictions-only mode")
            
            self.console.print("\n[bold green]CAPTCHA HANDLING:[/]")
            self.console.print("✓ The app can automatically handle 'Press & Hold' CAPTCHA challenges (~10 second hold)")
            self.console.print("✓ It can also attempt to solve simple 'I'm not a robot' checkbox CAPTCHAs")
            self.console.print("✓ If more complex image-based CAPTCHAs appear, it will take screenshots")
            self.console.print("[yellow]Note: Advanced CAPTCHA challenges may still require manual intervention[/]")
            
            # Add option for manual CAPTCHA solving
            self.console.print("\n[bold green]MANUAL CAPTCHA SOLVING:[/]")
            self.console.print("You can choose to manually solve CAPTCHAs instead of relying on automatic solving.")
            self.console.print("This will open a visible browser window when scraping is needed.")
            
            self.manual_captcha = Confirm.ask("Would you like to enable manual CAPTCHA solving?")
            
            if self.manual_captcha:
                self.console.print("[green]Manual CAPTCHA solving enabled. A browser window will open when needed.[/]")
            else:
                self.console.print("[yellow]Using automatic CAPTCHA solving. This may not work for all CAPTCHA types.[/]")
            
            self.console.print("\n[yellow]The application is designed to always work, even if scraping fails.[/]")
            self.console.print("[green]If scraping fails, the application will revert to predictions-only mode.[/]")
            self.console.print("[green]You will still be able to get predictions in either mode.[/]")
            
        else:
            self.console.print("\n[bold green]PREDICTIONS-ONLY MODE:[/]")
            self.console.print("✓ Makes predictions based on player stats without PrizePicks comparisons")
            self.console.print("✓ No web scraping required - works completely offline")
            self.console.print("✓ Faster performance with no waiting for external data")
            
        if Confirm.ask(f"\nSwitch to [bold]{new_mode}[/] mode?"):
            self.compare_with_prizepicks = not self.compare_with_prizepicks
            
            try:
                # Recreate the PrizePicks data handler with the new settings
                self.prizepicks = PrizePicksData(
                    use_sample_data=not self.compare_with_prizepicks,
                    manual_captcha=self.manual_captcha if self.compare_with_prizepicks else False
                )
                
                if self.compare_with_prizepicks:
                    self.console.print(f"\n[bold green]Mode changed to {new_mode}![/]")
                    
                    # Test the data source by fetching some lines
                    with self.console.status("[bold blue]Testing connection to PrizePicks...[/]", spinner="dots"):
                        test_lines = self.prizepicks.get_todays_lines()
                    
                    if test_lines:
                        self.console.print(f"[bold green]Successfully retrieved {len(test_lines)} lines![/]")
                    else:
                        self.console.print("[yellow]Unable to retrieve PrizePicks data. Reverting to predictions-only mode.[/]")
                        self.compare_with_prizepicks = False
                        self.manual_captcha = False
                        self.prizepicks = PrizePicksData(use_sample_data=True, manual_captcha=False)
                else:
                    # When switching to predictions-only, disable manual CAPTCHA
                    self.manual_captcha = False
                    self.console.print(f"\n[bold green]Mode changed to {new_mode}![/]")
                    self.console.print("[green]Using predictions-only mode - no PrizePicks data will be fetched.[/]")
            
            except Exception as e:
                self.console.print(f"[bold red]Error switching modes: {str(e)}[/]")
                self.console.print("[yellow]Reverting to predictions-only mode for reliability.[/]")
                # Ensure we have a valid PrizePicks data handler regardless of errors
                self.prizepicks = PrizePicksData(use_sample_data=True, manual_captcha=False)
                self.compare_with_prizepicks = False
                self.manual_captcha = False
        else:
            self.console.print("\nMode unchanged.") 