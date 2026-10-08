-- ============================================
-- CryptoFlow Database Schema
-- ============================================

-- Cryptocurrency assets
CREATE TABLE IF NOT EXISTS assets (
    asset_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw market prices received from exchanges
CREATE TABLE IF NOT EXISTS crypto_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    volume NUMERIC(30, 8),
    event_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated market metrics
CREATE TABLE IF NOT EXISTS market_metrics (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    open_price NUMERIC(20, 8),
    high_price NUMERIC(20, 8),
    low_price NUMERIC(20, 8),
    close_price NUMERIC(20, 8),
    total_volume NUMERIC(30, 8),
    price_change_percent NUMERIC(10, 4)
);

-- ML anomaly detection results
CREATE TABLE IF NOT EXISTS anomalies (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    anomaly_score NUMERIC(12, 6),
    anomaly_type VARCHAR(50),
    severity VARCHAR(20),
    detected_at TIMESTAMP NOT NULL
);

-- Insert initial supported assets
INSERT INTO assets (symbol, name)
VALUES
    ('BTC', 'Bitcoin'),
    ('ETH', 'Ethereum'),
    ('SOL', 'Solana')
ON CONFLICT (symbol) DO NOTHING;