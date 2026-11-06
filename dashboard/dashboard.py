from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="white")
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold"})
BLUE, LIGHT, ORANGE, GREY = "#1f5aa6", "#a9bfdc", "#e08a1e", "#b5b5b5"

BASE = Path(__file__).parent
SEASONS = ["Winter", "Spring", "Summer", "Fall"]
WEATHERS = ["Cerah/Berawan Sebagian", "Berkabut/Mendung", "Hujan/Salju Ringan", "Hujan Lebat/Salju"]
Q1 = "Pada jam berapa puncak penyewaan sepeda terjadi pada hari kerja dibandingkan akhir pekan/hari libur selama periode 2011–2012, dan berapa rata-rata penyewaan per jam pada jam puncak tersebut, sehingga operator dapat menentukan jadwal redistribusi sepeda dan jendela perawatan armada?"
Q2 = "Seberapa besar perbedaan rata-rata penyewaan harian antar musim dan antar kondisi cuaca (cerah, berkabut/mendung, hujan/salju ringan) selama periode 2011–2012, dan berapa persen penurunan permintaan pada kondisi cuaca terburuk dibandingkan cuaca cerah, sehingga tim bisnis dapat menyusun strategi promosi dan penyesuaian armada musiman?"
WEEKDAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


@st.cache_data
def load_data():
    hour = pd.read_csv(BASE / "main_data.csv", parse_dates=["dteday"])
    day = pd.read_csv(BASE / "day_data.csv", parse_dates=["dteday"])
    return day, hour


day_all, hour_all = load_data()

with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.caption("Capital Bikeshare, Washington D.C. (2011-2012)")
    min_d, max_d = day_all["dteday"].min().date(), day_all["dteday"].max().date()
    date_range = st.date_input("Rentang tanggal", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    seasons = st.multiselect("Musim", SEASONS, default=SEASONS)
    weathers = st.multiselect("Kondisi cuaca", WEATHERS, default=WEATHERS)
    st.markdown("---")
    st.caption("Filter berlaku untuk seluruh visualisasi. Data: day.csv & hour.csv yang sudah dibersihkan.")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = pd.Timestamp(min_d), pd.Timestamp(max_d)


def apply_filter(df):
    return df[df["dteday"].between(start, end) & df["season_name"].isin(seasons) & df["weather_label"].isin(weathers)]


day, hour = apply_filter(day_all), apply_filter(hour_all)

st.title("Dashboard Analisis Bike Sharing 🚲")
st.write("Menjawab dua pertanyaan bisnis: **(1)** jam puncak penyewaan hari kerja vs akhir pekan/libur, dan "
         "**(2)** pengaruh musim dan cuaca terhadap penyewaan harian.")

if day.empty or hour.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Ubah filter pada sidebar.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total penyewaan", f"{day['cnt'].sum():,.0f}")
c2.metric("Rata-rata per hari", f"{day['cnt'].mean():,.0f}")
c3.metric("Pengguna terdaftar", f"{day['registered'].sum() / day['cnt'].sum():.1%}")
c4.metric("Jumlah hari dianalisis", f"{len(day):,}")

tab1, tab2, tab3 = st.tabs(["⏰ Pola Jam (Pertanyaan 1)", "🌦️ Musim & Cuaca (Pertanyaan 2)", "🧩 Analisis Lanjutan"])

with tab1:
    st.subheader("Pertanyaan 1")
    st.write(Q1)
    hourly = hour.groupby(["hr", "day_type"])["cnt"].mean().reset_index()
    palette = {"Hari Kerja": BLUE, "Akhir Pekan/Libur": ORANGE}

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=hourly, x="hr", y="cnt", hue="day_type", palette=palette, linewidth=2.5, marker="o", ax=ax)
    for tipe, color in palette.items():
        sub = hourly[hourly["day_type"] == tipe]
        if sub.empty:
            continue
        peak = sub.loc[sub["cnt"].idxmax()]
        ax.annotate(f"Puncak {tipe}: {int(peak['hr']):02d}.00 ({peak['cnt']:.0f})", xy=(peak["hr"], peak["cnt"]),
                    xytext=(peak["hr"] + 0.8, peak["cnt"] + 60), color=color, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=color))
    ax.set_ylim(0, max(hourly["cnt"].max() * 1.25, 100))
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}" for h in range(24)])
    ax.set_xlabel("Jam dalam sehari")
    ax.set_ylabel("Rata-rata penyewaan per jam (sepeda)")
    ax.legend(title=None, frameon=False, loc="upper left")
    st.pyplot(fig)

    pivot = hourly.pivot(index="hr", columns="day_type", values="cnt")
    cols = st.columns(len(pivot.columns))
    for col, tipe in zip(cols, pivot.columns):
        col.metric(f"Jam puncak {tipe}", f"{int(pivot[tipe].idxmax()):02d}.00", f"{pivot[tipe].max():.0f} sepeda/jam", delta_color="off")
    st.info("**Insight:** hari kerja punya dua puncak komuter (08.00 dan 17.00), sedangkan akhir pekan/libur punya satu "
            "puncak siang (13.00). Dini hari (00.00-05.00) paling sepi, cocok untuk perawatan armada. "
            "(Insight di atas berdasarkan seluruh data; metrik berubah mengikuti filter.)")

