import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sn
import geopandas as gpd
import streamlit as st

# Fungsi yang akan digunakan
def analyze_geography(input_df):
    agg = {
    "order_id": "count"
    }
    pembelian_states = input_df[input_df['order_status'] == 'delivered'].groupby('customer_state').agg(agg).reset_index()
    pembelian_states.columns = ['customer_state', 'total_rows']
    pembelian_states = pembelian_states.sort_values(by='total_rows', ascending=False)
    pembelian_states_tertinggi = pembelian_states.head(25)

    return pembelian_states_tertinggi, input_df

def analyze_geography2(input_df):
    agg = {
    "order_id": "count"
    }

    pembelian_city = input_df[input_df['order_status'] == 'delivered'].groupby('customer_city').agg(agg).reset_index()
    pembelian_city.columns = ['customer_city', 'total_rows']
    pembelian_city = pembelian_city.sort_values(by='total_rows', ascending=False)
    pembelian_city_tertinggi = pembelian_city.head(25)

    return pembelian_city_tertinggi, input_df

def analyze_customer_reorder(input_df):
    customer_purchase_counts = input_df.groupby(by="customer_unique_id").order_id.nunique()
    customer_purchase_counts = customer_purchase_counts.sort_values(ascending=False)
    customer_purchase_counts.columns = ['customer_unique_id', 'count']
    transaction_counts = input_df.groupby('customer_unique_id').size().reset_index(name='transaction_count')

    return transaction_counts

def analyze_kategori_produk(input_df):
    agg = {
    'review_score': 'mean',
    'order_id': 'count'
    }

    # Kelompokkan sesuai dengan kategori produk
    result = input_df.groupby('product_category_name_english').agg(agg).reset_index()
    result.columns = ['product_category_name', 'avg_review_score', 'num_orders']

    # Sort dataframe sesuai dengan avg_review_score
    sorted_result = result.sort_values(by='avg_review_score', ascending=False)

    return sorted_result
    

# Import dataset
# Dataset Utama
all_data_df = pd.read_csv("https://raw.githubusercontent.com/AxellSiagian/E-Commerce_Analysis/master/data/all_data_df.csv").sort_values(by="order_approved_at").reset_index()
all_data_df.info()

# Dataset Geolocation
geolocation_df = pd.read_csv("https://raw.githubusercontent.com/AxellSiagian/E-Commerce_Analysis/master/data/geolocation_dataset.csv")
earth = gpd.read_file("https://raw.githubusercontent.com/AxellSiagian/E-Commerce_Analysis/master/data/earth.shp")
earthx = gpd.read_file("https://raw.githubusercontent.com/AxellSiagian/E-Commerce_Analysis/master/data/earth.shx")

# Mengubah data type datetime
perbaiki_datetime = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
for kolom in perbaiki_datetime:
    all_data_df[kolom] = pd.to_datetime(all_data_df[kolom])

# Menentukan min&max tanggal untuk diproses dalam dashboard
min_date = all_data_df["order_approved_at"].min()
max_date = all_data_df["order_approved_at"].max()

# Sidebar dari dashboard
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/AxellSiagian/E-Commerce_Analysis/master/data/logo.png")
    
    st.write("Oleh: Axell Amadeus Siagian")
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Input Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Main Section
main_df = all_data_df[(all_data_df["order_approved_at"] >= str(start_date)) & 
                 (all_data_df["order_approved_at"] <= str(end_date))]


# MAIN
st.header('Analisis E-Commerce Public Data')


# PEMBELIAN GEOGRAFIS TERTINGGI
st.subheader('Lokasi Geografis dengan Pembelian Tertinggi')

# STATES
st.write('Lokasi berdasarkan States:')
pembelian_states_tertinggi, pembelian_states = analyze_geography(main_df)

# Warna untuk plotting
colors = plt.cm.viridis(np.linspace(0, 1, len(pembelian_states)))

# Plotting data
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#C7C7C7')
bars = sn.barplot(
    x=pembelian_states_tertinggi['customer_state'], 
    y=pembelian_states_tertinggi['total_rows'], 
    palette=colors,
    ax=ax
)

# Menambahkan judul dan label
ax.set_title('Total Pembelian Masing-Masing State')
ax.set_xlabel('State')
ax.set_ylabel('Total Pembelian')

# Membuat plot
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Display plot in Streamlit
st.pyplot(fig)


# CITY
st.write('Lokasi berdasarkan Kota:')
pembelian_city_tertinggi, pembelian_city = analyze_geography2(main_df)

# Warna untuk plotting
colors = plt.cm.viridis(np.linspace(0, 1, len(pembelian_city)))

# Plotting data
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#C7C7C7')
bars = sn.barplot(
    x=pembelian_city_tertinggi['customer_city'], 
    y=pembelian_city_tertinggi['total_rows'], 
    palette=colors,
    ax=ax
)

# Menambahkan judul dan label
ax.set_title('Total Pembelian Masing-Masing Kota')
ax.set_xlabel('Kota')
ax.set_ylabel('Total Pembelian')

# Membuat plot
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Display plot in Streamlit
st.pyplot(fig)



# Pelanggan yang order berulang
st.write()
st.subheader('Analisis Pelanggan Order Berulang')

transaction_counts = analyze_customer_reorder(main_df)

