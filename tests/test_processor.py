"""Tests for NBA data processor."""

import pytest
import pandas as pd
import numpy as np
from nba_prizepicks.data.processor import NBADataProcessor


@pytest.fixture
def sample_player_data():
    """Create sample player data for testing."""
    return pd.DataFrame({
        'GAME_DATE': ['2023-11-01', '2023-11-03', '2023-11-05', '2023-11-07', '2023-11-09'],
        'MATCHUP': ['LAL vs BOS', 'LAL @ PHX', 'LAL vs HOU', 'LAL @ MEM', 'LAL vs POR'],
        'WL': ['W', 'L', 'W', 'W', 'L'],
        'MIN': [35, 32, 30, 36, 33],
        'PTS': [25, 30, 20, 28, 22],
        'REB': [10, 8, 12, 9, 11],
        'AST': [8, 9, 6, 7, 8],
        'FGM': [10, 12, 8, 11, 9],
        'FGA': [20, 22, 18, 21, 19],
        'FG3M': [3, 4, 2, 3, 2],
        'FG3A': [8, 7, 6, 9, 5],
        'FTM': [2, 2, 2, 3, 2],
        'FTA': [4, 3, 2, 5, 3],
        'TOV': [2, 3, 1, 2, 2],
        'STL': [1, 2, 1, 2, 1],
        'BLK': [1, 0, 2, 1, 1]
    })


def test_init():
    """Test initialization of NBADataProcessor."""
    processor = NBADataProcessor()
    assert processor is not None


def test_process_player_data(sample_player_data):
    """Test processing of player data."""
    processor = NBADataProcessor()
    processed_df = processor.process_player_data(sample_player_data)
    
    # Test basic processing
    assert processed_df is not None
    assert not processed_df.empty
    assert 'GAME_DATE' in processed_df.columns
    
    # Test date conversion
    assert pd.api.types.is_datetime64_any_dtype(processed_df['GAME_DATE'])
    
    # Test rolling averages exist
    assert 'PTS_L3' in processed_df.columns
    assert 'REB_L3' in processed_df.columns
    assert 'AST_L3' in processed_df.columns
    
    # Test shooting percentages
    assert 'FG_PCT' in processed_df.columns
    assert 'FG3_PCT' in processed_df.columns
    assert 'FT_PCT' in processed_df.columns
    
    # Test home game feature
    assert 'HOME_GAME' in processed_df.columns
    assert processed_df['HOME_GAME'].dtype == np.int64
    assert processed_df['HOME_GAME'].iloc[0] == 1  # First game is "LAL vs BOS" (home)
    assert processed_df['HOME_GAME'].iloc[1] == 0  # Second game is "LAL @ PHX" (away)


def test_process_player_data_empty():
    """Test processing with empty data."""
    processor = NBADataProcessor()
    
    # Test with empty DataFrame
    empty_df = pd.DataFrame()
    result = processor.process_player_data(empty_df)
    assert result is None
    
    # Test with None
    result = processor.process_player_data(None)
    assert result is None


def test_extract_features(sample_player_data):
    """Test feature extraction."""
    processor = NBADataProcessor()
    processed_df = processor.process_player_data(sample_player_data)
    
    # Test points features
    X, y = processor.extract_features(processed_df, 'PTS')
    
    assert X is not None
    assert y is not None
    assert not X.empty
    assert len(y) > 0
    
    # Check that target values match
    assert len(y) == len(processed_df)
    assert y.iloc[0] == processed_df['PTS'].iloc[0]
    
    # Check that features include rolling averages
    assert 'PTS_L3' in X.columns
    
    # Test with different target stat
    X, y = processor.extract_features(processed_df, 'AST')
    assert 'AST_L3' in X.columns
    assert y.iloc[0] == processed_df['AST'].iloc[0]


def test_prepare_prediction_data(sample_player_data):
    """Test preparation of prediction data."""
    processor = NBADataProcessor()
    processed_df = processor.process_player_data(sample_player_data)
    
    # Get prediction data for points
    pred_data = processor.prepare_prediction_data(processed_df, 'PTS')
    
    assert pred_data is not None
    assert not pred_data.empty
    assert len(pred_data) == 1  # Should return just one row
    
    # Features should include rolling averages
    assert 'PTS_L3' in pred_data.columns
    
    # Test with different target stat
    pred_data = processor.prepare_prediction_data(processed_df, 'REB')
    assert 'REB_L3' in pred_data.columns 