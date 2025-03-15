"""Tests for PrizePicks data fallback functionality."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from nba_prizepicks.utils.prizepicks import PrizePicksData

# Create test directory
os.makedirs("test_data/prizepicks", exist_ok=True)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return [
        {
            "player_name": "Test Player",
            "team": "TST",
            "opponent": "OPP",
            "projection_type": "Points",
            "line": 20.5,
            "game_time": "2023-11-15T19:30:00"
        }
    ]


@pytest.fixture
def prizepicks_handler(sample_data):
    """Create a PrizePicks data handler for testing."""
    # Create sample data file
    with open("test_data/prizepicks/sample_lines.json", "w") as f:
        json.dump(sample_data, f)
        
    # Return handler using the test data directory
    return PrizePicksData(data_dir="test_data")


def test_fallback_to_sample_data(prizepicks_handler):
    """Test that the handler falls back to sample data when scraping fails."""
    # Mock _scrape_prizepicks_data to simulate a failed scrape
    with patch.object(prizepicks_handler, '_scrape_prizepicks_data', return_value=[]):
        # Try to get lines with live data
        prizepicks_handler.use_sample_data = False
        lines = prizepicks_handler.get_todays_lines()
        
        # Should fall back to sample data
        assert lines is not None
        assert len(lines) > 0
        assert lines[0]["player_name"] == "Test Player"


def test_robust_get_player_line(prizepicks_handler):
    """Test that get_player_line gracefully handles errors."""
    # Test with invalid player name
    line = prizepicks_handler.get_player_line(None, "Points")
    assert line is None
    
    # Test with non-existent player
    line = prizepicks_handler.get_player_line("NonExistentPlayer", "Points")
    assert line is None
    
    # Test with exception during processing
    with patch.object(prizepicks_handler, 'get_todays_lines', side_effect=Exception("Test error")):
        line = prizepicks_handler.get_player_line("Test Player", "Points")
        assert line is None


def test_robust_get_player_lines(prizepicks_handler):
    """Test that get_player_lines gracefully handles errors."""
    # Test with invalid player name
    lines = prizepicks_handler.get_player_lines(None)
    assert lines == []
    
    # Test with non-existent player
    lines = prizepicks_handler.get_player_lines("NonExistentPlayer")
    assert lines == []
    
    # Test with exception during processing
    with patch.object(prizepicks_handler, 'get_todays_lines', side_effect=Exception("Test error")):
        lines = prizepicks_handler.get_player_lines("Test Player")
        assert lines == []


def test_extreme_fallback_case():
    """Test the extreme fallback case where even sample data can't be read."""
    # Create a handler with a directory we can actually write to
    handler = PrizePicksData(data_dir="test_data_extreme")
    
    # Make sure we clean up after the test
    try:
        # Force an exception when reading the sample file using a mock
        with patch('builtins.open', side_effect=Exception("Can't open file")):
            # Mock os.makedirs to avoid file system errors
            with patch('os.makedirs'):
                # Should still get minimal data back
                lines = handler.get_todays_lines()
                
                # Verify we get at least one line for the application to function
                assert lines is not None
                assert len(lines) > 0
                assert "player_name" in lines[0]
    finally:
        # Clean up if directory was created
        import shutil
        try:
            shutil.rmtree("test_data_extreme", ignore_errors=True)
        except:
            pass


# The dashboard test is complicated to run without a proper mock setup
# Let's create a simpler test focusing on the fallback mechanism
def test_prizepicks_always_returns_data():
    """Test that PrizePicksData always returns some data regardless of errors."""
    # Create a bare handler
    handler = PrizePicksData(data_dir="test_data")
    
    # Test with empty sample data
    with patch.object(handler, '_ensure_sample_data'):
        with patch('builtins.open', side_effect=Exception("Can't read any files")):
            with patch.object(handler, '_scrape_prizepicks_data', return_value=[]):
                # Even with all methods failing, should get minimal emergency data
                lines = handler.get_todays_lines()
                
                # Verify we get at least one emergency data line
                assert lines is not None
                assert len(lines) > 0
                assert "player_name" in lines[0] 