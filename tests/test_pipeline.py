import pandas as pd
import pytest
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def test_vader_sentiment():
    """Test that VADER correctly identifies positive and negative texts"""
    analyzer = SentimentIntensityAnalyzer()
    
    pos_text = "This Apollo banking app is absolutely amazing and extremely fast!"
    neg_text = "This app is completely useless, it crashes constantly and steals money."
    
    pos_score = analyzer.polarity_scores(pos_text)['compound']
    neg_score = analyzer.polarity_scores(neg_text)['compound']
    
    assert pos_score >= 0.05, "Positive review compound score should be positive"
    assert neg_score <= -0.05, "Negative review compound score should be negative"

def test_data_processing():
    """Test standard de-duplication and null handling preprocessing steps"""
    raw_data = [
        {"id": "1", "review": "Excellent service", "rating": 5, "date": "2026-05-16"},
        {"id": "1", "review": "Excellent service", "rating": 5, "date": "2026-05-16"}, # Duplicate
        {"id": "2", "review": None, "rating": 3, "date": "2026-05-15"},                # Null review
        {"id": "3", "review": "Average app", "rating": 3, "date": "2026-05-14"}
    ]
    df = pd.DataFrame(raw_data)
    
    # Preprocess
    df = df.drop_duplicates(subset=['id'])
    df = df.dropna(subset=['review', 'rating'])
    
    assert len(df) == 2, "After preprocessing, only 2 valid reviews should remain"
    assert "1" in df['id'].values
    assert "3" in df['id'].values
    assert "2" not in df['id'].values
