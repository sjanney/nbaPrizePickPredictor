"""Machine learning predictor for NBA player performance."""

import os
import joblib
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()


class NBAPredictor:
    """ML model to predict NBA player performance."""

    def __init__(self, model_dir="data/models"):
        """Initialize the NBA predictor.
        
        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.models = {}
        
    def train(self, X, y, stat_name, model_type="random_forest"):
        """Train a model for a specific stat.
        
        Args:
            X: Feature matrix
            y: Target values
            stat_name: Name of the stat being predicted (e.g., 'PTS')
            model_type: Type of model to train
            
        Returns:
            dict: Training metrics
        """
        if X is None or y is None or X.empty or len(y) == 0:
            console.print("[bold red]Error:[/] No data for training")
            return None
            
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold green]Training {stat_name} model..."),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Training...", total=100)
            
            try:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                progress.update(task, advance=10)
                
                # Select model type
                if model_type == "random_forest":
                    model = RandomForestRegressor(
                        n_estimators=100,
                        random_state=42,
                        n_jobs=-1
                    )
                elif model_type == "gradient_boosting":
                    model = GradientBoostingRegressor(
                        n_estimators=100,
                        random_state=42
                    )
                else:
                    model = RandomForestRegressor(
                        n_estimators=100,
                        random_state=42,
                        n_jobs=-1
                    )
                    
                # Train the model
                model.fit(X_train, y_train)
                progress.update(task, advance=50)
                
                # Cross-validation
                cv_scores = cross_val_score(
                    model, X, y, cv=5, scoring='neg_mean_absolute_error'
                )
                
                # Evaluate on test set
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)
                
                progress.update(task, advance=30)
                
                # Save model
                model_filename = f"{self.model_dir}/{stat_name}_{model_type}_{datetime.now().strftime('%Y%m%d')}.joblib"
                joblib.dump(model, model_filename)
                
                # Store model in memory
                self.models[stat_name] = model
                
                progress.update(task, advance=10)
                
                # Collect metrics
                metrics = {
                    'model_type': model_type,
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'cv_mae': -np.mean(cv_scores),
                    'feature_importance': dict(zip(X.columns, model.feature_importances_)),
                    'model_file': model_filename
                }
                
                # Display metrics
                self._display_metrics(metrics, stat_name)
                
                return metrics
                
            except Exception as e:
                console.print(f"[bold red]Error training model:[/] {str(e)}")
                return None
                
    def _display_metrics(self, metrics, stat_name):
        """Display model metrics in a table.
        
        Args:
            metrics: Dictionary of metrics
            stat_name: Name of the stat
        """
        table = Table(title=f"Model Performance for {stat_name}")
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Model Type", metrics['model_type'])
        table.add_row("Mean Absolute Error", f"{metrics['mae']:.2f}")
        table.add_row("Root Mean Squared Error", f"{metrics['rmse']:.2f}")
        table.add_row("R² Score", f"{metrics['r2']:.2f}")
        table.add_row("Cross-Val MAE", f"{metrics['cv_mae']:.2f}")
        
        console.print(table)
        
        # Feature importance table
        imp_table = Table(title="Feature Importance")
        imp_table.add_column("Feature", style="cyan")
        imp_table.add_column("Importance", style="green")
        
        # Sort features by importance
        sorted_features = sorted(
            metrics['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for feature, importance in sorted_features:
            imp_table.add_row(feature, f"{importance:.4f}")
            
        console.print(imp_table)
        
    def predict(self, X, stat_name):
        """Make a prediction for a player's performance.
        
        Args:
            X: Features for prediction (single row)
            stat_name: Statistic to predict
            
        Returns:
            float: Predicted value
        """
        if X is None or X.empty:
            console.print("[bold red]Error:[/] No data for prediction")
            return None
            
        try:
            # Check if model exists in memory
            if stat_name in self.models:
                model = self.models[stat_name]
            else:
                # Try to load from disk
                model_files = [f for f in os.listdir(self.model_dir) if f.startswith(f"{stat_name}_")]
                
                if not model_files:
                    console.print(f"[bold red]Error:[/] No trained model found for {stat_name}")
                    return None
                    
                # Get the most recent model
                latest_model = sorted(model_files)[-1]
                model = joblib.load(f"{self.model_dir}/{latest_model}")
                self.models[stat_name] = model
                
            # Make prediction
            prediction = model.predict(X)[0]
            
            return max(0, prediction)  # Ensure non-negative prediction
            
        except Exception as e:
            console.print(f"[bold red]Error making prediction:[/] {str(e)}")
            return None
            
    def evaluate_prediction(self, prediction, actual_value, stat_name):
        """Evaluate prediction against actual value.
        
        Args:
            prediction: Predicted value
            actual_value: Actual value
            stat_name: Name of the stat
            
        Returns:
            dict: Evaluation metrics
        """
        if prediction is None:
            return None
            
        try:
            error = actual_value - prediction
            abs_error = abs(error)
            pct_error = abs_error / max(1, actual_value) * 100
            
            evaluation = {
                'stat': stat_name,
                'prediction': prediction,
                'actual': actual_value,
                'error': error,
                'abs_error': abs_error,
                'pct_error': pct_error
            }
            
            return evaluation
            
        except Exception as e:
            console.print(f"[bold red]Error evaluating prediction:[/] {str(e)}")
            return None 