from unittest.mock import MagicMock, patch
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "data_pipeline"))

from data_pipeline.pipeline import (
    save_to_minio_with_type,
    run_profiling,
    run_pipeline,
)


@pytest.fixture
def sample_raw_df():
    """Minimal raw dataframe returned from extract."""
    base_ts = int(datetime(2024, 1, 1).timestamp() * 1000)
    return pd.DataFrame(
        {
            "Open_time": [base_ts, base_ts + 3600_000],
            "Open": [100, 101],
            "High": [101, 102],
            "Low": [99, 100],
            "Close": [100, 101],
            "Volume": [10, 11],
        }
    )


@pytest.fixture
def minio_client():
    """Mocked MinIO client."""
    return MagicMock()


@patch("data_pipeline.pipeline.save_to_minio_partitioned")
@patch("data_pipeline.pipeline.save_processed_data_to_minio")
def test_save_to_minio_with_type_raw(
    mock_save_processed,
    mock_save_raw,
    sample_raw_df,
    minio_client,
):
    """Raw data should be routed to raw save function."""
    save_to_minio_with_type(
        df=sample_raw_df,
        minio_client=minio_client,
        bucket_name="bucket",
        data_type="raw",
    )

    mock_save_raw.assert_called_once()
    mock_save_processed.assert_not_called()


@patch("data_pipeline.pipeline.save_to_minio_partitioned")
@patch("data_pipeline.pipeline.save_processed_data_to_minio")
def test_save_to_minio_with_type_processed(
    mock_save_processed,
    mock_save_raw,
    sample_raw_df,
    minio_client,
):
    """Processed data should be routed to processed save function."""
    save_to_minio_with_type(
        df=sample_raw_df,
        minio_client=minio_client,
        bucket_name="bucket",
        data_type="processed",
    )

    mock_save_processed.assert_called_once()
    mock_save_raw.assert_not_called()


def test_run_profiling_creates_report(tmp_path, sample_raw_df):
    """Profiling should generate a CSV report."""
    output_dir = tmp_path / "profiling"
    output_dir.mkdir()

    with patch("data_pipeline.pipeline.os.makedirs"), \
         patch("data_pipeline.pipeline.open", create=True), \
         patch("pandas.DataFrame.to_csv") as mock_to_csv:

        report_path = run_profiling(
            df=sample_raw_df,
            name="test_profile",
        )

        assert report_path.endswith("test_profile.csv")
        mock_to_csv.assert_called_once()


@patch("data_pipeline.pipeline.Minio")
@patch("data_pipeline.pipeline.run_profiling")
@patch("data_pipeline.pipeline.save_processed_data_to_minio")
@patch("data_pipeline.pipeline.generate_features")
@patch("data_pipeline.pipeline.read_raw_data_from_minio")
@patch("data_pipeline.pipeline.extract_binance_data")
def test_run_pipeline_full(
    mock_extract,
    mock_read_raw,
    mock_generate,
    mock_save_processed,
    mock_profiling,
    mock_minio,
):
    """Full pipeline should execute extract -> transform -> save."""
    sample_df = pd.DataFrame({"timestamp": ["2024-01-01 00:00:00"], "price": [100]})

    # Mock return_value
    mock_extract.return_value = sample_df
    mock_read_raw.return_value = sample_df
    mock_generate.return_value = sample_df.assign(feature=1)

    # Act
    result = run_pipeline(
        start_date="2024-01-01 00:00:00",
        end_date="2024-01-01 02:00:00",
    )

    # Assert
    assert result is not None
    mock_extract.assert_called_once()
    mock_generate.assert_called_once()
    mock_save_processed.assert_called_once()
    mock_profiling.assert_called_once()


@patch("data_pipeline.pipeline.extract_binance_data")
def test_run_pipeline_extract_returns_none(mock_extract):
    """Pipeline should fail gracefully if extract returns None."""
    mock_extract.return_value = None

    result = run_pipeline(
        start_date="2024-01-01 00:00:00",
        end_date="2024-01-01 01:00:00",
    )

    assert result is None