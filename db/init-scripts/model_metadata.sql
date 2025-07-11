CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    run_id VARCHAR(100) NOT NULL,
    model_uri TEXT NOT NULL,
    features TEXT[] NOT NULL,
    model_type VARCHAR,
    shuffle BOOLEAN,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    train_start_time TIMESTAMP WITHOUT TIME ZONE,
    train_end_time TIMESTAMP WITHOUT TIME ZONE
);