# Warna khusus
colors = {2:'#A58989', 3: '#8D6B6B', 4: '#A87070', 5: '#A65454', 6: '#9E3737', 7: '#9C2121'}

# Menghitung total dari customer
total_customers = len(transaction_counts)

# Menghitung customer yang order sebanyak 1 kali atau lebih
single_transaction_count = (transaction_counts['transaction_count'] == 1).sum()
multiple_transaction_count = total_customers - single_transaction_count
multiple_transactions = transaction_counts[transaction_counts['transaction_count'] > 0]
multiple_transactions = multiple_transactions.groupby('transaction_count').size().reset_index(name='customer_count')

# Plotting pie chart untuk perbandingan transaksi satu kali dan yang berulang
col1, col2, col3 = st.columns(3)

with col1:
    st.write('Perbandingan Customer Sekali Order dan Berulang')
    fig1, ax1 = plt.subplots()
    fig.patch.set_facecolor('#C7C7C7')
    ax1.pie([single_transaction_count, multiple_transaction_count], labels=['Order Sekali', 'Order Berulang'], autopct='%1.1f%%', startangle=140, colors=['#939393', '#A58989'])
    # ax1.set_title('Perbandingan Customer Sekali Order dan Berulang')
    ax1.axis('equal')
    st.pyplot(fig1)

# Plotting pie chart perbandingan transaksi 2, 3, dan 4 atau lebih
with col2:
    st.write('Perbandingan Customer Berulang (2 hingga 4+ Order)')
    fig2, ax2 = plt.subplots()
    fig.patch.set_facecolor('#C7C7C7')
    sizes = [multiple_transactions[multiple_transactions['transaction_count'] == 2]['customer_count'].values[0],
             multiple_transactions[multiple_transactions['transaction_count'] == 3]['customer_count'].values[0],
             multiple_transactions[multiple_transactions['transaction_count'] >= 4]['customer_count'].sum()]
    labels = ['2 Order', '3 Order', '4+ Order']
    ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=[colors[int(label[0])] for label in labels])
    # ax2.set_title('Distribusi Customer Berulang (2 hingga 4+ Order)')
    ax2.axis('equal')
    st.pyplot(fig2)

# Plotting pie chart perbandingan transaksi 3, 4, 5, 6, dan 7 atau lebih
with col3:
    st.write('Perbandingan Customer Berulang (3 hingga 7+ Order)')
    fig3, ax3 = plt.subplots()
    fig.patch.set_facecolor('#C7C7C7')
    sizes = [multiple_transactions[multiple_transactions['transaction_count'] == 3]['customer_count'].values[0],
             multiple_transactions[multiple_transactions['transaction_count'] == 4]['customer_count'].values[0],
             multiple_transactions[multiple_transactions['transaction_count'] == 5]['customer_count'].values[0],
             multiple_transactions[multiple_transactions['transaction_count'] == 6]['customer_count'].values[0],
             multiple_transactions[multiple_transactions['transaction_count'] >= 7]['customer_count'].sum()]
    labels = ['3 Order', '4 Order', '5 Order', '6 Order', '7+ Order']
    ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=[colors[int(label[0])] for label in labels])
    # ax3.set_title('Distribusi Customer Berulang (3 hingga 7+ Order)')
    ax3.axis('equal')
    st.pyplot(fig3)



# KATEGORI PRODUK DENGAN NILAI TERBAIKs
st.subheader('Analisis Kategori Produk Terbaik/Terburuk')
sorted_result = analyze_kategori_produk(main_df)

# Mengambil 5 kategori terbaik dan terburuk
top_categories = sorted_result.head(5)
bottom_categories = sorted_result.tail(5)

# Create columns for each plot
col1, col2 = st.columns(2)

# Plotting kategori terbaik
with col1:
    st.write('5 Kategori Produk Terbaik')
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#C7C7C7')
    ax1.barh(top_categories['product_category_name'], top_categories['avg_review_score'], color='skyblue')
    ax1.set_xlabel('Rata-Rata Review')
    ax1.set_ylabel('Product Category')
    ax1.set_xlim(0, 5)
    st.pyplot(fig1)

# Plotting kategori terburuk
with col2:
    st.write('5 Kategori Produk Terburuk')
    fig2, ax2 = plt.subplots(figsize=(8, 6.5))
    fig.patch.set_facecolor('#C7C7C7')
    ax2.barh(bottom_categories['product_category_name'][::-1], bottom_categories['avg_review_score'][::-1], color='salmon')
    ax2.set_xlabel('Rata-Rata Review')
    ax2.set_ylabel('Product Category')
    ax2.set_xlim(5, 0)
    ax2.yaxis.tick_right()
    st.pyplot(fig2)


# Plot daerah
st.subheader('Analisis Lokasi Geolocation')

# Create a sample dataframe (replace this with your actual dataframe)
df = geolocation_df

# Create columns for the map and the scatter plot
col1, col2 = st.columns([3, 1])

# Plot the map of Brazil
fig, ax = plt.subplots(figsize=(20, 12))
earth.plot(ax=ax, color='lightgrey', edgecolor='brown')

# Plot the locations on top of the map
ax.scatter(df['geolocation_lng'], df['geolocation_lat'], color='blue', alpha=0.5, label='Titik Lokasi')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Data Geolocation Overlay pada Peta Dunia')
plt.legend()
plt.grid(True)
st.pyplot(fig)

st.caption('Work of Axell Amadeus Siagian 2024')
