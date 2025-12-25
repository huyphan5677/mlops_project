from unittest.mock import MagicMock, patch

import sys
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from data_pipeline.load import insert_data_postgres


@pytest.fixture
def mock_psycopg2():
    """
    Mock psycopg2 connection and cursor.
    """
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        yield mock_connect, mock_conn, mock_cursor


def test_insert_data_success(mock_psycopg2):
    """
    Test successful insert into PostgreSQL.
    """
    mock_connect, mock_conn, mock_cursor = mock_psycopg2

    time_value = 1_700_000_000
    price = 68940.0
    trade_type = "real"

    insert_data_postgres(
        time_value=time_value,
        price=price,
        trade_type=trade_type,
    )

    # psycopg2.connect should be called once
    mock_connect.assert_called_once()

    # Cursor should be created
    mock_conn.cursor.assert_called_once()

    # CREATE TABLE should be executed
    assert any(
        "CREATE TABLE IF NOT EXISTS trades" in call.args[0]
        for call in mock_cursor.execute.call_args_list
    )

    # INSERT query should be executed
    assert any(
        "INSERT INTO trades" in str(call.args[0])
        for call in mock_cursor.execute.call_args_list
    )

    # Commit must be called
    mock_conn.commit.assert_called_once()

    # Resources must be closed
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_insert_data_db_error(mock_psycopg2):
    """
    Test database error handling.
    """
    mock_connect, mock_conn, mock_cursor = mock_psycopg2

    # Force execute() to raise exception
    mock_cursor.execute.side_effect = Exception("DB error")

    insert_data_postgres(
        time_value=1_700_000_000,
        price=100.0,
        trade_type="test",
    )

    # Commit should NOT be called on failure
    mock_conn.commit.assert_not_called()

    # Cursor and connection should still be closed
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
