
import psycopg2
import pandas as pd
from sklearn.ensemble import IsolationForest

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "cryptoflow",
    "user": "cryptoflow",
    "password": "cryptoflow"
}


def detect_anomalies():
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        data = pd.read_sql_query(
            """
            SELECT id, symbol, price, volume, event_time
            FROM crypto_prices
            ORDER BY event_time DESC, id DESC
            LIMIT 1000
            """,
            connection
        )

        if len(data) < 20:
            print("Not enough records for anomaly detection.")
            return

        data = data.sort_values(["symbol", "event_time", "id"]).copy()

        data["price_change_pct"] = (
            data.groupby("symbol")["price"].pct_change() * 100
        )
        data["volume_change_pct"] = (
            data.groupby("symbol")["volume"].pct_change() * 100
        )

        features = data[
            ["price_change_pct", "volume_change_pct"]
        ].replace([float("inf"), float("-inf")], float("nan"))

        valid = features.notna().all(axis=1)
        features = features.loc[valid]

        if len(features) < 20:
            print("Not enough valid records.")
            return

        model = IsolationForest(
            contamination=0.02,
            random_state=42
        )
        predictions = model.fit_predict(features)
        scores = model.decision_function(features)

        flagged = data.loc[valid].copy()
        flagged["prediction"] = predictions
        flagged["score"] = scores

        anomalies = flagged[flagged["prediction"] == -1]

        with connection.cursor() as cursor:
            for row in anomalies.itertuples():
                severity = (
                    "high" if row.score < -0.05 else "medium"
                )

                cursor.execute(
                    """
                    INSERT INTO anomalies
                    (symbol, price, anomaly_score, anomaly_type,
                     severity, detected_at)
                    SELECT %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM anomalies
                        WHERE symbol = %s AND detected_at = %s
                    )
                    """,
                    (
                        row.symbol,
                        float(row.price),
                        float(row.score),
                        "price_volume_change",
                        severity,
                        row.event_time,
                        row.symbol,
                        row.event_time
                    )
                )

        connection.commit()

        print(f"Records analyzed: {len(data)}")
        print(f"Potential anomalies detected: {len(anomalies)}")
        print(f"Anomaly records saved: {len(anomalies)}")

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    detect_anomalies()
