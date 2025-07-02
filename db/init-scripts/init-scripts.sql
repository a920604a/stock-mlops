CREATE TABLE stock_meta (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    name TEXT,
    exchange TEXT,
    industry TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE stock_prices (
    ticker TEXT NOT NULL,
    exchange TEXT,
    date DATE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    ma10 NUMERIC,
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY (ticker, date)
) PARTITION BY LIST (ticker);

CREATE TABLE stock_prices_aapl PARTITION OF stock_prices
    FOR VALUES IN ('AAPL');

CREATE TABLE stock_prices_2330tw PARTITION OF stock_prices
    FOR VALUES IN ('2330.TW');

CREATE TABLE stock_features (
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    feature_name TEXT NOT NULL,
    value NUMERIC,
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY (ticker, date, feature_name)
);

CREATE TABLE model_registry (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    version TEXT NOT NULL,
    accuracy NUMERIC,
    loss NUMERIC,
    run_id TEXT,  -- 對應 MLflow run_id
    created_at TIMESTAMP DEFAULT now()
);
