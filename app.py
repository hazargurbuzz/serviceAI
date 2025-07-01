from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

def connect_to_google_sheet(sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

@app.route("/")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    date = request.form["date"]
    time = request.form["time"]

    sheet = connect_to_google_sheet("service reservation")
    sheet.append_row([name, date, time])

    return redirect("/liste")  

@app.route("/liste")
def liste():
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    return render_template("liste.html", veriler=records)

if __name__ == "__main__":
    app.run(debug=True)
