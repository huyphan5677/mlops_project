from unittest.mock import MagicMock, patch
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from data_pipeline.transform import (
    read_data_from_minio,
    read_raw_data_from_minio,
    save_processed_data_to_minio,
    get_hour,
    get_day,
    EMA,
    SMA,
    VWAP,
    RSI,
    generate_features,
)


@pytest.fixture
def sample_df():
    """Return a minimal valid OHLCV DataFrame."""
    base_ts = int(datetime(2024, 1, 1, 0, 0).timestamp() * 1000)
    return pd.DataFrame(
        {
            "Open_time": [base_ts + i * 3600_000 for i in range(6)],
            "Open": [100, 101, 102, 103, 104, 105],
            "High": [101, 102, 103, 104, 105, 106],
            "Low": [99, 100, 101, 102, 103, 104],
            "Close": [100, 101, 102, 103, 104, 105],
            "Volume": [10, 11, 12, 13, 14, 15],
        }
    )


def test_get_hour():
    ts = int(datetime(2024, 1, 1, 15).timestamp() * 1000)
    assert get_hour(ts) == 15


def test_get_day():
    ts = int(datetime(2024, 1, 25).timestamp() * 1000)
    assert get_day(ts) == 25


def test_ema(sample_df):
    """EMA should return a Series with same length."""
    result = EMA(sample_df, "Close", 3)
    assert len(result) == len(sample_df)


def test_sma(sample_df):
    """SMA should compute rolling mean."""
    result = SMA(sample_df, "Close", 3)
    assert np.isnan(result.iloc[1])
    assert not np.isnan(result.iloc[3])


def test_vwap(sample_df):
    """VWAP should return rolling weighted price."""
    result = VWAP(sample_df, 3)
    assert len(result) == len(sample_df)


def test_rsi(sample_df):
    """RSI should be bounded between 0 and 100."""
    result = RSI(sample_df, 3)
    assert ((result.dropna() >= 0) & (result.dropna() <= 100)).all()


def test_generate_features_adds_columns(sample_df):
    """Feature engineering should add technical columns."""
    df = generate_features(sample_df.copy())

    expected_columns = {
        "EMA",
        "SMA",
        "VWAP",
        "RSI",
        "DCup",
        "DCdown",
        "DCmid",
        "BollingerBasis",
        "BollingerUpper",
        "BollingerLower",
        "target",
    }

    assert expected_columns.issubset(set(df.columns))


def test_save_processed_data_to_minio(sample_df):
    """Ensure data is partitioned and uploaded to MinIO."""
    minio_client = MagicMock()
    minio_client.bucket_exists.return_value = False

    save_processed_data_to_minio(
        df=sample_df.copy(),
        minio_client=minio_client,
        bucket_name="processed-bucket",
    )

    # Bucket should be created
    minio_client.make_bucket.assert_called_once()

    # At least one object uploaded
    assert minio_client.put_object.called


@patch("data_pipeline.transform.ds.dataset")
@patch("data_pipeline.transform.fs.S3FileSystem")
def test_read_data_from_minio(mock_s3, mock_dataset, sample_df):
    """Read parquet data using mocked PyArrow dataset."""
    mock_table = MagicMock()
    mock_table.to_pandas.return_value = sample_df

    mock_dataset.return_value.to_table.return_value = mock_table

    df = read_data_from_minio(
        s3_path="bucket/raw/",
        storage_options={
            "key": "k",
            "secret": "s",
            "endpoint_url": "minio:9000",
            "use_ssl": False,
        },
        start_date=0,
        end_date=9999999999999,
    )

    assert not df.empty
    assert "Open_time" in df.columns


@patch("data_pipeline.transform.read_data_from_minio")
def test_read_raw_data_from_minio(mock_read, sample_df):
    """Wrapper function should filter and sort data."""
    mock_read.return_value = sample_df

    df = read_raw_data_from_minio(
        bucket_name="bucket",
        start_date=sample_df["Open_time"].min(),
        end_date=sample_df["Open_time"].max(),
    )

    assert df.iloc[0]["Open_time"] <= df.iloc[-1]["Open_time"]