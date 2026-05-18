import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime
import os
import sys
import re
from langdetect import detect

# Common English words/short terms seen in reviews
SHORT_ENGLISH_WORDS = {
    'good', 'excellent', 'nice', 'best', 'perfect', 'bad', 'worst', 
    'great', 'love', 'fast', 'slow', 'okay', 'ok', 'super', 'cool', 
    'working', 'fine', 'thanks', 'thank', 'you', 'app', 'easy', 'simple',
    'helpful', 'use', 'useful', 'crashes', 'slow', 'lag', 'crashed', 
    'error', 'login', 'problem', 'issues', 'issue', 'otp', 'money', 
    'transfer', 'trust', 'trustworthy', 'worst', 'poor', 'happy', 
    'pleased', 'satisfactory', 'satisfied', 'five', 'star', 'stars',
    'awesome', 'wonderful', 'amazing', 'brilliant', 'fantastic'
}

def is_english(text):
    if not text or not isinstance(text, str):
        return False
    
    # Strip whitespace
    text_clean = text.strip()
    if not text_clean:
        return False
        
    # Filter out Ge'ez script (Amharic characters)
    # Ethiopic Unicode block is U+1200 to U+137F, and extended blocks
    if re.search(r'[\u1200-\u137F\u2D80-\u2DDF\uAB00-\uAB2F]', text_clean):
        return False
        
    # Check if it contains latin characters at all
    if not re.search(r'[a-zA-Z]', text_clean):
        return False
        
    # Tokenize words for short texts check
    words = [w.lower().strip(".,!?\"'()[]{}*-+=") for w in text_clean.split()]
    words = [w for w in words if w]
    
    if not words:
        return False
        
    # If the text is very short (1-3 words), check if at least one word is standard English
    if len(words) <= 3:
        if any(w in SHORT_ENGLISH_WORDS for w in words):
            return True
            
    # Check with langdetect
    try:
        lang = detect(text_clean)
        if lang == 'en':
            # Double check for common transliterated Amharic words to avoid misclassification
            # e.g., "betam arif new" or "gobez new" or similar
            amharic_transliterated_words = {
                'betam', 'arif', 'temetatagn', 'gobez', 'tiru', 'konjo', 'temesgen',
                'ayesram', 'alrisam', 'nw', 'new', 'des', 'yilal', 'yamral', 'yishalal',
                'nechew', 'gar', 'le', 'sew', 'ke', 'na', 'chahn', 'tew'
            }
            # If the review has a high density of Amharic transliterated words, return False
            amharic_word_count = sum(1 for w in words if w in amharic_transliterated_words)
            if amharic_word_count / len(words) > 0.3:
                return False
            return True
    except Exception:
        pass
        
    # Fallback check: if at least 50% of the words are in SHORT_ENGLISH_WORDS, count as English
    english_overlap = sum(1 for w in words if w in SHORT_ENGLISH_WORDS)
    if len(words) > 0 and (english_overlap / len(words)) >= 0.5:
        return True
        
    return False

def scrape_bank_reviews(app_id, bank_name, num_reviews=400):
    print(f"Scraping reviews for {bank_name} ({app_id})...")
    result, continuation_token = reviews(
        app_id,
        lang='en', # defaults to 'en'
        country='us', # defaults to 'us'
        sort=Sort.NEWEST, # defaults to Sort.NEWEST
        count=num_reviews # defaults to 100
    )
    
    # Extract only required fields
    columns = ['id', 'review', 'rating', 'date', 'bank', 'source']
    if not result:
        return pd.DataFrame(columns=columns)
        
    data = []
    for r in result:
        data.append({
            'id': r['reviewId'],
            'review': r['content'],
            'rating': r['score'],
            'date': r['at'],
            'bank': bank_name,
            'source': 'Google Play'
        })
    
    return pd.DataFrame(data, columns=columns)

def preprocess_data(df):
    initial_len = len(df)
    
    # Remove duplicate reviews
    df = df.drop_duplicates(subset=['id'])
    
    # Handle missing values: drop rows missing review text or rating
    df = df.dropna(subset=['review', 'rating'])
    
    # Filter only English language reviews
    print("Filtering English-only reviews...")
    df = df[df['review'].apply(is_english)]
    
    # Normalize dates to YYYY-MM-DD format
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Drop the temporary ID column as it's not requested in the final CSV spec
    df = df.drop(columns=['id'])
    
    final_len = len(df)
    print(f"Preprocessed data: {initial_len} -> {final_len} rows.")
    return df

def main():
    app_ids = {
        'CBE': 'prod.cbe.birr',       # CBEBirr Plus / CBE Mobile
        'BOA': 'com.boa.apollo',       # BOA Apollo
        'Dashen': 'com.cr2.amolelight' # Dashen Amole Light
    }

    all_reviews = []
    for bank_name, app_id in app_ids.items():
        try:
            # Scrape up to 1500 to ensure we have >400 English reviews per bank after pruning
            df = scrape_bank_reviews(app_id, bank_name, num_reviews=1500)
            if not df.empty:
                all_reviews.append(df)
            else:
                print(f"No reviews found for {bank_name} ({app_id}).")
        except Exception as e:
            print(f"Failed to scrape {bank_name}: {e}")
    
    if not all_reviews:
        print("No data collected. Exiting.")
        sys.exit(1)
        
    final_df = pd.concat(all_reviews, ignore_index=True)
    
    # Preprocessing
    cleaned_df = preprocess_data(final_df)
    
    # Save the cleaned dataset
    os.makedirs('data/raw', exist_ok=True)
    output_path = 'data/raw/cleaned_reviews.csv'
    cleaned_df.to_csv(output_path, index=False)
    print(f"Saved {len(cleaned_df)} cleaned reviews to {output_path}")

if __name__ == '__main__':
    main()

