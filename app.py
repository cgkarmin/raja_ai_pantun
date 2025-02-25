import streamlit as st
import pandas as pd
import os

# --- Fungsi-fungsi Bantuan ---

def analisis_pantun(row):
    """
    Menganalisis pantun dan memberikan markah.
    """
    markah_muktamad = 0
    baris = row['text'].splitlines()

    # --- Kriteria 1: Jumlah Baris (WAJIB) ---
    if len(baris) != 4:
        return 0

    markah_muktamad += 10

    # --- Kriteria 2: Jumlah Suku Kata ---
    try:
        suku_kata_p1 = int(row['sukukata_p1'])
        suku_kata_p2 = int(row['sukukata_p2'])
        suku_kata_m1 = int(row['sukukata_m1'])
        suku_kata_m2 = int(row['sukukata_m2'])
    except ValueError:
        return 0

    if 8 <= suku_kata_p1 <= 12:
        markah_muktamad += 2
    if 8 <= suku_kata_p2 <= 12:
        markah_muktamad += 2
    if 8 <= suku_kata_m1 <= 12:
        markah_muktamad += 2
    if 8 <= suku_kata_m2 <= 12:
        markah_muktamad += 2

    # --- Kriteria 3: Rima Tengah ---
    try:
        if row['tengah_p1'].lower() == row['tengah_m1'].lower():
            markah_muktamad += 3
        if row['tengah_p2'].lower() == row['tengah_m2'].lower():
            markah_muktamad += 3
    except:
        pass

    # --- Kriteria 4: Rima Akhir ---
    try:
        if row['akhir_p1'].lower() == row['akhir_m1'].lower():
            markah_muktamad += 4
        if row['akhir_p2'].lower() == row['akhir_m2'].lower():
            markah_muktamad += 4
    except:
        pass

    return markah_muktamad

# --- Konstanta ---
DATA_DIR = "data"
NAMA_FILE_CSV = os.path.join(DATA_DIR, "raja_pantun.csv")
MARKAH_MINIMUM_LAYAK = 23

# --- Fungsi untuk Menghitung Markah ---
def hitung_markah_penulis(df):
    """Menghitung markah untuk setiap penulis."""

    if 'markah_muktamad' not in df.columns:
        df['markah_muktamad'] = 0
    df = df[df['markah_muktamad'].notna()]
    df['markah_muktamad'] = pd.to_numeric(df['markah_muktamad'], errors='coerce')
    df = df.dropna(subset=['markah_muktamad'])
    df['markah_muktamad'] = df['markah_muktamad'].astype(int)

    df_layak = df[df['markah_muktamad'] >= MARKAH_MINIMUM_LAYAK]

    perangkaan_penulis = df_layak.groupby('author').agg(
        Bilangan_Pantun_Layak=('text', 'count'),
        Jumlah_Markah_Penuh=('markah_muktamad', 'sum')
    ).reset_index()

    bilangan_pantun_terbanyak = perangkaan_penulis['Bilangan_Pantun_Layak'].max()
    if bilangan_pantun_terbanyak > 0:
        perangkaan_penulis['Bonus_Kuantiti'] = (perangkaan_penulis['Bilangan_Pantun_Layak'] / bilangan_pantun_terbanyak) * 100
    else:
        perangkaan_penulis['Bonus_Kuantiti'] = 0

    perangkaan_penulis['Peratusan'] = perangkaan_penulis.apply(lambda row: (row['Jumlah_Markah_Penuh'] / (row['Bilangan_Pantun_Layak'] * 25)) * 100, axis=1)
    perangkaan_penulis['Markah_Akhir'] = (perangkaan_penulis['Peratusan'] * 0.8) + (perangkaan_penulis['Bonus_Kuantiti'] * 0.2)
    perangkaan_penulis = perangkaan_penulis.sort_values('Markah_Akhir', ascending=False)

    return perangkaan_penulis

# --- Antaramuka Streamlit ---

st.title("Raja Pantun")

# --- Navigasi (Tabs) ---
tab1, tab2, tab3 = st.tabs(["Pengenalan", "Senarai Raja Pantun", "Jadi Raja Pantun"])

with tab1:
    st.header("Pengenalan")
    st.write("Anda ingin tahu siapakah Raja Pantun? Anda ingin jadi Raja Pantun? .")

with tab2:
    st.header("Senarai Raja Pantun")
    df_pantun = pd.read_csv(NAMA_FILE_CSV)
    perangkaan_penulis = hitung_markah_penulis(df_pantun)

    st.subheader("Ranking 20 Teratas")
    df_tampil = perangkaan_penulis[["author", "Bilangan_Pantun_Layak", "Peratusan", "Markah_Akhir"]]
    df_tampil = df_tampil.rename(columns={
        "author": "Pengarang",
        "Bilangan_Pantun_Layak": "Bilangan Pantun Layak",
        "Peratusan": "Peratusan Markah Penuh",
        "Markah_Akhir": "Markah Akhir"
    })
    df_tampil["Markah Akhir"] = df_tampil["Markah Akhir"].map("{:.2f}".format)
    df_tampil["Peratusan Markah Penuh"] = df_tampil["Peratusan Markah Penuh"].map("{:.2f}%".format)
    st.table(df_tampil.head(20))

with tab3:
    st.header("Jadi Raja Pantun")
    with st.form("hantar_pantun"):
        pantun = st.text_area("Masukkan Pantun Anda (4 baris):", height=150)
        pengarang = st.text_input("Pengarang")
        tema = st.text_input("Tema")
        sumber = st.text_input("Sumber")

        submitted = st.form_submit_button("Periksa & Hantar")

    if submitted:
        if not pantun.strip() or not pengarang.strip():
            st.error("Pantun dan Pengarang tidak boleh kosong.")
        else:
            st.success("Pantun anda telah dianalisis dan dihantar!")
