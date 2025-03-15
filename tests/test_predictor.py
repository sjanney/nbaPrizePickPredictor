"""Tests for NBA predictor model."""

import os
import pytest
import pandas as pd
import numpy as np
import tempfile
import shutil
from nba_prizepicks.models.predictor import NBAPredictor


@pytest.fixture
def temp_model_dir():
    """Create a temporary directory for test models."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after test
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_training_data():
    """Create sample training data for testing."""
    # Create feature matrix
    X = pd.DataFrame({
        'PTS_L3': [25.0, 27.0, 22.0, 30.0, 28.0, 26.0, 24.0, 29.0, 20.0, 25.0],
        'PTS_L5': [24.0, 26.0, 23.0, 28.0, 27.0, 25.0, 24.0, 27.0, 22.0, 24.0],
        'PTS_L10': [23.0, 25.0, 22.0, 27.0, 26.0, 24.0, 23.0, 26.0, 21.0, 23.0],
        'MIN_L3': [35.0, 34.0, 32.0, 36.0, 33.0, 35.0, 34.0, 35.0, 30.0, 33.0],
        'HOME_GAME': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        'DAY_OF_WEEK': [1, 3, 5, 0, 2, 4, 6, 1, 3, 5]
    })
    
    # Create target values
    y = pd.Series([26, 28, 20, 32, 30, 24, 25, 31, 18, 27])
    
    return X, y


def test_init(temp_model_dir):
    """Test initialization of NBAPredictor."""
    predictor = NBAPredictor(model_dir=temp_model_dir)
    
    # Check that the model directory was created
    assert os.path.isdir(temp_model_dir)
    
    # Check that models dict is empty
    assert predictor.models == {}


def test_train(temp_model_dir, sample_training_data):
    """Test training a model."""
    predictor = NBAPredictor(model_dir=temp_model_dir)
    X, y = sample_training_data
    
    # Train a model
    metrics = predictor.train(X, y, 'PTS')
    
    # Check that metrics were returned
    assert metrics is not None
    assert 'mae' in metrics
    assert 'rmse' in metrics
    assert 'r2' in metrics
    assert 'cv_mae' in metrics
    assert 'model_file' in metrics
    assert 'feature_importance' in metrics
    
    # Check that model was saved
    assert os.path.exists(metrics['model_file'])
    
    # Check that model is in memory
    assert 'PTS' in predictor.models
    
    # Check feature importance
    assert len(metrics['feature_importance']) == len(X.columns)
    assert sum(metrics['feature_importance'].values()) > 0


def test_train_empty_data(temp_model_dir):
    """Test training with empty data."""
    predictor = NBAPredictor(model_dir=temp_model_dir)
    
    # Empty DataFrame
    X = pd.DataFrame()
    y = pd.Series()
    
    # Train should fail gracefully
    metrics = predictor.train(X, y, 'PTS')
    assert metrics is None
    
    # None values
    metrics = predictor.train(None, None, 'PTS')
    assert metrics is None


def test_predict(temp_model_dir, sample_training_data):
    """Test making a prediction."""
    predictor = NBAPredictor(model_dir=temp_model_dir)
    X, y = sample_training_data
    
    # Train a model first
    predictor.train(X, y, 'PTS')
    
    # Create a test sample
    test_sample = pd.DataFrame({
        'PTS_L3': [26.0],
        'PTS_L5': [25.0],
        'PTS_L10': [24.0],
        'MIN_L3': [34.0],
        'HOME_GAME': [1],
        'DAY_OF_WEEK': [2]
    })
    
    # Make a prediction
    prediction = predictor.predict(test_sample, 'PTS')
    
    # Check that a prediction was made
    assert prediction is not None
    assert isinstance(prediction, (int, float))
    assert prediction > 0  # Non-negative prediction


def test_predict_missing_model(temp_model_dir, sample_training_data):
    """Test prediction with missing model."""
    predictor = NBAPredictor(model_dir=temp_model_dir)
    X, _ = sample_training_data
    
    # Create a test sample
    test_sample = X.iloc[[0]]
    
    # Prediction should fail gracefully
    prediction = predictor.predict(test_sample, 'NONEXISTENT')
    assert prediction is None


def test_evaluate_prediction():
    """Test evaluating a prediction."""
    predictor = NBAPredictor()
    
    # Test evaluation
    evaluation = predictor.evaluate_prediction(25.0, 28.0, 'PTS')
    
    assert evaluation is not None
    assert evaluation['stat'] == 'PTS'
    assert evaluation['prediction'] == 25.0
    assert evaluation['actual'] == 28.0
    assert evaluation['error'] == 3.0
    assert evaluation['abs_error'] == 3.0
    assert evaluation['pct_error'] > 0
    
    # Test with None prediction
    evaluation = predictor.evaluate_prediction(None, 28.0, 'PTS')
    assert evaluation is None 