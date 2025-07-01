import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def tahmin_uret(df):
    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["Tarih"])

    df["gun"] = df["Tarih"].dt.date
    gunluk_sayim = df.groupby("gun").size().reset_index(name="servis_sayisi")
    gunluk_sayim = gunluk_sayim.set_index("gun")

    # 7 günlük hareketli ortalama
    gunluk_sayim["7_gun_ort"] = gunluk_sayim["servis_sayisi"].rolling(window=7, min_periods=1).mean()

    # Basit ileriye kopyalama tahmini (son 7 gün ortalaması)
    tahmin_baslangic = gunluk_sayim.index.max() + timedelta(days=1)
    tahminler = []
    for i in range(7):
        tarih = tahmin_baslangic + timedelta(days=i)
        tahmin_deger = gunluk_sayim["7_gun_ort"].iloc[-7:].mean()
        tahminler.append({"gun": tarih, "tahmin": tahmin_deger})

    tahmin_df = pd.DataFrame(tahminler).set_index("gun")

    return gunluk_sayim, tahmin_df

def grafik_ciz(gercek_df, tahmin_df, path="servis_tahmini.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(gercek_df.index, gercek_df["servis_sayisi"], label="Gerçek Servis Sayısı")
    plt.plot(gercek_df.index, gercek_df["7_gun_ort"], label="7 Günlük Ortalama", linestyle="--")
    plt.plot(tahmin_df.index, tahmin_df["tahmin"], label="Tahmin (İleriye)", linestyle="--", color="orange")

    plt.title("Servis Talep Tahmini")
    plt.xlabel("Tarih")
    plt.ylabel("Servis Sayısı")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"Grafik kaydedildi: {path}")
def yorumla_tahmin(tahmin_df):
    ort = tahmin_df["tahmin"].mean()
    maks_tarih = tahmin_df["tahmin"].idxmax()
    maks_deger = tahmin_df["tahmin"].max()

    yorum = (
        f"Tahmin Yorumu:\n"
        f"Önümüzdeki 7 gün için ortalama günlük servis sayısı **{ort:.1f}** olarak tahmin edilmektedir.\n"
        f"En yüksek talep {maks_tarih.strftime('%d %B %Y')} tarihinde (**{maks_deger:.1f}** servis) beklenmektedir.\n"
    )

    if ort > 8:
        yorum += "Yüksek yoğunluk uyarısı: Personel planlaması gözden geçirilmeli.\n"
    elif ort < 3:
        yorum += "Düşük yoğunluk bekleniyor: Kampanya yapılabilir.\n"
    else:
        yorum += "Yoğunluk normal düzeyde. Standart planlama yeterlidir.\n"

    return yorum

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    gercek_df, tahmin_df = tahmin_uret(df)
    grafik_ciz(gercek_df, tahmin_df)
