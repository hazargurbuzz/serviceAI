import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from fpdf import FPDF
from datetime import datetime
import unicodedata
import re
from thefuzz import process
import os
from train_model import normalize_text, connect_to_google_sheet

def find_closest_user(input_name, user_list, threshold=70):
    match, score = process.extractOne(input_name, user_list)
    if score >= threshold:
        return match
    else:
        return None

def recommend_for_user(user_name, topn=5):
    user_name = normalize_text(user_name)
    df = connect_to_google_sheet()
    df["Ad Soyad"] = df["Ad Soyad"].apply(normalize_text)
    user_list = df["Ad Soyad"].unique()

    closest_user = find_closest_user(user_name, user_list)
    if closest_user is None:
        print(f"⚠️ Kullanıcı bulunamadı: {user_name}")
        return []

    user_enc = joblib.load("user_encoder.pkl")
    item_enc = joblib.load("item_encoder.pkl")
    model = tf.keras.models.load_model("ncf_model.h5")

    try:
        user_id = user_enc.transform([closest_user])[0]
    except ValueError:
        print(f"⚠️ Kullanıcı encoder'da bulunamadı: {closest_user}")
        return []

    all_items = np.arange(len(item_enc.classes_))

    scores = model.predict([np.full_like(all_items, user_id), all_items]).flatten()
    top_items = all_items[np.argsort(scores)[-topn:][::-1]]

    return item_enc.inverse_transform(top_items)

def turkish_char_replace(text):
    replacements = {
        'ş': 's', 'Ş': 'S',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C',
        'ı': 'i', 'İ': 'I'
    }
    for tr_char, en_char in replacements.items():
        text = text.replace(tr_char, en_char)
    return text

def generate_user_recommendation_pdf(name, topn=3):
    öneriler = recommend_for_user(name, topn=topn)

    if öneriler is None or len(öneriler) == 0:
        print("Öneri bulunamadı.")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, turkish_char_replace("Kişisel Hizmet Öneri Raporu"), ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, turkish_char_replace(f"Müşteri: {name}"), ln=True)
    pdf.cell(0, 10, turkish_char_replace(f"Tarih: {datetime.today().strftime('%d.%m.%Y')}"), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, turkish_char_replace("Önerilen Hizmetler:"), ln=True)
    pdf.set_font("Arial", "", 12)
    for i, hizmet in enumerate(öneriler, 1):
        pdf.cell(0, 10, turkish_char_replace(f"- {hizmet}"), ln=True)

    dosya_adi = f"{name.replace(' ', '_')}_oneriler.pdf"
    pdf.output(dosya_adi)
    print(f"PDF kaydedildi: {dosya_adi}")

if __name__ == "__main__":
    ad = input("Lütfen müşteri adını girin: ").strip()
    ad = normalize_text(ad)
    generate_user_recommendation_pdf(ad)
