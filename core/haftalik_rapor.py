import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from fpdf import FPDF
import os
import matplotlib.pyplot as plt
from collections import Counter

# Türkçe karakterleri düzleştir
def temizle(text):
    return (text.replace("ı", "i")
                .replace("ş", "s")
                .replace("ğ", "g")
                .replace("ü", "u")
                .replace("ö", "o")
                .replace("ç", "c")
                .replace("İ", "I")
                .replace("Ş", "S")
                .replace("Ğ", "G")
                .replace("Ü", "U")
                .replace("Ö", "O")
                .replace("Ç", "C"))

# Google Sheet bağlantısı
def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, temizle("Haftalik Servis Raporu"), ln=True, align="C")

    def body_text(self, text):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, temizle(text))

    def table(self, data):
        self.set_font("Arial", "B", 12)
        self.ln(10)
        self.cell(60, 10, temizle("Ad Soyad"), border=1)
        self.cell(40, 10, temizle("Tarih"), border=1)
        self.cell(30, 10, temizle("Saat"), border=1)
        self.ln()
        self.set_font("Arial", "", 12)
        for row in data:
            self.cell(60, 10, temizle(row["Ad Soyad"]), border=1)
            self.cell(40, 10, temizle(row["Tarih"]), border=1)
            self.cell(30, 10, temizle(row["Saat"]), border=1)
            self.ln()

    def insert_image(self, image_path):
        self.image(image_path, x=30, w=150)
        self.ln(10)

def generate_chart(dates, output_path):
    counts = Counter(dates)
    days = sorted(counts.keys())
    values = [counts[day] for day in days]

    plt.figure(figsize=(8, 4))
    plt.bar(days, values, color='skyblue')
    plt.title("Gunluk Servis Sayisi")
    plt.xlabel("Tarih")
    plt.ylabel("Servis Sayisi")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    rows = sheet.get_all_records()
    bugun = datetime.today()
    yedi_gun_once = bugun - timedelta(days=7)

    filtreli = []
    for row in rows:
        try:
            tarih = datetime.strptime(row["Tarih"], "%d.%m.%Y")
            if yedi_gun_once <= tarih <= bugun:
                row["ParsedDate"] = tarih
                filtreli.append(row)
        except Exception:
            continue

    total = len(filtreli)
    if total > 0:
        dates = [r["ParsedDate"].strftime("%d.%m") for r in filtreli]
        en_yogun_gun = Counter(dates).most_common(1)[0][0]
        ortalama_saat = sum([int(r["Saat"].split(":")[0]) for r in filtreli]) / total
    else:
        dates = []
        en_yogun_gun = "-"
        ortalama_saat = 0

    chart_path = "chart.png"
    generate_chart(dates, chart_path)

    pdf = PDF()
    pdf.add_page()
    pdf.body_text(
        f" Istatistiksel Ozet:\n\n"
        f"- Toplam servis sayisi: {total}\n"
        f"- En yogun gun: {en_yogun_gun}\n"
        f"- Ortalama servis saati: {ortalama_saat:.1f}\n"
    )
    pdf.insert_image(chart_path)
    pdf.table(filtreli)

    pdf.output("haftalik_servis_raporu.pdf")
    print("PDF basariyla olusturuldu: haftalik_servis_raporu.pdf")
