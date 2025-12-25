from pathlib import Path
import sys
from unittest.mock import patch

from typer.testing import CliRunner

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from btc_prediction.modeling.train import app, main


runner = CliRunner()


def test_cli_main_exit_code_zero(tmp_path):
    """CLI command should exit with code 0."""
    features_path = tmp_path / "features.csv"
    labels_path = tmp_path / "labels.csv"
    model_path = tmp_path / "model.pkl"

    features_path.touch()
    labels_path.touch()

    result = runner.invoke(
        app,
        [
            "--features-path",
            str(features_path),
            "--labels-path",
            str(labels_path),
            "--model-path",
            str(model_path),
        ],
    )

    assert result.exit_code == 0


@patch("btc_prediction.modeling.train.logger")
def test_main_logging(mock_logger):
    """Main function should log start, mid-iteration, and success messages."""
    main(
        features_path=Path("features.csv"),
        labels_path=Path("labels.csv"),
        model_path=Path("model.pkl"),
    )

    mock_logger.info.assert_any_call("Training some model...")
    mock_logger.info.assert_any_call(
        "Something happened for iteration 5."
    )
    mock_logger.success.assert_called_once_with(
        "Modeling training complete."
    )


@patch("btc_prediction.modeling.train.tqdm")
def test_main_tqdm_called_correctly(mock_tqdm):
    """tqdm should wrap range(10) with total=10."""
    mock_tqdm.return_value = range(10)

    main(
        features_path=Path("features.csv"),
        labels_path=Path("labels.csv"),
        model_path=Path("model.pkl"),
    )

    mock_tqdm.assert_called_once_with(range(10), total=10)
