import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import pandas as pd
import streamlit as st

# ⚠️ Podmień na swój identyfikator profilu (user=XXX)
SCHOLAR_URL = "https://scholar.google.com/citations?user=aI0gZBEAAAAJ&hl=en&cstart=0&pagesize=100"
CSV_FILE = "citations_history.csv"

headers = {"User-Agent": "Mozilla/5.0"}

# ======================
# Funkcje
# ======================
def get_publications():
    response = requests.get(SCHOLAR_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select(".gsc_a_tr")

    publications = {}
    for row in rows:
        title = row.select_one(".gsc_a_at").text
        citations_tag = row.select_one(".gsc_a_c a")
        citations = int(citations_tag.text) if citations_tag and citations_tag.text.isdigit() else 0
        publications[title] = citations
    return publications

def save_to_csv(publications):
    file_exists = os.path.isfile(CSV_FILE)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            header = ["timestamp"] + list(publications.keys())
            writer.writerow(header)

        row = [timestamp] + list(publications.values())
        writer.writerow(row)

def load_history():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return None

# ======================
# Aplikacja Streamlit
# ======================
st.title("📈 Google Scholar Citation Tracker")


# Pobieranie danych (ręczne + przy starcie strony)
if st.button("🔍 Pobierz aktualne dane"):
    publications = get_publications()
    save_to_csv(publications)
    st.success("Dane pobrane i zapisane w historii!")

# Przy każdym odświeżeniu spróbuj pobrać dane raz na dobę
if not os.path.exists(CSV_FILE):
    st.info("Brak danych. Kliknij przycisk powyżej, aby pobrać pierwsze dane.")
else:
    history = load_history()
    if history is not None:
        st.subheader("📊 Historia cytowań")
        st.dataframe(history)

        # sumaryczny wykres cytowań
        st.subheader("📈 Wzrost łącznych cytowań w czasie")
        history["total_citations"] = history.drop("timestamp", axis=1).sum(axis=1)
        st.line_chart(history.set_index("timestamp")["total_citations"])

        # wybór publikacji do podglądu
        pub_choice = st.selectbox("Wybierz publikację do analizy", history.columns[1:-1])
        st.line_chart(history.set_index("timestamp")[pub_choice])
