import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


# Fungsi-fungsi Penyiapan DataFrame

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return daily_orders_df


def create_rfm_df(df):

    recent_date = df["order_purchase_timestamp"].max()

    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max",   # tanggal transaksi terakhir
        "order_id": "nunique",               # frequency
        "payment_value": "sum"               # monetary
    })
    rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days
    )
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state", as_index=False).agg({
        "payment_value": "sum",
        "delivery_time_days": "mean"
    })
    bystate_df.rename(columns={
        "payment_value": "total_revenue",
        "delivery_time_days": "avg_delivery_time_days"
    }, inplace=True)

    return bystate_df


def create_bycustomer_count_state_df(df):
    bycustomer_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    bycustomer_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)

    return bycustomer_df


# Load Data

all_df = pd.read_csv("main_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True, drop=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Menghitung delivery_time_days (khusus order yang sudah delivered)

all_df["delivery_time_days"] = (all_df["order_delivered_customer_date"] - all_df["order_purchase_timestamp"]).dt.days

# Komponen Filter (Sidebar)

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.title("E-Commerce Dashboard")
    st.caption("Olist Brazilian E-Commerce Public Dataset")

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= str(start_date)) &
    (all_df["order_purchase_timestamp"] <= str(end_date))
]

daily_orders_df = create_daily_orders_df(main_df)
rfm_df = create_rfm_df(main_df)
bystate_df = create_bystate_df(main_df)
bycustomer_state_df = create_bycustomer_count_state_df(main_df)


# Dashboard

st.header('E-Commerce Public Dataset Dashboard :sparkles:')

# Daily Orders 

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=f"{total_orders:,}")

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Jumlah Order Harian", fontsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=12)

st.pyplot(fig)


# Revenue & Delivery Time per State 

st.subheader("Revenue & Delivery Time by State")

col1, col2 = st.columns(2)

with col1:
    top_state_revenue = bystate_df.sort_values(by="total_revenue", ascending=False).iloc[0]
    st.metric("Top State (Revenue)", value=top_state_revenue["customer_state"])

with col2:
    fastest_state = bystate_df.sort_values(by="avg_delivery_time_days", ascending=True).iloc[0]
    st.metric("Fastest Delivery State", value=fastest_state["customer_state"])

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 12))

top10_revenue = bystate_df.sort_values(by="total_revenue", ascending=False).head(10)
colors_rev = ["#90CAF9" if state != top10_revenue.iloc[0]["customer_state"] else "#F24236"
              for state in top10_revenue["customer_state"]]
colors_rev = ["#F24236" if i == 0 else "#90CAF9" for i in range(len(top10_revenue))]

sns.barplot(
    x="total_revenue", y="customer_state",
    data=top10_revenue, palette=colors_rev, ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Revenue (R$)", fontsize=25)
ax[0].set_title("Top 10 State by Revenue", loc="center", fontsize=35)
ax[0].tick_params(axis='y', labelsize=25)
ax[0].tick_params(axis='x', labelsize=20)

top10_delivery = bystate_df.sort_values(by="avg_delivery_time_days", ascending=True).head(10)
colors_del = ["#F24236" if i == 0 else "#90CAF9" for i in range(len(top10_delivery))]

sns.barplot(
    x="avg_delivery_time_days", y="customer_state",
    data=top10_delivery, palette=colors_del, ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Avg Delivery Time (days)", fontsize=25)
ax[1].set_title("Top 10 State by Fastest Delivery", loc="center", fontsize=35)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=20)

st.pyplot(fig)

# Jumlah pelanggan per state

fig, ax = plt.subplots(figsize=(20, 10))
top10_customer_state = bycustomer_state_df.sort_values(by="customer_count", ascending=False).head(10)
colors_cust = ["#F24236" if i == 0 else "#90CAF9" for i in range(len(top10_customer_state))]

sns.barplot(
    x="customer_count", y="customer_state",
    data=top10_customer_state, palette=colors_cust, ax=ax
)
ax.set_title("Top 10 State by Number of Customers", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)


# RFM Analysis 

st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR')
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(
    y="recency", x="customer_unique_id",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=colors, ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_unique_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=20, rotation=90)

sns.barplot(
    y="frequency", x="customer_unique_id",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=colors, ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_unique_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=20, rotation=90)

sns.barplot(
    y="monetary", x="customer_unique_id",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    palette=colors, ax=ax[2]
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_unique_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=20, rotation=90)

st.pyplot(fig)

st.caption('Copyright (c) Tokesi Lukynawa 2026')
