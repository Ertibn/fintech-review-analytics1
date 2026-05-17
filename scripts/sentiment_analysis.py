import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import os
import sys
import torch

def run_vader_sentiment(df):
    print("Running VADER Sentiment Analysis...")
    analyzer = SentimentIntensityAnalyzer()
    
    vader_labels = []
    vader_scores = []
    
    for text in df['review']:
        score = analyzer.polarity_scores(text)
        compound = score['compound']
        vader_scores.append(compound)
        
        if compound >= 0.05:
            vader_labels.append('positive')
        elif compound <= -0.05:
            vader_labels.append('negative')
        else:
            vader_labels.append('neutral')
            
    df['vader_label'] = vader_labels
    df['vader_score'] = vader_scores
    return df

def run_transformer_sentiment(df):
    print("Running DistilBERT Sentiment Analysis (CPU)...")
    # Check if GPU is available
    device = 0 if torch.cuda.is_available() else -1
    
    try:
        classifier = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=device
        )
        
        # Batch processing to avoid memory errors
        batch_size = 32
        texts = df['review'].tolist()
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            # Truncate texts to maximum length of 512 tokens for DistilBERT
            batch_truncated = [t[:512] for t in batch]
            batch_results = classifier(batch_truncated)
            results.extend(batch_results)
            
        transformer_labels = []
        transformer_scores = []
        
        for r in results:
            # DistilBERT outputs POSITIVE / NEGATIVE
            label = r['label'].lower()
            score = r['score']
            
            # Map score to positive/negative values
            if label == 'negative':
                score = -score
                
            transformer_labels.append(label)
            transformer_scores.append(score)
            
        df['transformer_label'] = transformer_labels
        df['transformer_score'] = transformer_scores
    except Exception as e:
        print(f"Error running DistilBERT: {e}. Falling back to VADER only.")
        df['transformer_label'] = df['vader_label']
        df['transformer_score'] = df['vader_score']
        
    return df

def extract_themes(text):
    text_lower = str(text).lower()
    
    themes = {
        'Account Access & Authentication': ['login', 'sign in', 'password', 'otp', 'code', 'access', 'locked', 'register', 'signup', 'verification'],
        'Transaction & Payment Issues': ['transaction', 'transfer', 'money', 'pay', 'send', 'cbebirr', 'amole', 'apollo', 'send money', 'deposit', 'withdraw', 'pending', 'failed', 'deducted'],
        'App Performance & Stability': ['slow', 'crash', 'freeze', 'loading', 'bug', 'error', 'lag', 'crashes', 'network', 'connection', 'open', 'close'],
        'UI & Customer Experience': ['ui', 'design', 'interface', 'beautiful', 'clean', 'easy', 'user friendly', 'look', 'nice', 'love', 'perfect'],
        'Customer Support & Service': ['support', 'contact', 'help', 'service', 'branch', 'agent', 'response', 'reply', 'customer service', 'call']
    }
    
    matched_themes = []
    for theme, keywords in themes.items():
        if any(kw in text_lower for kw in keywords):
            matched_themes.append(theme)
            
    if not matched_themes:
        return 'Other / General Feedback'
    # Return primary matched theme
    return matched_themes[0]

def main():
    input_path = 'data/raw/cleaned_reviews.csv'
    if not os.path.exists(input_path):
        print(f"Input file {input_path} not found. Please run scrape_reviews.py first.")
        sys.exit(1)
        
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} reviews.")
    
    # 1. Run VADER
    df = run_vader_sentiment(df)
    
    # 2. Run DistilBERT (Transformer)
    df = run_transformer_sentiment(df)
    
    # 3. Add identified themes
    print("Running thematic analysis extraction...")
    df['identified_theme'] = df['review'].apply(extract_themes)
    
    # 4. Generate comparison metrics
    agreement = (df['vader_label'] == df['transformer_label']).mean()
    print(f"Sentiment label agreement between VADER and DistilBERT: {agreement:.2%}")
    
    # 5. Format final output for Task 2 specifications
    # Save results as a CSV with columns: review_id, review_text, sentiment_label, sentiment_score, identified_theme
    # Use the transformer model as our main sentiment analysis tool
    df['review_id'] = range(1, len(df) + 1)
    
    output_df = pd.DataFrame({
        'review_id': df['review_id'],
        'review_text': df['review'],
        'rating': df['rating'],
        'date': df['date'],
        'bank': df['bank'],
        'sentiment_label': df['transformer_label'],
        'sentiment_score': df['transformer_score'],
        'vader_label': df['vader_label'],
        'vader_score': df['vader_score'],
        'identified_theme': df['identified_theme']
    })
    
    output_path = 'data/raw/sentiment_reviews.csv'
    output_df.to_csv(output_path, index=False)
    print(f"Saved sentiment and thematic results to {output_path}")

if __name__ == '__main__':
    main()
