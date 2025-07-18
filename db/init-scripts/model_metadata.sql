CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    run_id VARCHAR(100) ,
    model_uri TEXT ,
    val_size FLOAT NOT NULL,
    features TEXT[] NOT NULL,
    model_type VARCHAR,
    shuffle BOOLEAN,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    train_start_date TIMESTAMP WITHOUT TIME ZONE,
    train_end_date TIMESTAMP WITHOUT TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_model_ticker_exchange ON model_metadata(ticker, exchange);