with tab2:
    st.subheader("Pertanyaan 2")
    st.write(Q2)
    season_avg = day.groupby("season_name")["cnt"].mean().reindex(SEASONS).dropna()
    weather_avg = day.groupby("weather_label")["cnt"].mean().reindex(WEATHERS).dropna()
    weather_n = day["weather_label"].value_counts().reindex(weather_avg.index)

    left, right = st.columns(2)
    with left:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        colors = [BLUE if v == season_avg.max() else LIGHT for v in season_avg]
        bars = ax.bar(season_avg.index, season_avg.values, color=colors, width=0.62)
        for b, v in zip(bars, season_avg.values):
            ax.text(b.get_x() + b.get_width() / 2, v + season_avg.max() * 0.015, f"{v:,.0f}", ha="center", fontweight="bold")
        ax.set_ylim(0, season_avg.max() * 1.15)
        ax.set_ylabel("Rata-rata penyewaan harian")
        ax.set_title("Per musim", loc="left")
        st.pyplot(fig)
    with right:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        base = weather_avg.iloc[0]
        colors = [BLUE] + [LIGHT] * (len(weather_avg) - 1)
        labels = [w.replace("/", "/\n") for w in weather_avg.index]
        bars = ax.bar(labels, weather_avg.values, color=colors, width=0.6)
        for b, v, n in zip(bars, weather_avg.values, weather_n.values):
            pct = "" if v == base else f" ({v / base - 1:+.0%})"
            ax.text(b.get_x() + b.get_width() / 2, v + weather_avg.max() * 0.015, f"{v:,.0f}{pct}\nn={n} hari",
                    ha="center", fontweight="bold", fontsize=9)
        ax.set_ylim(0, weather_avg.max() * 1.25)
        ax.set_ylabel("Rata-rata penyewaan harian")
        ax.set_title("Per kondisi cuaca (persen vs kategori pertama)", loc="left", fontsize=11)
        ax.tick_params(axis="x", labelsize=8)
        st.pyplot(fig)
    st.info("**Insight:** Summer paling tinggi dan Winter paling rendah (sekitar 54% lebih rendah). "
            "Cuaca berkabut/mendung menurunkan permintaan sekitar 17%, hujan/salju ringan sekitar 63% dibanding cuaca cerah "
            "(sampel hujan/salju hanya 21 hari pada keseluruhan data).")

with tab3:
    st.subheader("Binning suhu, klaster jam, dan heatmap")
    day = day.copy()
    day["temp_group"] = pd.cut(day["temp_c"], [-np.inf, 10, 20, 30, np.inf],
                               labels=["Dingin (<10°C)", "Sejuk (10-20°C)", "Hangat (20-30°C)", "Panas (>30°C)"])
    temp_summary = day.groupby("temp_group", observed=True).agg(n=("cnt", "size"), avg=("cnt", "mean"))

    left, right = st.columns(2)
    with left:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        colors = [BLUE if v == temp_summary["avg"].max() else LIGHT for v in temp_summary["avg"]]
        bars = ax.bar(temp_summary.index.astype(str), temp_summary["avg"], color=colors, width=0.6)
        for b, v, n in zip(bars, temp_summary["avg"], temp_summary["n"]):
            ax.text(b.get_x() + b.get_width() / 2, v + temp_summary["avg"].max() * 0.015, f"{v:,.0f}\n(n={n})",
                    ha="center", fontsize=9, fontweight="bold")
        ax.set_ylim(0, temp_summary["avg"].max() * 1.25)
        ax.set_ylabel("Rata-rata penyewaan harian")
        ax.set_title("Binning suhu udara", loc="left")
        ax.tick_params(axis="x", labelsize=8)
        st.pyplot(fig)
    with right:
        profile = hour.groupby("hr")["cnt"].mean().round(1).to_frame("rata2")
        profile["klaster"] = pd.cut(profile["rata2"], [0, 100, 300, np.inf],
                                    labels=["Rendah (<100)", "Sedang (100-300)", "Tinggi (>300)"])
        summary = profile.reset_index().groupby("klaster", observed=True).agg(
            jam=("hr", lambda s: ", ".join(f"{h:02d}" for h in s)), rata2_penyewaan=("rata2", "mean")).round(0)
        st.markdown("**Klaster jam berdasarkan rata-rata penyewaan per jam**")
        st.dataframe(summary)

    heat = hour.pivot_table(index="weekday_name", columns="hr", values="cnt", aggfunc="mean").reindex(WEEKDAYS)
    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(heat, cmap="Blues", linewidths=0.4, linecolor="white", cbar_kws={"label": "Rata-rata penyewaan/jam"}, ax=ax)
    ax.set_xlabel("Jam dalam sehari")
    ax.set_ylabel("")
    ax.set_title("Heatmap rata-rata penyewaan: hari x jam", loc="left")
    st.pyplot(fig)

st.caption("Sumber data: Fanaee-T & Gama (2013), Capital Bikeshare 2011-2012. Dashboard proyek analisis data Dicoding.")
