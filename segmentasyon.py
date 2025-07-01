import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def segment_musteriler(df, n_clusters=3):
    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["Tarih"])
    df["gun_farki"] = (pd.Timestamp.today() - df["Tarih"]).dt.days

    df["upsell"] = df["Upsell"].fillna("Hayır").apply(lambda x: 1 if str(x).lower() == "evet" else 0)
    df["tekrar"] = df["Tekrar Geliş"].fillna("Hayır").apply(lambda x: 1 if str(x).lower() == "evet" else 0)
    df["servis_sayisi"] = df.groupby("Ad Soyad")["Ad Soyad"].transform("count")

    features = df[["upsell", "tekrar", "gun_farki", "servis_sayisi"]]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    model = KMeans(n_clusters=n_clusters, random_state=42)
    df["segment"] = model.fit_predict(scaled)

    return df

def yorumla_segmentler(ortalama_df):
    yorumlar = []
    for seg, satir in ortalama_df.iterrows():
        fark = satir["gun_farki"]
        upsell = satir["upsell"]
        tekrar = satir["tekrar"]
        yorum = f"• Segment {seg}: "

        if upsell > 0.8:
            yorum += "Upsell oranı çok yüksek. "
        elif upsell < 0.2:
            yorum += "Upsell fırsatı kullanılmamış. "

        if fark > 120:
            yorum += "Uzun süredir servis alınmamış. "
        elif fark < 60:
            yorum += "Yakın zamanda servis alınmış. "

        if tekrar > 0.5:
            yorum += "Sadakat potansiyeli yüksek."
        elif tekrar < 0.3:
            yorum += "Müşteri elde tutma riski olabilir."

        yorumlar.append(yorum)
    return yorumlar

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    df_segmentli = segment_musteriler(df)

    print("\nSegment Dağılımı:")
    print(df_segmentli["segment"].value_counts())

    ortalama_df = df_segmentli.groupby("segment")[["gun_farki", "upsell", "tekrar"]].mean()
    print("\nSegmentlere Göre Ortalama Değerler:")
    print(ortalama_df.round(2))

    yorumlar = yorumla_segmentler(ortalama_df)
    print("\nSegment Yorumları:\n")
    for y in yorumlar:
        print(y)
def get_segment_yorumlari():
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    df_segmentli = segment_musteriler(df)
    ortalama_df = df_segmentli.groupby("segment")[["gun_farki", "upsell", "tekrar"]].mean()
    yorumlar = yorumla_segmentler(ortalama_df)

    return yorumlar

def get_segment_ozet_ve_yorum():
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    df_seg = segment_musteriler(df)
    ozet = df_seg.groupby("segment")[["gun_farki", "upsell", "tekrar"]].mean().round(1)
    ozet["count"] = df_seg["segment"].value_counts()
    ozet = ozet[["count", "gun_farki", "upsell", "tekrar"]].reset_index()
    yorumlar = yorumla_segmentler(ozet)
    return ozet, yorumlar
