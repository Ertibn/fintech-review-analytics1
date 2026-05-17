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
│   └── raw/
│       ├── cleaned_reviews.csv    # Preprocessed and normalized review dataset
│       └── sentiment_reviews.csv  # Enriched reviews with sentiment labels and themes
├── notebooks/
│   ├── plots/
│   │   ├── ratings_by_bank.png    # Seaborn Star Ratings Distribution
│   │   ├── sentiment_distribution.png  # Seaborn Sentiment Split by Bank
│   │   └── themes_frequency.png   # Seaborn Theme Frequencies per Bank
│   ├── task1_data_scraping_preprocessing.ipynb # Ingestion & Cleaning Notebook
│   └── task2_sentiment_thematic_analysis.ipynb # Sentiment & Thematic Notebook
├── scripts/
│   ├── create_notebooks.py        # Programmatic notebook generator script
│   ├── generate_plots.py          # Seaborn plotting engine
│   ├── scrape_reviews.py          # Google Play Store review extraction pipeline
│   └── sentiment_analysis.py      # VADER and Keyword theme classifier
├── tests/
│   └── test_pipeline.py           # Pytest unit tests for NLP and Data Cleaning
├── dashboard.html                 # Interactive premium dark mode analytics dashboard
├── requirements.txt               # Project dependency specification
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
    Scrapes the newest 600 reviews for CBE, BOA, and Dashen Bank. It filters duplicates, normalizes dates, and saves a clean dataset to `data/raw/cleaned_reviews.csv`.
    ```bash
    python scripts/scrape_reviews.py
    ```

2.  **Execute Sentiment & Thematic Classifier:**
    Ingests the cleaned reviews and runs VADER sentiment analysis to label reviews as `positive`, `negative`, or `neutral`. It classifies user complaints into 5 fintech operational themes.
    ```bash
    python scripts/sentiment_analysis.py
    ```

3.  **Generate Visualization Charts:**
    Processes the sentiment-enriched dataset to compile and save three premium Seaborn charts into `notebooks/plots/`.
    ```bash
    python scripts/generate_plots.py
    ```

### Running Jupyter Notebooks

Alternatively, you can open and run the fully annotated notebooks to see step-by-step executions:
```bash
jupyter notebook
```
*   Navigate to `notebooks/task1_data_scraping_preprocessing.ipynb` to view the data collection workflow.
*   Navigate to `notebooks/task2_sentiment_thematic_analysis.ipynb` to view the sentiment, keyword mapping, and visualization generation workflow.

---

## 🧪 Running Automated Unit Tests

A robust test suite is established to ensure continuous integration. The unit tests verify the sentiment intensity classifier and dataset preprocessing rules.

Run the test suite locally with `pytest`:
```bash
pytest tests/
```

On every push to the `main` branch, **GitHub Actions** automatically runs this test suite to guarantee continuous integration (CI) is completely green.

---

## 📊 Interactive Analytics Dashboard

The project includes a premium, high-fidelity, single-page web dashboard (`dashboard.html`) to display results interactively.

### Dashboard Features:
*   **KPI Metrics Cards:** Displays total reviews processed, positive sentiment ratio, and average star ratings dynamically.
*   **Interactive Visualizations:** Renders responsive sentiment breakdowns and thematic charts powered by **Chart.js** CDN.
*   **Search & Filter Engine:** Allows real-time filtering of customer reviews by specific bank, star rating, or custom keyword search.
*   **Glassmorphism UI:** Formatted with a dark-mode premium interface, responsive CSS grid, and Outfit/Inter typography.

### Run Dashboard Locally:
Start a local lightweight web server from the project directory:
```bash
python -m http.server 8000
```
Open your browser and navigate to: **`http://localhost:8000/dashboard.html`**

---

## 💡 Key Analytical Findings (Interim Phase)

1.  **Apollo (Bank of Abyssinia) Leads:** Holds a spectacular **82.3% Positive Sentiment** rate, driven heavily by praise for its sleek, modern UI/UX and fast login flows.
2.  **CBE (CBEBirr Plus) Faces Pain Points:** Suffers from a high **40.0% Negative Sentiment** rate. The key drivers are frequent transaction slowdowns, failed transfers, and delays in receiving login OTP (One-Time Passwords).
3.  **Dashen Bank (Amole) Stability:** Maintains a solid **62.7% Positive Sentiment** split, with some user frustrations regarding daily transaction limits and wallet-to-bank sync issues.

---

*Report prepared by Omega Consultancy. Code and pipeline released under the MIT License.*
