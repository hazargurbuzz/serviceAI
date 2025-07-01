import pandas as pd
import gspread
import joblib
from oauth2client.service_account import ServiceAccountCredentials
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from datetime import datetime
import os

def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def preprocess(df):
    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["Tarih"])

    df["gun_farki"] = (datetime.today() - df["Tarih"]).dt.days
    df["churn"] = df["gun_farki"] > 180

    df["upsell"] = df["Upsell"].fillna("Hayır").apply(lambda x: 1 if str(x).lower() == "evet" else 0)
    df["tekrar"] = df["Tekrar Geliş"].fillna("Hayır").apply(lambda x: 1 if str(x).lower() == "evet" else 0)

    X = df[["upsell", "tekrar", "gun_farki"]]
    y = df["churn"].astype(int)

    return X, y

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    X, y = preprocess(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    print("Model Performansı:")
    print(classification_report(y_test, model.predict(X_test)))

    # Kaydet
    joblib.dump(model, "churn_model.pkl")
    print("churn_model.pkl olarak kaydedildi.")
