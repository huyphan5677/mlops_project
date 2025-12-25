from datetime import datetime
from pathlib import Path
import sys
import pandas as pd
from unittest.mock import MagicMock, patch
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from data_pipeline.extract import (
    get_year,
    get_month,
    get_day,
    get_hour,
    get_data,
    save_to_minio_partitioned,
)


def test_get_year():
    ts_ms = int(datetime(2024, 1, 15, 10, 0).timestamp() * 1000)
    assert get_year(ts_ms) == 2024


def test_get_month():
    ts_ms = int(datetime(2024, 5, 15, 10, 0).timestamp() * 1000)
    assert get_month(ts_ms) == 5


def test_get_day():
    ts_ms = int(datetime(2024, 5, 15, 10, 0).timestamp() * 1000)
    assert get_day(ts_ms) == 15


def test_get_hour():
    ts_ms = int(datetime(2024, 5, 15, 22, 30).timestamp() * 1000)
    assert get_hour(ts_ms) == 22


def test_save_to_minio_partitioned_creates_bucket_and_uploads():
    """
    Ensure data is partitioned and uploaded to MinIO.
    """
    minio_client = MagicMock()
    minio_client.bucket_exists.return_value = False

    bucket_name = "test-bucket"

    df = pd.DataFrame(
        {
            "Open_time": [
                int(datetime(2024, 5, 15, 10).timestamp() * 1000),
                int(datetime(2024, 5, 15, 11).timestamp() * 1000),
            ],
            "Open": [1.0, 2.0],
            "High": [1.5, 2.5],
            "Low": [0.5, 1.5],
            "Close": [1.2, 2.2],
            "Volume": [100, 200],
        }
    )

    save_to_minio_partitioned(df, minio_client, bucket_name)

    # Bucket should be created
    minio_client.make_bucket.assert_called_once_with(bucket_name)

    # At least one object should be uploaded
    assert minio_client.put_object.called

    # Validate object name format
    args, kwargs = minio_client.put_object.call_args
    assert "raw/date=" in kwargs["object_name"]
    assert "hour=" in kwargs["object_name"]


@patch("data_pipeline.extract.save_to_minio_partitioned")
@patch("data_pipeline.extract.Client")
def test_get_data_success(mock_client, mock_save):
    """
    Test Binance data fetch and MinIO save workflow.
    """
    # Mock Binance client
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance

    mock_instance.get_historical_klines.return_value = [
        [
            1700000000000,
            "100",
            "110",
            "90",
            "105",
            "1000",
            0,
            0,
            0,
            0,
            0,
            0,
        ]
    ]

    minio_client = MagicMock()

    df = get_data(
        api_key="key",
        api_secret="secret",
        minio_client=minio_client,
        bucket_name="bucket",
        start_date=1700000000000,
        end_date=1700003600000,
    )

    # Binance API should be called
    mock_instance.get_historical_klines.assert_called_once()

    # DataFrame should not be empty
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

    # Save function must be called
    mock_save.assert_called_once()