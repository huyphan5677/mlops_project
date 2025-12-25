from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from btc_prediction.dataset import app

runner = CliRunner()


def test_cli_runs_successfully(tmp_path):
    """
    CLI command should run successfully with default arguments.
    """
    result = runner.invoke(app)

    assert result.exit_code == 0


@patch("btc_prediction.dataset.logger")
@patch("btc_prediction.dataset.tqdm")
def test_logging_and_progress_called(mock_tqdm, mock_logger):
    """
    main() should log start, mid, and success messages.
    """
    # Arrange
    mock_tqdm.return_value = range(10)

    # Act
    result = runner.invoke(app)

    # Assert
    assert result.exit_code == 0

    mock_logger.info.assert_any_call("Processing dataset...")
    mock_logger.info.assert_any_call("Something happened for iteration 5.")
    mock_logger.success.assert_called_once_with("Processing dataset complete.")


def test_cli_accepts_custom_paths(tmp_path):
    """
    CLI should accept custom input/output paths.
    """
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    input_file.write_text("dummy data")

    result = runner.invoke(
        app,
        [
            "--input-path",
            str(input_file),
            "--output-path",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
