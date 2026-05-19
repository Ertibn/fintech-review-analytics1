-- PostgreSQL schema for fintech-review-analytics review ingestion
-- This schema can be used to create the production-ready bank_reviews database.

CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    app_id VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(100) PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    date DATE NOT NULL,
    sentiment_label VARCHAR(20) NOT NULL,
    sentiment_score REAL NOT NULL,
    identified_theme VARCHAR(100) NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'Google Play'
);
