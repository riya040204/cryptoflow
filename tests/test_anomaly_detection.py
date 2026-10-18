
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from ml.anomaly_detection import detect_anomalies


@patch("ml.anomaly_detection.psycopg2.connect")
def test_not_enough_records(mock_connect, capsys):
    connection = MagicMock()
    mock_connect.return_value = connection

    with patch(
        "ml.anomaly_detection.pd.read_sql_query",
        return_value=pd.DataFrame(
            columns=["id", "symbol", "price", "volume", "event_time"]
        ),
    ):
        detect_anomalies()

    assert "Not enough records" in capsys.readouterr().out
    connection.close.assert_called_once()


@patch("ml.anomaly_detection.psycopg2.connect")
def test_database_connection_failure(mock_connect):
    mock_connect.side_effect = Exception("Database unavailable")

    with pytest.raises(Exception, match="Database unavailable"):
        detect_anomalies()

@patch("ml.anomaly_detection.psycopg2.connect")
def test_valid_data_commits_transaction(mock_connect, capsys):
    connection = MagicMock()
    mock_connect.return_value = connection

    data = pd.DataFrame({
        "id": range(30),
        "symbol": ["BTCUSDT"] * 30,
        "price": [100 + i for i in range(30)],
        "volume": [1000 + i * 10 for i in range(30)],
        "event_time": pd.date_range("2026-01-01", periods=30, freq="min"),
    })

    with patch(
        "ml.anomaly_detection.pd.read_sql_query",
        return_value=data,
    ):
        with patch(
            "ml.anomaly_detection.IsolationForest.fit_predict",
            return_value=[1] * 28 + [-1],
        ), patch(
            "ml.anomaly_detection.IsolationForest.decision_function",
            return_value=[0.1] * 28 + [-0.1],
        ):
            detect_anomalies()

    connection.commit.assert_called_once()
    connection.close.assert_called_once()
    assert "Records analyzed: 30" in capsys.readouterr().out
