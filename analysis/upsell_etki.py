import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scipy.stats import chi2_contingency
import os

# Google Sheet bağlantısı
def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def analyze_upsell_effect(df):
    # Temizle
    df = df[(df["Upsell"].notna()) & (df["Tekrar Geliş"].notna())]
    df["upsell"] = df["Upsell"].apply(lambda x: 1 if str(x).lower() == "evet" else 0)
    df["tekrar"] = df["Tekrar Geliş"].apply(lambda x: 1 if str(x).lower() == "evet" else 0)

    # Kontenjan tablosu oluştur
    contingency = pd.crosstab(df["upsell"], df["tekrar"])
    print("\nKontenjan Tablosu (Upsell vs Tekrar Geliş):\n")
    print(contingency)

    # Ki-kare testi
    chi2, p, dof, expected = chi2_contingency(contingency)

    print("\n🔍 Ki-kare Test Sonuçları:")
    print(f"Chi2 Değeri: {chi2:.4f}")
    print(f"p-değeri: {p:.4f}")

    if p < 0.05:
        print("\nSonuç: Upsell yapılan müşterilerin tekrar gelme oranı istatistiksel olarak farklıdır.")
    else:
        print("\nSonuç: Upsell etkisi istatistiksel olarak anlamlı değil.")

    return chi2, p, contingency

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    chi2, p, tablo = analyze_upsell_effect(df)

def get_upsell_effect_comment():
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    _, p, _ = analyze_upsell_effect(df)

    if p < 0.05:
        return "Upsell yapılan müşterilerin tekrar gelme oranı anlamlı derecede yüksektir (p < 0.05)."
    else:
        return "Upsell etkisi istatistiksel olarak anlamlı değildir (p ≥ 0.05)."
