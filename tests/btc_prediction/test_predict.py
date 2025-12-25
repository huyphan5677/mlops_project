from pathlib import Path
import sys
from unittest.mock import patch

from typer.testing import CliRunner

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from btc_prediction.modeling.predict import app, main


runner = CliRunner()


def test_main_runs_successfully(tmp_path):
    """Main command should run without raising exceptions."""
    features_path = tmp_path / "features.csv"
    model_path = tmp_path / "model.pkl"
    predictions_path = tmp_path / "predictions.csv"

    features_path.touch()
    model_path.touch()

    result = runner.invoke(
        app,
        [
            "--features-path",
            str(features_path),
            "--model-path",
            str(model_path),
            "--predictions-path",
            str(predictions_path),
        ],
    )

    assert result.exit_code == 0


@patch("btc_prediction.modeling.predict.logger")
def test_main_logging_calls(mock_logger):
    """Logger should record info and success messages."""
    main(
        features_path=Path("features.csv"),
        model_path=Path("model.pkl"),
        predictions_path=Path("predictions.csv"),
    )

    mock_logger.info.assert_any_call("Performing inference for model...")
    mock_logger.success.assert_called_once_with("Inference complete.")


@patch("btc_prediction.modeling.predict.tqdm")
def test_main_progress_loop(mock_tqdm):
    """Progress loop should iterate exactly 10 times."""
    mock_tqdm.return_value = range(10)

    main(
        features_path=Path("features.csv"),
        model_path=Path("model.pkl"),
        predictions_path=Path("predictions.csv"),
    )

    mock_tqdm.assert_called_once_with(range(10), total=10)
