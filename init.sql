    CREATE TABLE IF NOT EXISTS explain (
        id SERIAL PRIMARY KEY,
        explain_output TEXT NOT NULL,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )