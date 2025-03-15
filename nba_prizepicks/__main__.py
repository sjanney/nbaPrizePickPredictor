"""Entry point for NBA PrizePicks Predictor."""

import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from nba_prizepicks.ui.dashboard import Dashboard

app = typer.Typer(help="NBA PrizePicks Predictor CLI")
console = Console()


@app.callback()
def main():
    """NBA PrizePicks Predictor - Predict player performances with ML."""
    title = Text("NBA PrizePicks Predictor", style="bold blue")
    subtitle = Text("Predict winning PrizePicks with machine learning", style="italic cyan")
    
    panel = Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="green",
        expand=False,
    )
    console.print(panel)


@app.command()
def run(compare_prizepicks: bool = typer.Option(False, "--compare", "-c", help="Compare predictions with live PrizePicks lines")):
    """Run the NBA PrizePicks Predictor dashboard."""
    try:
        dashboard = Dashboard()
        
        # Set PrizePicks comparison mode if specified
        if compare_prizepicks:
            console.print("[bold yellow]Starting with PrizePicks comparisons enabled[/]")
            dashboard.compare_with_prizepicks = True
            dashboard.prizepicks = dashboard.prizepicks.__class__(use_sample_data=False)
        else:
            console.print("[bold green]Starting in predictions-only mode[/]")
        
        dashboard.run()
    except KeyboardInterrupt:
        console.print("[bold red]Application terminated by user.[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    app() 