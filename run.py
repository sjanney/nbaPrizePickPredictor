#!/usr/bin/env python
"""Run the NBA PrizePicks Predictor application.

This application provides:
1. Predictions-only mode: Pure statistical predictions without PrizePicks data (default)
2. PrizePicks comparison mode: Compare predictions with live PrizePicks lines

Run with --compare/-c flag to enable PrizePicks comparisons:
    python run.py --compare
"""

import sys
from nba_prizepicks.__main__ import app

if __name__ == "__main__":
    # If arguments are provided, pass them to the app
    if len(sys.argv) > 1:
        app(sys.argv[1:])
    else:
        # Default to running with default options
        app(["run"]) 