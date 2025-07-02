# ServiceAI – AI-Powered Automotive Service CRM and ROI System

**ServiceAI** is a complete AI-powered CRM and automation system designed for automotive service centers. It supports intelligent customer tracking, upsell opportunity detection, churn analysis, service scheduling, and ROI reporting – all integrated with Google Sheets.

---
## Features

-  Google Sheets–based service reservation tracking
-  Automated appointment reminders and 6-month service recalls
-  FAQ chatbot integration
-  Churn prediction using logistic regression
-  A/B test–based upsell impact analysis
-  Customer segmentation using K-Means + behavioral interpretation
-  Service demand forecasting (time series)
-  PDF report generation with graphs, statistics, and actionable insights

---
## Tech Stack

- **Python** (pandas, scikit-learn, matplotlib)
- **gspread** for Google Sheets API
- **FPDF** for report generation
- **KMeans**, **Logistic Regression**, A/B Testing, Time Series

---
##  Project Structure
serviceAI/

├── analysis/ # Churn, segmentation, forecasting, ROI reports

├── core/ # Reminder bots, chatbot, Google Sheets connectors

├── reports/ # Auto-generated charts and PDF reports

├── templates/ # Optional: Flask web UI

├── app.py # Web app entry point (optional)

├── README.md # This file

├── .gitignore # To ignore credentials & reports

```bash
pip install -r requirements.txt
python analysis/roi_dashboard.py

---
## How to Run
1. Install dependencies:
```bash
pip install -r requirements.txt
python analysis/roi_dashboard.py



