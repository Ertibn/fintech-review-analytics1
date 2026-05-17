import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime
import os
import sys

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
            df = scrape_bank_reviews(app_id, bank_name, num_reviews=600) # Scrape extra to ensure 400+ after cleaning
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
