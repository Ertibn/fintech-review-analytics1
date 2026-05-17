import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_visualizations():
    # Set style
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
    
    # Create plots directory if not exists
    os.makedirs('notebooks/plots', exist_ok=True)
    
    # 1. Sentiment Distribution by Bank
    plt.figure(figsize=(10, 6))
    sentiment_counts = df.groupby(['bank', 'vader_label']).size().unstack(fill_value=0)
    sentiment_pct = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100
    
    # Custom aesthetic colors
    colors = ['#e74c3c', '#95a5a6', '#2ecc71'] # red, neutral gray, green
    
    ax = sentiment_pct.plot(kind='bar', stacked=True, color=colors, figsize=(10, 6), width=0.6)
    plt.title('Sentiment Distribution by Bank (VADER Analysis)', pad=20)
    plt.xlabel('Bank')
    plt.ylabel('Percentage (%)')
    plt.xticks(rotation=0)
    plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add percentage labels
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy() 
        if height > 5: # Only label if significant
            ax.text(x + width/2, 
                    y + height/2, 
                    f'{height:.1f}%', 
                    horizontalalignment='center', 
                    verticalalignment='center',
                    color='white',
                    weight='bold')
                    
    plt.tight_layout()
    plt.savefig('notebooks/plots/sentiment_distribution.png', dpi=300)
    plt.close()
    print("Generated sentiment_distribution.png")

    # 2. Rating Distribution per Bank
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x='rating', hue='bank', palette='viridis')
    plt.title('App Rating Distribution per Bank', pad=20)
    plt.xlabel('Rating (Stars)')
    plt.ylabel('Number of Reviews')
    plt.legend(title='Bank')
    plt.tight_layout()
    plt.savefig('notebooks/plots/ratings_by_bank.png', dpi=300)
    plt.close()
    print("Generated ratings_by_bank.png")

    # 3. Top Keywords/Themes Frequency per Bank
    plt.figure(figsize=(12, 8))
    theme_counts = df.groupby(['identified_theme', 'bank']).size().unstack(fill_value=0)
    theme_counts = theme_counts.sort_values(by='CBE', ascending=True) # Sort by CBE for clean display
    
    theme_counts.plot(kind='barh', figsize=(12, 8), width=0.8, colormap='coolwarm')
    plt.title('Distribution of Identified Themes across Banks', pad=20)
    plt.xlabel('Number of Reviews')
    plt.ylabel('Identified Theme')
    plt.legend(title='Bank', loc='lower right')
    plt.tight_layout()
    plt.savefig('notebooks/plots/themes_frequency.png', dpi=300)
    plt.close()
    print("Generated themes_frequency.png")

if __name__ == '__main__':
    generate_visualizations()
