import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

# Mengimpor data yang telah disiapkan
all_data_df = pd.read_csv("all_data.csv")

# Mengubah tipe data kolom 'dteday' menjadi datetime
all_data_df['dteday'] = pd.to_datetime(all_data_df['dteday'])

# Menambahkan kolom total_rentals
all_data_df['total_rentals'] = all_data_df['casual'] + all_data_df['registered']

# Menghitung Recency (R), Frequency (F), dan Monetary (M)
current_date = all_data_df['dteday'].max()
all_data_df['recency'] = (current_date - all_data_df['dteday']).dt.days

customer_data = all_data_df.groupby('instant').agg(
    frequency=('total_rentals', 'sum'),
    recency=('recency', 'min')
).reset_index()

customer_data['monetary'] = customer_data['frequency'] * customer_data['recency']

# Segmentasi berdasarkan quantiles
quantiles = customer_data[['recency', 'frequency', 'monetary']].quantile([0.25, 0.5, 0.75])

def rfm_segment(x, var):
    if x <= quantiles[var][0.25]:
        return 1  # Low
    elif x <= quantiles[var][0.5]:
        return 2  # Medium
    else:
        return 3  # High

customer_data['recency_segment'] = customer_data['recency'].apply(rfm_segment, var='recency')
customer_data['frequency_segment'] = customer_data['frequency'].apply(rfm_segment, var='frequency')
customer_data['monetary_segment'] = customer_data['monetary'].apply(rfm_segment, var='monetary')

customer_data['rfm_score'] = customer_data['recency_segment'] + customer_data['frequency_segment'] + customer_data['monetary_segment']

# Judul Dashboard
st.title('Dashboard Data Penyewaan Sepeda')

# Menambahkan Sidebar untuk memilih filter
st.sidebar.title('Pilih Filter Data')

# Filter untuk memilih visualisasi
visualization_option = st.sidebar.selectbox(
    'Pilih Visualisasi:',
    ('Pengaruh Cuaca terhadap Penyewaan Sepeda', 
     'Total Penyewaan Sepeda per Bulan', 
     'Distribusi Penyewaan Sepeda per Jam',
     'Distribusi Pelanggan Berdasarkan Skor RFM')  # Opsi baru untuk RFM
)

# Fungsi untuk menampilkan visualisasi pertama (Pengaruh Cuaca terhadap Jumlah Penyewa Sepeda)
def plot_weather_impact(filtered_df):
    plt.figure(figsize=(10, 6))
    palette = sns.color_palette("muted")
    sns.barplot(x='weathersit', y='cnt', data=filtered_df, errorbar=None, palette=palette, hue='weathersit', legend=False)
    plt.title('Pengaruh Cuaca terhadap Jumlah Penyewa Sepeda', fontsize=16, fontweight='bold')
    plt.xlabel('Kondisi Cuaca', fontsize=12)
    plt.ylabel('Rata-rata Penyewaan Sepeda', fontsize=12)
    plt.xticks(ticks=[0, 1, 2, 3], labels=['Cerah', 'Berawan', 'Hujan ringan', 'Hujan berat'], fontsize=11)
    st.pyplot(plt)  # Menampilkan plot

# Fungsi untuk menampilkan visualisasi kedua (Total Penyewaan Sepeda per Bulan)
def plot_monthly_rentals(filtered_df):
    plt.figure(figsize=(12, 6))
    monthly_rentals = filtered_df.groupby('mnth')['cnt'].sum()
    monthly_rentals.plot(kind='bar', color='mediumseagreen', edgecolor='black')
    plt.xticks(ticks=range(12), labels=[calendar.month_name[i] for i in range(1, 13)], rotation=45, fontsize=11)
    plt.title('Total Penyewaan Sepeda per Bulan', fontsize=16, fontweight='bold')
    plt.xlabel('Bulan', fontsize=12)
    plt.ylabel('Total Penyewaan Sepeda', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)  # Menampilkan plot

# Fungsi untuk menampilkan visualisasi ketiga (Distribusi Penyewaan Sepeda per Jam)
def plot_hourly_rentals(filtered_df):
    plt.figure(figsize=(10, 6))
    hourly_rentals = filtered_df.groupby('hr')['cnt'].mean()
    plt.plot(hourly_rentals.index, hourly_rentals.values, marker='o', color='purple', linewidth=2)
    plt.title('Distribusi Penyewaan Sepeda per Jam', fontsize=16, fontweight='bold')
    plt.xlabel('Jam', fontsize=12)
    plt.ylabel('Rata-rata Penyewaan Sepeda', fontsize=12)
    plt.xticks(range(0, 24))
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)  # Menampilkan plot

# Fungsi untuk menampilkan visualisasi RFM
def plot_rfm_distribution(customer_data):
    plt.figure(figsize=(10, 6))
    sns.countplot(data=customer_data, x='rfm_score', palette='viridis')
    plt.title('Distribusi Pelanggan Berdasarkan Skor RFM', fontsize=16)
    plt.xlabel('Skor RFM', fontsize=12)
    plt.ylabel('Jumlah Pelanggan', fontsize=12)
    st.pyplot(plt)

# Menampilkan visualisasi berdasarkan pilihan pengguna
if visualization_option == 'Pengaruh Cuaca terhadap Penyewaan Sepeda':
    plot_weather_impact(all_data_df)
elif visualization_option == 'Total Penyewaan Sepeda per Bulan':
    plot_monthly_rentals(all_data_df)
elif visualization_option == 'Distribusi Penyewaan Sepeda per Jam':
    plot_hourly_rentals(all_data_df)
elif visualization_option == 'Distribusi Pelanggan Berdasarkan Skor RFM':
    plot_rfm_distribution(customer_data)  # Menampilkan plot RFM
