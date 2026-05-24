# Manga Publisher Drop Prediction (Manga Status Predictor)
**An End-to-End Machine Learning Project for Predicting Manga Series Discontinuation**

## Project Overview
A classic pain point for manga readers is buying the first few volumes of a new series, only to have the local publisher "drop" or discontinue the translation indefinitely. This project leverages data engineering and machine learning to predict the "drop risk" of a manga series the moment the publisher announces the license or releases the first volume. 

**Primary Goal:** To predict the publishing status (Safe / At-Risk of being dropped) based purely on day-one features, helping readers make informed purchasing decisions.

---

## Architecture & Data Pipeline
This project implements the **Medallion Architecture** to manage the ETL data pipeline, from raw extraction to an ML-ready dataset:

*   **Bronze Layer (Raw Data):** Web Scraping to extract volume-level data directly from the local publisher's website (Phoenix), including prices, release dates, and premium set availability.
*   **Silver Layer (Enriched Data):** REST API Integration with Jikan API (MyAnimeList) to fetch the original Japanese source material data (authors, latest Japanese volume count, genres) with built-in rate limit handling.
*   **Gold Layer (Analytical Base Table):** Aggregating volume-level data into series-level data and performing Feature Engineering to prepare predictors for the machine learning model.

---

## Exploratory Data Analysis (EDA)
Before training the model, the data was analyzed to uncover the publisher's behavioral patterns:

### 1. Target Distribution
<img width="695" height="475" alt="distribution" src="https://github.com/user-attachments/assets/9c603d91-5dc6-4121-ab3c-a2df24a39621" />


> **Insight:** The initial target class was highly imbalanced. By redefining a "Dropped" series as one with `> 365 days since the last release AND available un-translated Japanese volumes`, the dataset became much more balanced and optimal for ML training (~75% Safe vs ~25% Dropped).

### 2. Volume Gap Analysis
<img width="930" height="552" alt="gap" src="https://github.com/user-attachments/assets/fc6dc586-205a-4f83-8e95-d49da17519ee" />


> **Insight:** The boxplot clearly illustrates that discontinued manga typically have a significantly larger gap between the number of available Japanese volumes and published local volumes, serving as a strong early warning sign.

---

## Machine Learning Model
### Data Preprocessing
*   **One-Hot Encoding:** Converted the `Genres` list into binary categorical columns.
*   **Preventing Data Leakage:** Strictly removed future-reflecting features (e.g., `vol_gap`, `max_vol_th`, `days_since_last_release`). The model was forced to evaluate risk using only features available on **Day 1** of a new manga release.

### Model Performance
A **Random Forest Classifier** was utilized for its excellent performance on tabular data and its explainability.
*   **Accuracy:** ~81% (in strict No Data Leakage mode).
*   **Precision (Drop class):** High precision in identifying high-risk manga, making it a reliable tool for risk aversion.

### Feature Importance (The Publisher's Secret)
<img width="950" height="552" alt="Feature Importance" src="https://github.com/user-attachments/assets/3b9f6b7e-f6a1-4803-89ec-0fc219fde837" />

> **Business Insight (Domain Knowledge):** The model heavily weighted **Price / Average Price** as the #1 predictor. This perfectly mirrors the publisher's real-world strategy: if a series launches with an expensive "Premium Set," it signals high publisher confidence and a near-zero chance of being dropped.

---

## How to Run the Pipeline
1.  Run Scripts `manga_flow.py` to scrape data and fetch API details (Note: API fetching includes intentional delays to respect rate limits) and generate the Gold Layer dataset.
2.  Run the `manga_eda.ipynb` Notebook to explore the data and train the model (the trained model will be saved in the `/models` directory).
3.  Run `predict_new_manga.py` to input new manga details and get an AI-generated risk prediction.

---

## Future Work
*   **Web Application:** Integrate the trained model into a Web App with a user-friendly UI showing a "Risk Percentage Bar" for newly announced titles.
*   **Expand Publishers:** Scale the web scraper to include other major local publishers to compare drop rates across the industry.
