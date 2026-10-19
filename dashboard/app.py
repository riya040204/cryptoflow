
import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="CryptoFlow | Intelligence Dashboard",
    page_icon="₿",
    layout="wide"
)
st_autorefresh(interval=5000, key="cryptoflow_refresh")

st.title("₿ CryptoFlow Intelligence")
st.caption("Real-time cryptocurrency streaming analytics")



import os

def get_db_config():
    if "database" in st.secrets:
        db = st.secrets["database"]
        return {
            "host": db["host"],
            "port": int(db.get("port", 5432)),
            "dbname": db["dbname"],
            "user": db["user"],
            "password": db["password"],
            "sslmode": "require",
        }

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5433")),
        "dbname": os.getenv("DB_NAME", "cryptoflow"),
        "user": os.getenv("DB_USER", "cryptoflow"),
        "password": os.getenv("DB_PASSWORD", "cryptoflow"),
    }

DB_CONFIG = get_db_config()




@st.cache_data(ttl=5)
def load_data():
    connection = psycopg2.connect(**DB_CONFIG)
    try:
        
        query = """
            SELECT symbol, price, volume, event_time
            FROM crypto_prices
            WHERE event_time >= NOW() - INTERVAL '2 hours'
            ORDER BY event_time DESC
            LIMIT 500
        """

        return pd.read_sql_query(query, connection)
    finally:
        connection.close()


try:
    data = load_data()
    connection = psycopg2.connect(**DB_CONFIG)
    try:
        anomalies = pd.read_sql_query(
            """
            SELECT symbol, price, anomaly_score,
                   anomaly_type, severity, detected_at
            FROM anomalies
            ORDER BY detected_at DESC
            LIMIT 20
            """,
            connection
        )
    finally:
        connection.close()

    if data.empty:
        st.warning("No price records found. Start the producer and Spark.")
        st.stop()

    data["event_time"] = pd.to_datetime(data["event_time"])
    data = data.sort_values("event_time")

    
    latest = data.iloc[-1]
    previous = data.iloc[-2] if len(data) > 1 else latest

    price_change = latest["price"] - previous["price"]

    price_change_pct = (
        price_change / previous["price"] * 100
        if previous["price"] else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Latest BTCUSDT Price",
        f"${latest['price']:,.2f}",
        f"{price_change_pct:+.3f}%"
    )

    col2.metric(
        "Price Change",
        f"${price_change:+,.2f}"
    )

    col3.metric(
        "Latest Recorded Volume",
        f"{latest['volume']:,.4f}"
    )

    col4.metric(
        "Records Loaded",
        f"{len(data):,}"
    )

    st.divider()

    st.subheader("Price History")

    
    chart = px.line(
        data,
        x="event_time",
        y="price",
        color="symbol",
        markers=True,
        title="Cryptocurrency Price Over Time",
        labels={
            "event_time": "Time",
            "price": "Price (USDT)",
            "symbol": "Asset"
        }
    )

    chart.update_layout(
        hovermode="x unified",
        xaxis_title="Time",
        yaxis_title="Price (USDT)"
    )
    st.plotly_chart(chart, width="stretch")
    st.subheader("🤖 ML Anomaly Alerts")
    
    chart.update_layout(hovermode="x unified")
    st.plotly_chart(chart, width="stretch", key="price_chart")

    st.subheader("🤖 ML Anomaly Alerts")
    if anomalies.empty:
        st.info("No anomaly records found yet.")
    else:
        st.dataframe(
            anomalies,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Recent Market Records")

    recent = data.sort_values(
        "event_time", ascending=False
    ).head(20)

    st.dataframe(recent, use_container_width=True)

    if st.button("Refresh dashboard"):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        f"Last displayed timestamp: {latest['event_time']}"
    )

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.info(
        "Check that Docker PostgreSQL is running "
        "and exposed on port 5433."
    )

