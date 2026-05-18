import json
import os

def create_task1_notebook():
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Task 1: Google Play Store Review Scraper & Preprocessing\n",
                    "## 10 Academy Week 2 Challenge: Fintech Customer Experience Analytics\n",
                    "\n",
                    "This notebook implements the data engineering pipeline to scrape, clean, and preprocess customer reviews for the three major Ethiopian banking apps:\n",
                    "1. **CBE (Commercial Bank of Ethiopia)** - `prod.cbe.birr`\n",
                    "2. **BOA (Bank of Abyssinia - Apollo)** - `com.boa.apollo`\n",
                    "3. **Dashen Bank (Amole)** - `com.cr2.amolelight`"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Setup & Libraries"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    "from google_play_scraper import Sort, reviews\n",
                    "from datetime import datetime\n",
                    "import os\n",
                    "import sys\n",
                    "\n",
                    "print(\"Libraries loaded successfully.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Define Ingestion & Scraping Logic\n",
                    "We scrape up to 1500 reviews per bank to ensure a statistically robust baseline, focusing on recent user feedback."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import re\n",
                    "from langdetect import detect\n",
                    "\n",
                    "# Common English words/short terms seen in reviews\n",
                    "SHORT_ENGLISH_WORDS = {\n",
                    "    'good', 'excellent', 'nice', 'best', 'perfect', 'bad', 'worst',\n",
                    "    'great', 'love', 'fast', 'slow', 'okay', 'ok', 'super', 'cool',\n",
                    "    'working', 'fine', 'thanks', 'thank', 'you', 'app', 'easy', 'simple',\n",
                    "    'helpful', 'use', 'useful', 'crashes', 'slow', 'lag', 'crashed',\n",
                    "    'error', 'login', 'problem', 'issues', 'issue', 'otp', 'money',\n",
                    "    'transfer', 'trust', 'trustworthy', 'worst', 'poor', 'happy',\n",
                    "    'pleased', 'satisfactory', 'satisfied', 'five', 'star', 'stars',\n",
                    "    'awesome', 'wonderful', 'amazing', 'brilliant', 'fantastic'\n",
                    "}\n",
                    "\n",
                    "def is_english(text):\n",
                    "    if not text or not isinstance(text, str):\n",
                    "        return False\n",
                    "    \n",
                    "    text_clean = text.strip()\n",
                    "    if not text_clean:\n",
                    "        return False\n",
                    "        \n",
                    "    # Filter out Ge'ez script (Amharic characters)\n",
                    "    if re.search(r'[\\u1200-\\u137F\\u2D80-\\u2DDF\\uAB00-\\uAB2F]', text_clean):\n",
                    "        return False\n",
                    "        \n",
                    "    # Check if it contains latin characters at all\n",
                    "    if not re.search(r'[a-zA-Z]', text_clean):\n",
                    "        return False\n",
                    "        \n",
                    "    words = [w.lower().strip(\".,!?\\\"'()[]{}*-+=\") for w in text_clean.split()]\n",
                    "    words = [w for w in words if w]\n",
                    "    \n",
                    "    if not words:\n",
                    "        return False\n",
                    "        \n",
                    "    if len(words) <= 3:\n",
                    "        if any(w in SHORT_ENGLISH_WORDS for w in words):\n",
                    "            return True\n",
                    "            \n",
                    "    try:\n",
                    "        lang = detect(text_clean)\n",
                    "        if lang == 'en':\n",
                    "            amharic_transliterated_words = {\n",
                    "                'betam', 'arif', 'temetatagn', 'gobez', 'tiru', 'konjo', 'temesgen',\n",
                    "                'ayesram', 'alrisam', 'nw', 'new', 'des', 'yilal', 'yamral', 'yishalal',\n",
                    "                'nechew', 'gar', 'le', 'sew', 'ke', 'na', 'chahn', 'tew'\n",
                    "            }\n",
                    "            amharic_word_count = sum(1 for w in words if w in amharic_transliterated_words)\n",
                    "            if amharic_word_count / len(words) > 0.3:\n",
                    "                return False\n",
                    "            return True\n",
                    "    except Exception:\n",
                    "        pass\n",
                    "        \n",
                    "    english_overlap = sum(1 for w in words if w in SHORT_ENGLISH_WORDS)\n",
                    "    if len(words) > 0 and (english_overlap / len(words)) >= 0.5:\n",
                    "        return True\n",
                    "        \n",
                    "    return False\n",
                    "\n",
                    "def scrape_bank_reviews(app_id, bank_name, num_reviews=1500):\n",
                    "    print(f\"Scraping reviews for {bank_name} ({app_id})...\")\n",
                    "    result = []\n",
                    "    \n",
                    "    try:\n",
                    "        batch, token = reviews(\n",
                    "            app_id,\n",
                    "            lang='en',\n",
                    "            country='us',\n",
                    "            sort=Sort.NEWEST,\n",
                    "            count=num_reviews\n",
                    "        )\n",
                    "        result.extend(batch)\n",
                    "    except Exception as e:\n",
                    "        print(f\"Error scraping {bank_name}: {e}\")\n",
                    "        return pd.DataFrame()\n",
                    "\n",
                    "    # Extract required fields\n",
                    "    data = []\n",
                    "    for r in result:\n",
                    "        row = {\n",
                    "            'id': r.get('reviewId'),\n",
                    "            'review': r.get('content'),\n",
                    "            'rating': r.get('score'),\n",
                    "            'date': r.get('at'),\n",
                    "            'bank': bank_name,\n",
                    "            'source': 'Google Play Store'\n",
                    "        }\n",
                    "        data.append(row)\n",
                    "        \n",
                    "    df = pd.DataFrame(data)\n",
                    "    print(f\"Successfully collected {len(df)} raw reviews for {bank_name}.\")\n",
                    "    return df"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Execute Data Extraction Pipeline"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [],
                "source": [
                    "app_ids = {\n",
                    "    'CBE': 'prod.cbe.birr',\n",
                    "    'BOA': 'com.boa.apollo',\n",
                    "    'Dashen': 'com.cr2.amolelight'\n",
                    "}\n",
                    "\n",
                    "dfs = []\n",
                    "for bank, app_id in app_ids.items():\n",
                    "    df_bank = scrape_bank_reviews(app_id, bank, 1500)\n",
                    "    if not df_bank.empty:\n",
                    "        dfs.append(df_bank)\n",
                    "\n",
                    "raw_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()\n",
                    "print(f\"Total combined raw reviews: {len(raw_df)}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Data Cleaning & Preprocessing Steps\n",
                    "1. **De-duplication**: Filter unique reviews using `id`.\n",
                    "2. **Null Filtering**: Drop records with missing text/rating.\n",
                    "3. **Language Filtering**: Keep only English reviews.\n",
                    "4. **Date Standardization**: Normalize dates to `YYYY-MM-DD` ISO format."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 4,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def preprocess_data(df):\n",
                    "    if df.empty:\n",
                    "        return df\n",
                    "    \n",
                    "    # 1. Remove duplicates\n",
                    "    initial_count = len(df)\n",
                    "    df = df.drop_duplicates(subset=['id'])\n",
                    "    print(f\"Removed {initial_count - len(df)} duplicates.\")\n",
                    "    \n",
                    "    # 2. Filter null reviews/ratings\n",
                    "    df = df.dropna(subset=['review', 'rating'])\n",
                    "    \n",
                    "    # 3. Filter English only reviews\n",
                    "    print(\"Filtering English-only reviews...\")\n",
                    "    df = df[df['review'].apply(is_english)]\n",
                    "    \n",
                    "    # 4. Format Date to YYYY-MM-DD\n",
                    "    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')\n",
                    "    \n",
                    "    return df\n",
                    "\n",
                    "cleaned_df = preprocess_data(raw_df)\n",
                    "print(f\"Total processed and cleaned reviews: {len(cleaned_df)}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Save Cleaned Dataset\n",
                    "We serialize the resulting dataset into `data/raw/cleaned_reviews.csv`."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 5,
                "metadata": {},
                "outputs": [],
                "source": [
                    "os.makedirs('../data/raw', exist_ok=True)\n",
                    "cleaned_df.to_csv('../data/raw/cleaned_reviews.csv', index=False)\n",
                    "print(\"Cleaned reviews successfully saved to '../data/raw/cleaned_reviews.csv'.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Exploratory Data Summary"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 6,
                "metadata": {},
                "outputs": [],
                "source": [
                    "print(cleaned_df.groupby('bank')['rating'].describe())\n",
                    "print(\"\\nFirst 5 cleaned records:\")\n",
                    "print(cleaned_df.head())"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    os.makedirs('notebooks', exist_ok=True)
    with open('notebooks/task1_data_scraping_preprocessing.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    print("Created notebooks/task1_data_scraping_preprocessing.ipynb")

def create_task2_notebook():
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Task 2: Sentiment Analysis, Thematic Mapping & Data Visualization\n",
                    "## 10 Academy Week 2 Challenge: Fintech Customer Experience Analytics\n",
                    "\n",
                    "This notebook implements the Natural Language Processing (NLP) pipeline to evaluate user feedback across CBE, BOA, and Dashen Bank. \n",
                    "We use the lexicon-based **VADER Sentiment Analysis** model and execute keyword-based thematic extraction to segment user pain points into five primary fintech domains."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Setup & Imports"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "import os\n",
                    "\n",
                    "print(\"Libraries loaded successfully.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Ingest Cleaned Dataset"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": [
                    "df = pd.read_csv('../data/raw/cleaned_reviews.csv')\n",
                    "print(f\"Loaded {len(df)} cleaned records.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Run VADER Sentiment Classifier\n",
                    "VADER assigns compound sentiment scores between -1.0 (highly negative) and +1.0 (highly positive)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [],
                "source": [
                    "analyzer = SentimentIntensityAnalyzer()\n",
                    "\n",
                    "def get_vader_sentiment(text):\n",
                    "    if not isinstance(text, str):\n",
                    "        return 'neutral', 0.0\n",
                    "    score = analyzer.polarity_scores(text)['compound']\n",
                    "    if score >= 0.05:\n",
                    "        return 'positive', score\n",
                    "    elif score <= -0.05:\n",
                    "        return 'negative', score\n",
                    "    else:\n",
                    "        return 'neutral', score\n",
                    "\n",
                    "sentiments = [get_vader_sentiment(t) for t in df['review']]\n",
                    "df['sentiment_label'] = [s[0] for s in sentiments]\n",
                    "df['sentiment_score'] = [s[1] for s in sentiments]\n",
                    "\n",
                    "print(\"Sentiment classification completed.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Run Thematic extraction mapping\n",
                    "We classify user feedback into 5 major categories:\n",
                    "1. `Account Access & Authentication` (login, OTP, register)\n",
                    "2. `Transaction & Payment Issues` (transfer, send, deposit, balance, fee)\n",
                    "3. `App Performance & Stability` (crash, slow, freeze, error)\n",
                    "4. `UI & Customer Experience` (interface, modern, design, update)\n",
                    "5. `Customer Support & Service` (call, customer, response, service)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 4,
                "metadata": {},
                "outputs": [],
                "source": [
                    "themes = {\n",
                    "    'Account Access & Authentication': ['login', 'log in', 'otp', 'code', 'password', 'pin', 'register', 'verification', 'opened'],\n",
                    "    'Transaction & Payment Issues': ['transfer', 'send', 'payment', 'fee', 'charge', 'money', 'transaction', 'balance', 'deduct', 'receive', 'pay', 'double'],\n",
                    "    'App Performance & Stability': ['crash', 'slow', 'freeze', 'loading', 'network', 'error', 'bug', 'connection', 'open', 'worst', 'bad'],\n",
                    "    'UI & Customer Experience': ['ui', 'ux', 'interface', 'beautiful', 'clean', 'design', 'update', 'awesome', 'good', 'nice', 'easy'],\n",
                    "    'Customer Support & Service': ['support', 'customer', 'care', 'agent', 'help', 'response', 'bank', 'service', 'branch']\n",
                    "}\n",
                    "\n",
                    "def map_theme(text):\n",
                    "    if not isinstance(text, str):\n",
                    "        return 'Other / General Feedback'\n",
                    "    text_lower = text.lower()\n",
                    "    for theme, keywords in themes.items():\n",
                    "        for kw in keywords:\n",
                    "            if kw in text_lower:\n",
                    "                return theme\n",
                    "    return 'Other / General Feedback'\n",
                    "\n",
                    "df['identified_theme'] = [map_theme(t) for t in df['review']]\n",
                    "print(\"Thematic extraction mapping completed.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Save Results"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 5,
                "metadata": {},
                "outputs": [],
                "source": [
                    "df.to_csv('../data/raw/sentiment_reviews.csv', index=False)\n",
                    "print(\"Saved results to '../data/raw/sentiment_reviews.csv'.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Generate Plot Visualizations"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 6,
                "metadata": {},
                "outputs": [],
                "source": [
                    "sns.set_theme(style=\"whitegrid\")\n",
                    "\n",
                    "# Plot 1: Sentiment Distribution\n",
                    "plt.figure(figsize=(10, 6))\n",
                    "sns.countplot(data=df, x='bank', hue='sentiment_label', palette='viridis')\n",
                    "plt.title('Sentiment Distribution per Ethiopian Banking App', fontsize=14, fontweight='bold')\n",
                    "plt.xlabel('Bank', fontsize=12)\n",
                    "plt.ylabel('Review Count', fontsize=12)\n",
                    "plt.legend(title='Sentiment')\n",
                    "plt.tight_layout()\n",
                    "plt.savefig('../notebooks/plots/sentiment_distribution.png')\n",
                    "plt.show()\n",
                    "\n",
                    "# Plot 2: Rating star Distribution\n",
                    "plt.figure(figsize=(10, 6))\n",
                    "sns.countplot(data=df, x='rating', hue='bank', palette='magma')\n",
                    "plt.title('Star Ratings Distribution per Bank App', fontsize=14, fontweight='bold')\n",
                    "plt.xlabel('Rating (Stars)', fontsize=12)\n",
                    "plt.ylabel('Count', fontsize=12)\n",
                    "plt.tight_layout()\n",
                    "plt.savefig('../notebooks/plots/ratings_by_bank.png')\n",
                    "plt.show()\n",
                    "\n",
                    "# Plot 3: Themes Frequency\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "theme_counts = df[df['identified_theme'] != 'Other / General Feedback']\n",
                    "sns.countplot(data=theme_counts, y='identified_theme', hue='bank', palette='muted')\n",
                    "plt.title('Common Play Store Complaint & Praise Themes per Bank', fontsize=14, fontweight='bold')\n",
                    "plt.xlabel('Review Count', fontsize=12)\n",
                    "plt.ylabel('Theme', fontsize=12)\n",
                    "plt.tight_layout()\n",
                    "plt.savefig('../notebooks/plots/themes_frequency.png')\n",
                    "plt.show()"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    os.makedirs('notebooks', exist_ok=True)
    with open('notebooks/task2_sentiment_thematic_analysis.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    print("Created notebooks/task2_sentiment_thematic_analysis.ipynb")

if __name__ == '__main__':
    create_task1_notebook()
    create_task2_notebook()
