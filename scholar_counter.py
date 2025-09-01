import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

headers = {"User-Agent": "Mozilla/5.0"}

def get_publications(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Błąd pobierania strony. Sprawdź adres profilu Google Scholar.")

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select(".gsc_a_tr")

    data = []
    for row in rows:
        title = row.select_one(".gsc_a_at").text
        citations_tag = row.select_one(".gsc_a_c a")
        citations = int(citations_tag.text) if citations_tag and citations_tag.text.isdigit() else 0
        year_tag = row.select_one(".gsc_a_y span")
        year = year_tag.text if year_tag else ""
        data.append([title, citations, year])

    return pd.DataFrame(data, columns=["Tytuł", "Cytowania", "Rok"])

def main():
    # okienko do wklejenia linku
    root = tk.Tk()
    root.withdraw()
    url = tk.simpledialog.askstring("Google Scholar", "Wklej adres swojego profilu Google Scholar:")
    if not url:
        return

    try:
        df = get_publications(url)
    except Exception as e:
        messagebox.showerror("Błąd", str(e))
        return

    # wybór miejsca zapisu
    filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if filepath:
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Sukces", f"Plik zapisany jako:\n{filepath}")

if __name__ == "__main__":
    main()
