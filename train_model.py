import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import tensorflow as tf
import joblib
import unicodedata
import re

def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def connect_to_google_sheet(sheet_name="service reservation"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return pd.DataFrame(sheet.get_all_records())

def preprocess_train(df):
    df = df[df["Son Servis"].notna()]
    df["Ad Soyad"] = df["Ad Soyad"].apply(normalize_text)
    df["Geri Bildirim Puanı"] = pd.to_numeric(df["Geri Bildirim Puanı"], errors="coerce").fillna(0)
    df["interaction"] = df["Tekrar Geliş"].apply(lambda x: 1 if x == "Evet" else 0) + (df["Geri Bildirim Puanı"] / 5)

    user_enc = LabelEncoder()
    item_enc = LabelEncoder()
    df["user_id"] = user_enc.fit_transform(df["Ad Soyad"])
    df["item_id"] = item_enc.fit_transform(df["Son Servis"])

    return df[["user_id", "item_id", "interaction"]], user_enc, item_enc

def build_model(n_users, n_items, embedding_dim=32):
    user_input = tf.keras.Input(shape=(1,))
    item_input = tf.keras.Input(shape=(1,))

    user_embedding = tf.keras.layers.Embedding(n_users, embedding_dim)(user_input)
    item_embedding = tf.keras.layers.Embedding(n_items, embedding_dim)(item_input)

    user_vec = tf.keras.layers.Flatten()(user_embedding)
    item_vec = tf.keras.layers.Flatten()(item_embedding)

    x = tf.keras.layers.Concatenate()([user_vec, item_vec])
    x = tf.keras.layers.Dense(64, activation='relu')(x)
    x = tf.keras.layers.Dense(32, activation='relu')(x)
    output = tf.keras.layers.Dense(1, activation='sigmoid')(x)

    model = tf.keras.Model(inputs=[user_input, item_input], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['AUC'])
    return model

def train_and_save():
    df = connect_to_google_sheet()
    data, user_enc, item_enc = preprocess_train(df)

    n_users = data["user_id"].nunique()
    n_items = data["item_id"].nunique()

    model = build_model(n_users, n_items)

    model.fit(
        [data["user_id"], data["item_id"]],
        data["interaction"],
        batch_size=64,
        epochs=10,
        validation_split=0.2
    )

    model.save("ncf_model.h5")
    joblib.dump(user_enc, "user_encoder.pkl")
    joblib.dump(item_enc, "item_encoder.pkl")
    print("Model ve encoder'lar kaydedildi.")

if __name__ == "__main__":
    train_and_save()
