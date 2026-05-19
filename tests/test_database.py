import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from scripts.database_ingestion import Bank, Review, get_database_engine

def test_database_connection():
    """Verify that get_database_engine returns a valid SQLAlchemy engine and connects"""
    engine = get_database_engine()
    assert engine is not None, "Database engine should not be None"
    
    # Test connection
    with engine.connect() as conn:
        assert conn is not None

def test_database_tables_exist():
    """Verify that tables 'banks' and 'reviews' exist in the database"""
    engine = get_database_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    assert "banks" in tables, "'banks' table should exist in database"
    assert "reviews" in tables, "'reviews' table should exist in database"

def test_database_seeded_data():
    """Verify that database has seeded bank metadata and loaded review records"""
    engine = get_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check banks
        banks_count = session.query(Bank).count()
        assert banks_count >= 3, f"At least 3 banks should be seeded, found {banks_count}"
        
        # Check reviews
        reviews_count = session.query(Review).count()
        assert reviews_count > 0, "Reviews table should not be empty after running ingestion"
        
        # Verify a specific bank
        cbe = session.query(Bank).filter_by(name="CBE").first()
        assert cbe is not None, "CBE metadata should be present in banks table"
        assert cbe.app_id == "prod.cbe.birr"
        
    finally:
        session.close()
