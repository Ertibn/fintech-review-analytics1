import os
from collections import Counter

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def top_keywords(reviews, top_n=10):
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=250)
    matrix = vectorizer.fit_transform(reviews)
    scores = matrix.sum(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    return [term for term, _ in ranked[:top_n]]


def summary_for_bank(df, bank_name):
    bank_df = df[df['bank'] == bank_name]
    positive = bank_df[bank_df['sentiment_label'] == 'positive']
    negative = bank_df[bank_df['sentiment_label'] == 'negative']
    neutral = bank_df[bank_df['sentiment_label'] == 'neutral']

    drivers = positive['identified_theme'].value_counts().head(3).to_dict()
    pain_points = negative['identified_theme'].value_counts().head(3).to_dict()
    frequent_reviews = Counter(str(bank_df['review_text'].astype(str).str.lower()).split()).most_common(10)
    keywords = top_keywords(bank_df['review_text'].astype(str).tolist(), top_n=8)

    return {
        'bank_name': bank_name,
        'total_reviews': len(bank_df),
        'avg_rating': round(bank_df['rating'].mean(), 2) if len(bank_df) else 0,
        'positive_share': round(len(positive) / len(bank_df) * 100, 2) if len(bank_df) else 0,
        'negative_share': round(len(negative) / len(bank_df) * 100, 2) if len(bank_df) else 0,
        'neutral_share': round(len(neutral) / len(bank_df) * 100, 2) if len(bank_df) else 0,
        'top_positive_themes': drivers,
        'top_negative_themes': pain_points,
        'top_keywords': keywords
    }


def generate_insights():
    input_path = 'data/raw/sentiment_reviews.csv'
    if not os.path.exists(input_path):
        print(f"Input file {input_path} not found. Run sentiment_analysis.py first.")
        return

    df = pd.read_csv(input_path)
    df['review_text'] = df['review_text'].astype(str)
    df['sentiment_label'] = df['sentiment_label'].fillna('neutral')

    banks = df['bank'].unique()
    lines = [
        '# Fintech App Review Insights Summary',
        '',
        'This summary is generated from the processed review dataset and highlights satisfaction drivers, recurring complaints, and keyword trends for each bank.',
        ''
    ]

    for bank in banks:
        summary = summary_for_bank(df, bank)

        lines.extend([
            f'## {bank}',
            f'- Total reviews: {summary["total_reviews"]}',
            f'- Average rating: {summary["avg_rating"]}',
            f'- Positive review share: {summary["positive_share"]}%',
            f'- Negative review share: {summary["negative_share"]}%',
            f'- Neutral review share: {summary["neutral_share"]}%',
            '',
            '### Top Positive Themes',
        ])

        for theme, count in summary['top_positive_themes'].items():
            lines.append(f'- {theme}: {count} reviews')

        lines.extend(['', '### Top Negative Themes'])
        for theme, count in summary['top_negative_themes'].items():
            lines.append(f'- {theme}: {count} reviews')

        lines.extend(['', '### Top Keywords', ''])
        lines.append(', '.join(summary['top_keywords']))
        lines.extend(['', '---', ''])

    output_path = 'notebooks/insights_summary.md'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Saved insights summary to {output_path}")


if __name__ == '__main__':
    generate_insights()
