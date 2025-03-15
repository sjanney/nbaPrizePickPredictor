"""Data processor for NBA statistics."""

import pandas as pd
import numpy as np
from rich.console import Console

console = Console()


class NBADataProcessor:
    """Process NBA data for machine learning models."""

    def __init__(self):
        """Initialize the NBA data processor."""
        pass

    def process_player_data(self, player_df):
        """Process player game log data for prediction.
        
        Args:
            player_df: DataFrame containing player game data
            
        Returns:
            DataFrame: Processed data with engineered features
        """
        if player_df is None or player_df.empty:
            console.print("[bold red]Error:[/] No player data to process")
            return None
            
        try:
            # Make a copy to avoid modifying the original
            df = player_df.copy()
            
            # Convert date strings to datetime
            if 'GAME_DATE' in df.columns:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
            
            # Sort by date
            df = df.sort_values(by='GAME_DATE', ascending=False)
            
            # Create rolling averages for key stats
            # Last 3 games
            for stat in ['PTS', 'AST', 'REB', 'STL', 'BLK', 'FG3M', 'FG3A', 'FGM', 'FGA', 'FTM', 'FTA', 'TOV', 'MIN']:
                if stat in df.columns:
                    df[f'{stat}_L3'] = df[stat].rolling(3).mean()
                    df[f'{stat}_L5'] = df[stat].rolling(5).mean()
                    df[f'{stat}_L10'] = df[stat].rolling(10).mean()
            
            # Calculate shooting percentages
            if 'FGA' in df.columns and 'FGM' in df.columns:
                df['FG_PCT'] = df['FGM'] / df['FGA'].replace(0, np.nan)
                
            if 'FG3A' in df.columns and 'FG3M' in df.columns:
                df['FG3_PCT'] = df['FG3M'] / df['FG3A'].replace(0, np.nan)
                
            if 'FTA' in df.columns and 'FTM' in df.columns:
                df['FT_PCT'] = df['FTM'] / df['FTA'].replace(0, np.nan)
            
            # Add game location feature
            if 'MATCHUP' in df.columns:
                df['HOME_GAME'] = df['MATCHUP'].str.contains('vs').astype(int)
            
            # Add day of week
            if 'GAME_DATE' in df.columns:
                df['DAY_OF_WEEK'] = df['GAME_DATE'].dt.dayofweek
            
            # Clean up any NaN values
            df = df.fillna(0)
            
            return df
            
        except Exception as e:
            console.print(f"[bold red]Error processing player data:[/] {str(e)}")
            return None

    def extract_features(self, df, target_stat):
        """Extract features for ML model from processed data.
        
        Args:
            df: Processed DataFrame
            target_stat: Target statistic to predict (e.g., 'PTS', 'AST')
            
        Returns:
            tuple: X (features) and y (target values)
        """
        if df is None or df.empty:
            return None, None
            
        try:
            # Define feature columns based on available data
            feature_cols = []
            
            # Add rolling averages for target stat
            for window in [3, 5, 10]:
                col = f"{target_stat}_L{window}"
                if col in df.columns:
                    feature_cols.append(col)
            
            # Add other relevant features
            if 'HOME_GAME' in df.columns:
                feature_cols.append('HOME_GAME')
                
            if 'DAY_OF_WEEK' in df.columns:
                feature_cols.append('DAY_OF_WEEK')
                
            # Add minutes played features
            if 'MIN_L3' in df.columns:
                feature_cols.append('MIN_L3')
                
            if 'MIN_L5' in df.columns:
                feature_cols.append('MIN_L5')
            
            # Select features and target
            X = df[feature_cols].copy()
            y = df[target_stat].copy()
            
            return X, y
            
        except Exception as e:
            console.print(f"[bold red]Error extracting features:[/] {str(e)}")
            return None, None

    def prepare_prediction_data(self, player_df, target_stat):
        """Prepare the most recent data for making a prediction.
        
        Args:
            player_df: Processed player DataFrame
            target_stat: Target statistic to predict
            
        Returns:
            DataFrame: Single row of features for prediction
        """
        if player_df is None or player_df.empty:
            return None
            
        try:
            # Get the most recent data
            df = self.process_player_data(player_df)
            
            # Extract the relevant features
            X, _ = self.extract_features(df, target_stat)
            
            if X is None or X.empty:
                return None
                
            # Return only the most recent row for prediction
            return X.iloc[0:1]
            
        except Exception as e:
            console.print(f"[bold red]Error preparing prediction data:[/] {str(e)}")
            return None

    def process_comprehensive_data(self, games_df):
        """Process comprehensive NBA game data from player game logs.
        
        This method handles data from multiple players' game stats collected with PlayerGameLog API,
        augmenting it with additional features.
        
        Args:
            games_df: DataFrame containing multiple players' game data
            
        Returns:
            DataFrame: Processed data with engineered features
        """
        if games_df is None or games_df.empty:
            console.print("[bold red]Error:[/] No comprehensive data to process")
            return None
            
        try:
            # Make a copy to avoid modifying the original
            df = games_df.copy()
            
            # Get unique player names to process each player separately
            if 'PLAYER_NAME' not in df.columns:
                console.print("[yellow]Warning: No player name column found in data, using Player ID[/]")
                player_col = 'PLAYER_ID' if 'PLAYER_ID' in df.columns else None
            else:
                player_col = 'PLAYER_NAME'
                
            if player_col is None:
                console.print("[bold red]Error: Cannot identify player column in data[/]")
                return None
                
            # Convert date column to datetime
            if 'GAME_DATE' in df.columns:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
                
            players = df[player_col].unique()
            console.print(f"[green]Processing data for {len(players)} players[/]")
            
            processed_players = []
            
            # Process each player's data to create rolling features
            for player in players:
                player_data = df[df[player_col] == player].copy()
                
                # Sort by date if available
                if 'GAME_DATE' in player_data.columns:
                    player_data = player_data.sort_values(by='GAME_DATE')
                
                # Create rolling averages for key stats
                for stat in ['PTS', 'AST', 'REB', 'STL', 'BLK', 'FG3M', 'FGM', 'FGA', 'FTM', 'FTA', 'TOV', 'MIN']:
                    if stat in player_data.columns:
                        player_data[f'{stat}_L3'] = player_data[stat].rolling(3).mean()
                        player_data[f'{stat}_L5'] = player_data[stat].rolling(5).mean()
                        player_data[f'{stat}_L10'] = player_data[stat].rolling(10).mean()
                
                # Calculate shooting percentages
                if 'FGA' in player_data.columns and 'FGM' in player_data.columns:
                    player_data['FG_PCT'] = player_data['FGM'] / player_data['FGA'].replace(0, np.nan)
                    
                if 'FG3A' in player_data.columns and 'FG3M' in player_data.columns:
                    player_data['FG3_PCT'] = player_data['FG3M'] / player_data['FG3A'].replace(0, np.nan)
                    
                if 'FTA' in player_data.columns and 'FTM' in player_data.columns:
                    player_data['FT_PCT'] = player_data['FTM'] / player_data['FTA'].replace(0, np.nan)
                
                # Add home/away indicator
                if 'MATCHUP' in player_data.columns:
                    player_data['HOME_GAME'] = player_data['MATCHUP'].str.contains('vs.').astype(int)
                
                # Add day of week if date available
                if 'GAME_DATE' in player_data.columns:
                    player_data['DAY_OF_WEEK'] = player_data['GAME_DATE'].dt.dayofweek
                
                processed_players.append(player_data)
            
            # Combine all processed player data
            processed_df = pd.concat(processed_players)
            
            # Fill NaN values with 0s
            processed_df = processed_df.fillna(0)
            
            console.print(f"[bold green]Successfully processed {len(processed_df)} rows of data![/]")
            return processed_df
            
        except Exception as e:
            console.print(f"[bold red]Error processing comprehensive data:[/] {str(e)}")
            return None 