CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    run_id VARCHAR(100) NOT NULL,
    model_uri TEXT NOT NULL,
    features TEXT[] NOT NULL,
    rmse FLOAT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);