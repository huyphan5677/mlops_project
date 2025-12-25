from pathlib import Path
import pickle
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from btc_prediction.train_and_predict import (
    process_input,
    get_model_candidates,
    train_models_with_gridsearch,
    evaluate_model,
    champion_challenger_competition,
)


@pytest.fixture
def sample_dataframe():
    """Create a minimal valid dataframe for training."""
    rows = 10
    data = {
        "Open": np.random.rand(rows),
        "High": np.random.rand(rows),
        "Low": np.random.rand(rows),
        "Close": np.random.rand(rows),
        "Volume": np.random.rand(rows),
        "Quote_asset_volume": np.random.rand(rows),
        "Number_of_trades": np.random.rand(rows),
        "Taker_buy_base_asset_volume": np.random.rand(rows),
        "Taker_buy_base_quote_volume": np.random.rand(rows),
        "SMA": np.random.rand(rows),
        "VWAP": np.random.rand(rows),
        "DCdown": np.random.rand(rows),
        "DCup": np.random.rand(rows),
        "DCmid": np.random.rand(rows),
        "BollingerBasis": np.random.rand(rows),
        "BollingerUpper": np.random.rand(rows),
        "BollingerLower": np.random.rand(rows),
        "Past_trend_Open_2h": np.random.rand(rows),
        "Past_trend_Open_3h": np.random.rand(rows),
        "Past_trend_Open_2h_flag": np.random.randint(0, 2, rows),
        "Past_trend_Open_3h_flag": np.random.randint(0, 2, rows),
        "target": np.random.rand(rows),
    }
    return pd.DataFrame(data)


def test_process_input_shapes(sample_dataframe):
    """process_input should return correct shapes."""
    feature_cols = [c for c in sample_dataframe.columns if c != "target"]

    X_train, y_train, X_test, scaler = process_input(
        sample_dataframe, feature_cols, "target"
    )

    assert X_train.shape[0] == len(sample_dataframe) - 4
    assert X_test.shape[0] == 1
    assert len(y_train) == X_train.shape[0]
    assert scaler is not None


def test_get_model_candidates_structure():
    """Model candidates should contain expected keys."""
    models = get_model_candidates()

    expected = {
        "Ridge",
        "Lasso",
        "ElasticNet",
        "RandomForest",
        "GradientBoosting",
    }

    assert set(models.keys()) == expected

    for config in models.values():
        assert "model" in config
        assert "params" in config


@patch("btc_prediction.train_and_predict.GridSearchCV")
def test_train_models_with_gridsearch(mock_gridsearch):
    """train_models_with_gridsearch should return best model and results."""
    mock_instance = MagicMock()
    mock_instance.best_score_ = -1.0
    mock_instance.best_estimator_ = MagicMock()
    mock_instance.best_params_ = {"alpha": 1.0}
    mock_gridsearch.return_value = mock_instance

    X = np.random.rand(20, 5)
    y = pd.Series(np.random.rand(20))

    best_model, best_name, results = train_models_with_gridsearch(X, y)

    assert best_model is not None
    assert best_name in results
    assert "rmse" in results[best_name]
    assert mock_gridsearch.called


def test_evaluate_model_outputs():
    """evaluate_model should return all metrics."""
    model = MagicMock()
    model.predict.return_value = np.array([1.0, 2.0, 3.0])

    X_test = np.zeros((3, 2))
    y_test = np.array([1.0, 2.0, 2.5])

    metrics = evaluate_model(model, X_test, y_test)

    assert set(metrics.keys()) == {"mse", "rmse", "mae", "r2"}
    assert metrics["mse"] >= 0.0


@patch("btc_prediction.train_and_predict.load_champion_model_from_s3")
def test_champion_challenger_no_champion(mock_load):
    mock_load.return_value = None

    challenger = MagicMock()

    X = np.random.rand(10, 3)
    y = pd.Series(np.random.rand(10))

    split_idx = int(len(X) * 0.8)
    val_len = len(X) - split_idx

    challenger.predict.return_value = np.ones(val_len)

    model, name, metrics, is_new = champion_challenger_competition(
        challenger, "Ridge", X, y
    )

    assert is_new is True
    assert model is challenger
    assert "rmse" in metrics
