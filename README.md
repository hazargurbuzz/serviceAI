ServiceAI – AI-Powered Automotive Service CRM and ROI System

ServiceAI is a complete AI-powered CRM and automation system designed for automotive service centers. It supports intelligent customer tracking, upsell opportunity detection, churn analysis, service scheduling, and ROI reporting – all integrated with Google Sheets.

Features

Google Sheets–based service reservation tracking

Automated appointment reminders and 6-month service recalls

FAQ chatbot integration

Churn prediction using logistic regression

A/B test–based upsell impact analysis

Customer segmentation using K-Means + behavioral interpretation

Service demand forecasting (time series)

PDF report generation with graphs, statistics, and actionable insights

Deep learning–based personalized service recommender system

Tech Stack

Python (pandas, scikit-learn, matplotlib, tensorflow)

gspread for Google Sheets API

FPDF for report generation

KMeans, Logistic Regression, A/B Testing, Time Series

TheFuzz for fuzzy string matching in recommender

Project Structure

serviceAI/
├── analysis/ # Churn, segmentation, forecasting, ROI reports

├── core/ # Reminder bots, chatbot, Google Sheets connectors

├── reports/ # Auto-generated charts and PDF reports

├── templates/ # Optional: Flask web UI templates

├── app.py # Web app entry point (optional)

├── recommend.py # Recommender system + PDF report generator

├── train_model.py # Model training script

├── recommender_ncf.py # (Legacy or alternative recommender code)

├── README.md # This file

├── .gitignore # To ignore credentials & reports

├── credentials.json # Google API credentials (should be .gitignored)

└── requirements.txt # Python dependencies

Installation & Setup

Clone the repository:
git clone https://github.com/hazargurbuzz/serviceAI.git
cd serviceAI

Install dependencies:
pip install -r requirements.txt

Place your Google API credentials as credentials.json in the project root.

How to Run

Train the AI Model
python train_model.py

Generate Recommendations and PDF Report
python recommend.py

Enter customer name when prompted.

Notes

Make sure your Google Sheets contains up-to-date data.

The recommender system uses deep learning and fuzzy matching for personalized suggestions.

PDF reports are generated using FPDF, with Turkish character normalization.

Contribution & Support

Contributions welcome! Open issues or submit pull requests for improvements.

Last updated: 2025-07-02
