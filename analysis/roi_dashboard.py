import gspread
import joblib
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dateutil.relativedelta import relativedelta
from upsell_etki import get_upsell_effect_comment
from segmentasyon import get_segment_yorumlari
from segmentasyon import get_segment_ozet_ve_yorum
from tahmin_servis import tahmin_uret, grafik_ciz, yorumla_tahmin
from segmentasyon import get_segment_ozet_ve_yorum

def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).worksheet("Sayfa1")

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "ROI ve CRM Kontrol Paneli", ln=True, align="C")

    def body_text(self, text):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, text)

    def insert_image(self, path, title=""):
        self.set_font("Arial", "B", 12)
        if title:
            self.cell(0, 10, title, ln=True)
        self.image(path, w=180)
        self.ln(10)

    def churn_tablosu(self, tablo):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, temizle("En Riskli 10 Müsteri (Churn Tahmini)"), ln=True)
        self.set_font("Arial", "B", 11)
        self.cell(60, 10, "Ad Soyad", border=1)
        self.cell(40, 10, "Son Servis", border=1)
        self.cell(40, 10, "Churn Riski", border=1)
        self.ln()
        self.set_font("Arial", "", 11)
        for row in tablo:
            self.cell(60, 10, temizle(row["Ad Soyad"]), border=1)
            self.cell(40, 10, temizle(row["Son Servis"]), border=1)
            self.cell(40, 10, row["Churn Riski"], border=1)
            self.ln()
    def segment_table(self, df):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Musteri Segment Ozeti", ln=True)
        self.set_font("Arial", "B", 11)
        self.cell(20, 10, "Seg", border=1)
        self.cell(30, 10, "Kayit", border=1)
        self.cell(40, 10, "Gun Farki", border=1)
        self.cell(40, 10, "Upsell", border=1)
        self.cell(40, 10, "Tekrar", border=1)
        self.ln()

        self.set_font("Arial", "", 11)
        for _, row in df.iterrows():
            self.cell(20, 10, str(row["segment"]), border=1)
            self.cell(30, 10, str(int(row["count"])), border=1)
            self.cell(40, 10, str(row["gun_farki"]), border=1)
            self.cell(40, 10, f"%{row['upsell']*100:.0f}", border=1)
            self.cell(40, 10, f"%{row['tekrar']*100:.0f}", border=1)
            self.ln()

def temizle(text):
    return (text.replace("ı", "i")
                .replace("İ", "I")
                .replace("ş", "s")
                .replace("Ş", "S")
                .replace("ğ", "g")
                .replace("Ğ", "G")
                .replace("ü", "u")
                .replace("Ü", "U")
                .replace("ö", "o")
                .replace("Ö", "O")
                .replace("ç", "c")
                .replace("Ç", "C")
                .replace("≥", ">=")
                .replace("•", "-"))

def plot_churn(df):
    today = datetime.today()
    churned = []
    active = []

    for _, row in df.iterrows():
        try:
            last_visit = row["Tarih"]
            if pd.isna(last_visit): continue
            fark = relativedelta(today, last_visit)
            if fark.years > 0 or fark.months >= 6:
                churned.append(row)
            else:
                active.append(row)
        except:
            continue

    total = len(churned) + len(active)
    if total == 0:
        print("Uyarı: Churn analizi için geçerli veri bulunamadı.")
        return

    labels = ['Aktif Musteri', 'Kaybedilen Musteri']
    values = [len(active), len(churned)]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=["#4CAF50", "#FF5733"])
    plt.title("Churn (Musteri Kaybi) Analizi")
    plt.tight_layout()
    plt.savefig("churn.png")
    plt.close()

def plot_upsell(df):
    if "Upsell" not in df.columns:
        print("Uyarı: 'Upsell' sütunu bulunamadı.")
        return

    counts = df["Upsell"].value_counts()

    plt.figure(figsize=(6, 4))
    sns.barplot(x=counts.index, y=counts.values, palette="plasma")
    plt.title("Upsell Dagilimi")
    plt.xlabel("Upsell Yapildi mi?")
    plt.ylabel("Kayit Sayisi")
    plt.tight_layout()
    plt.savefig("upsell.png")
    plt.close()

def churn_risk_hesapla(df):
    try:
        model = joblib.load("churn_model.pkl")
    except:
        print("churn_model.pkl bulunamadı.")
        return []

    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["Tarih"])

    df["gun_farki"] = (datetime.today() - df["Tarih"]).dt.days
    df["upsell"] = df["Upsell"].fillna("Hayır").apply(lambda x: 1 if str(x).lower() == "evet" else 0)
    df["tekrar"] = df["Tekrar Geliş"].fillna("Hayır").apply(lambda x: 1 if str(x).lower() == "evet" else 0)

    X_pred = df[["upsell", "tekrar", "gun_farki"]]
    churn_risk = model.predict_proba(X_pred)[:,1]

    df["churn_risk"] = churn_risk
    en_riskli = df.sort_values("churn_risk", ascending=False).head(10)

    tablo = []
    for _, row in en_riskli.iterrows():
        tablo.append({
            "Ad Soyad": row["Ad Soyad"],
            "Son Servis": row["Tarih"].strftime("%d.%m.%Y"),
            "Churn Riski": f"%{row['churn_risk']*100:.1f}"
        })
    return tablo

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y", errors='coerce')

    plot_churn(df)
    plot_upsell(df)

    pdf = PDF()
    pdf.add_page()

    # Segment analizi
    segment_ozet_df, segment_yorumlar = get_segment_ozet_ve_yorum()
    yorum_metni = "\n".join(segment_yorumlar)
    pdf.segment_table(segment_ozet_df)

    # Temel sayısal özet + upsell + segment yorumları
    pdf.body_text(temizle(
        f"Toplam Kayit: {len(df)}\n"
        f"Upsell Yapilan Musteri Sayisi: {(df['Upsell'] == 'Evet').sum()}\n"
        f"Tekrar Gelen Musteri Sayisi: {(df['Tekrar Geliş'] == 'Evet').sum()}\n"
        f"Analiz gorselleri asagidadir:\n\n"
        f"Upsell Etki Yorumu:\n"
        f"{get_upsell_effect_comment()}\n\n"
        f"Musteri Segmenti Yorumlari:\n"
        f"{yorum_metni}"
    ))

    # Churn ve upsell grafikleri
    if os.path.exists("churn.png"):
        pdf.insert_image("churn.png", "Churn Analizi")

    if os.path.exists("upsell.png"):
        pdf.insert_image("upsell.png", "Upsell Analizi")

    # En riskli 10 müşteri tablosu
    risk_tablosu = churn_risk_hesapla(df)
    if risk_tablosu:
        pdf.churn_tablosu(risk_tablosu)

    # Servis tahmini grafiği ve yorum
    gercek_df, tahmin_df = tahmin_uret(df)
    grafik_ciz(gercek_df, tahmin_df)

    if os.path.exists("servis_tahmini.png"):
        pdf.insert_image("servis_tahmini.png", "Servis Talep Tahmini")
        yorum = yorumla_tahmin(tahmin_df)
        pdf.body_text(temizle(yorum))

    pdf.output("roi_raporu.pdf")
    print("ROI raporu başarıyla oluşturuldu: roi_raporu.pdf")

