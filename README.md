# Customer Experience Analytics for Fintech Apps (Week 2 Challenge)

[![Unit Tests](https://github.com/Ertibn/fintech-review-analytics1/actions/workflows/unittests.yml/badge.svg)](https://github.com/Ertibn/fintech-review-analytics1/actions/workflows/unittests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

An automated data engineering and natural language processing (NLP) pipeline designed to extract, preprocess, analyze, and visualize Google Play Store reviews for three flagship Ethiopian mobile banking applications:
1.  **CBEBirr Plus** (Commercial Bank of Ethiopia) — App ID: `prod.cbe.birr`
2.  **Apollo Digital Banking** (Bank of Abyssinia) — App ID: `com.boa.apollo`
3.  **Dashen Amole Light** (Dashen Bank) — App ID: `com.cr2.amolelight`

This project is built as part of the **10 Academy Artificial Intelligence Mastery (KAIM)** program to translate raw user reviews into competitive product intelligence for Ethiopian banks.

---

## 📁 Repository Structure

```text
fintech-review-analytics/
├── .github/
│   └── workflows/
│       └── unittests.yml          # GitHub Actions CI/CD Pipeline
├── data/
│   └── raw/                       # Generated local review outputs (ignored by git)
├── notebooks/
│   ├── plots/                     # Generated visualizations
│   │   ├── ratings_by_bank.png
│   │   ├── sentiment_distribution.png
│   │   ├── themes_frequency.png
│   │   └── sentiment_trend.png
│   ├── task1_data_scraping_preprocessing.ipynb
│   └── task2_sentiment_thematic_analysis.ipynb
├── scripts/
│   ├── create_notebooks.py
│   ├── database_ingestion.py      # PostgreSQL/SQLite persistence pipeline
│   ├── extract_insights.py        # Bank-level insights summary generation
│   ├── generate_plots.py          # Visualization generation for analysis
│   ├── scrape_reviews.py          # Google Play Store review extraction pipeline
│   └── sentiment_analysis.py      # Transformer-based sentiment and theme extraction
├── tests/
│   ├── test_database.py
│   └── test_pipeline.py           # Pytest unit tests for NLP and data cleaning
├── requirements.txt               # Project dependency specification
├── scripts/schema.sql             # PostgreSQL schema definitions
├── .gitignore                     # Git exclusion rules
└── README.md                      # Professional project documentation (this file)
```

---

## 🚀 Getting Started & Installation

Follow these steps to set up the workspace, install dependencies, and execute the analytical pipeline locally.

### 1. Prerequisites
Ensure you have **Python 3.10 or higher** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Ertibn/fintech-review-analytics1.git
cd fintech-review-analytics1
```

### 3. Create a Virtual Environment
Initialize a clean Python virtual environment to manage dependencies locally:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🛠️ Pipeline Execution & Usage Guide

The data pipeline can be executed in two ways: through **executable Python scripts** or **interactive Jupyter Notebooks**.

### Running Python Scripts

1.  **Execute Review Scraper:**
    Scrapes the newest English reviews for CBE, BOA, and Dashen Bank. It de-duplicates reviews, filters out non-English content, normalizes dates, and saves the cleaned dataset to `data/raw/cleaned_reviews.csv`.
    ```bash
    python scripts/scrape_reviews.py
    ```

2.  **Execute Sentiment & Thematic Classifier:**
    Loads the cleaned dataset, applies VADER and DistilBERT sentiment scoring, labels each review as `positive`, `negative`, or `neutral`, and extracts fintech themes.
    ```bash
    python scripts/sentiment_analysis.py
    ```

3.  **Create the Database and Insert Processed Reviews:**
    Uses PostgreSQL when available, otherwise falls back to SQLite for local development. The database schema is also available in `scripts/schema.sql`.
    ```bash
    python scripts/database_ingestion.py
    ```

4.  **Generate Stakeholder Visualizations:**
    Produces bank-level sentiment, rating, theme frequency, and sentiment trend plots for reporting.
    ```bash
    python scripts/generate_plots.py
    ```

5.  **Extract Bank Insights:**
    Builds a concise insights summary for each bank based on sentiment distribution, theme counts, and top keywords.
    ```bash
    python scripts/extract_insights.py
    ```

### Running Jupyter Notebooks

Alternatively, you can open and run the fully annotated notebooks to see step-by-step executions:
```bash
jupyter notebook
```
*   Navigate to `notebooks/task1_data_scraping_preprocessing.ipynb` to view the data collection workflow.
*   Navigate to `notebooks/task2_sentiment_thematic_analysis.ipynb` to view the sentiment, keyword mapping, and visualization generation workflow.

---

## 🔠 English-Only Filtering Engine

Google Play Store reviews for Ethiopian banking apps commonly contain Amharic text, either written in native Ethiopic Unicode characters (Ge'ez script) or transliterated into Latin characters (e.g., *"Betam arif new"*, *"tiru mobile bank"*). 

To ensure **100% clean English reviews**, we implemented a professional, multi-layered language verification engine:
1.  **Ge'ez Character Block Check:** Uses regular expressions to scan for and immediately discard text containing characters in the Ethiopic Unicode range (`\u1200-\u137F`, `\u2D80-\u2DDF`, `\uAB00-\uAB2F`).
2.  **Short Review Safeguard:** Pre-approves high-frequency short reviews (e.g., *"good"*, *"excellent"*, *"crashes"*, *"bad app"*, *"ok"*) against a curated English lexicon to prevent naive language models from misclassifying them (which often happens with single-word responses).
3.  **Transliteration Density Filter:** Rejects reviews that contain a high density (>30%) of transliterated Amharic slang/vocabulary words (e.g., *betam*, *arif*, *temetatagn*, *nw*, *new*, *gobez*, *tiru*, *konjo*).
4.  **Hugging Face / LangDetect Verification:** Runs `langdetect` on the cleaned and validated review string to confirm the final classification is `'en'`.
5.  **Heuristic Token Overlap Fallback:** If `langdetect` fails due to formatting, the script evaluates the text against a dictionary of fintech terms and keeps it if there is a strong English overlap.

---

## 🧪 Running Automated Unit Tests

A robust test suite is established to ensure continuous integration. The unit tests verify the sentiment intensity classifier and dataset preprocessing rules.

Run the test suite locally with `pytest`:
```bash
pytest tests/
```

On every push to the `main` branch, **GitHub Actions** automatically runs this test suite to guarantee continuous integration (CI) is completely green.

---

## 💡 Key Analytical Findings (Interim Phase)

1.  **Apollo (Bank of Abyssinia) Leads:** Holds a spectacular **82.3% Positive Sentiment** rate, driven heavily by praise for its sleek, modern UI/UX and fast login flows.
2.  **CBE (CBEBirr Plus) Faces Pain Points:** Suffers from a high **40.0% Negative Sentiment** rate. The key drivers are frequent transaction slowdowns, failed transfers, and delays in receiving login OTP (One-Time Passwords).
3.  **Dashen Bank (Amole) Stability:** Maintains a solid **62.7% Positive Sentiment** split, with some user frustrations regarding daily transaction limits and wallet-to-bank sync issues.

---

*Report prepared by Omega Consultancy. Code and pipeline released under the MIT License.*

