# Dicoding Collection Dashboard ✨

Proyek Analisis Data **Bike Sharing Dataset** (Capital Bikeshare, Washington D.C., 2011-2012).
Dashboard menjawab dua pertanyaan bisnis: jam puncak penyewaan (hari kerja vs akhir pekan/libur) serta pengaruh musim dan cuaca terhadap penyewaan harian.

## Struktur Direktori
```
submission
├───dashboard
| ├───main_data.csv      (data per jam yang sudah dibersihkan)
| ├───day_data.csv       (data harian yang sudah dibersihkan)
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard/dashboard.py
```
