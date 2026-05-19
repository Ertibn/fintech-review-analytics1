import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_visualizations():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        'font.size': 12,
        'axes.labelsize': 14,
        'axes.titlesize': 16,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'figure.titlesize': 18
    })

    input_path = 'data/raw/sentiment_reviews.csv'
    if not os.path.exists(input_path):
        print(f"Input file {input_path} not found. Run sentiment_analysis.py first.")
        return

    df = pd.read_csv(input_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    os.makedirs('notebooks/plots', exist_ok=True)

    # 1. Sentiment Distribution by Bank
    plt.figure(figsize=(10, 6))
    sentiment_counts = df.groupby(['bank', 'sentiment_label']).size().unstack(fill_value=0)
    sentiment_pct = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100
    colors = ['#e74c3c', '#95a5a6', '#2ecc71']

    ax = sentiment_pct.plot(kind='bar', stacked=True, color=colors, figsize=(10, 6), width=0.65)
    plt.title('Transformer-Based Sentiment Distribution by Bank', pad=20)
    plt.xlabel('Bank')
    plt.ylabel('Percentage (%)')
    plt.xticks(rotation=0)
    plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')

    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()
        if height > 3:
            ax.text(x + width/2, y + height/2, f'{height:.1f}%', ha='center', va='center', color='white', weight='bold')

    plt.tight_layout()
    plt.savefig('notebooks/plots/sentiment_distribution.png', dpi=300)
    plt.close()
    print("Generated sentiment_distribution.png")

    # 2. Rating Distribution per Bank
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x='rating', hue='bank', palette='viridis')
    plt.title('Rating Distribution per Bank', pad=20)
    plt.xlabel('Rating (Stars)')
    plt.ylabel('Number of Reviews')
    plt.legend(title='Bank')
    plt.tight_layout()
    plt.savefig('notebooks/plots/ratings_by_bank.png', dpi=300)
    plt.close()
    print("Generated ratings_by_bank.png")

    # 3. Top Themes Frequency per Bank
    plt.figure(figsize=(12, 8))
    theme_counts = df.groupby(['identified_theme', 'bank']).size().unstack(fill_value=0)
    theme_counts = theme_counts.loc[theme_counts.sum(axis=1).sort_values(ascending=False).head(12).index]

    theme_counts.plot(kind='barh', figsize=(12, 8), width=0.8, colormap='coolwarm')
    plt.title('Top Identified Themes across Banks', pad=20)
    plt.xlabel('Number of Reviews')
    plt.ylabel('Identified Theme')
    plt.legend(title='Bank', loc='lower right')
    plt.tight_layout()
    plt.savefig('notebooks/plots/themes_frequency.png', dpi=300)
    plt.close()
    print("Generated themes_frequency.png")

    # 4. Sentiment Trend over Time
    if df['date'].notna().any():
        sentiment_trend = (
            df.groupby([pd.Grouper(key='date', freq='7D'), 'bank'])['sentiment_score']
              .mean()
              .reset_index()
        )
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=sentiment_trend, x='date', y='sentiment_score', hue='bank', marker='o')
        plt.title('Weekly Average Sentiment Score Trend by Bank', pad=20)
        plt.xlabel('Date')
        plt.ylabel('Average Sentiment Score')
        plt.legend(title='Bank')
        plt.tight_layout()
        plt.savefig('notebooks/plots/sentiment_trend.png', dpi=300)
        plt.close()
        print("Generated sentiment_trend.png")
    else:
        print("Skipping sentiment trend plot because no valid date values were found.")

if __name__ == '__main__':
    generate_visualizations()
