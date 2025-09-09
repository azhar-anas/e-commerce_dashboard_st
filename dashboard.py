import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set icon on browser tab
st.set_page_config(page_title="E-Commerce Dashboard", page_icon=":material/bar_chart_4_bars:")

# Set page style
st.markdown("""
    <style>
        .block-container {
            max-width: 80%;
            padding-top: 4.5rem;
        }
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1rem;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)


def create_orders_df(df):
    orders_df = df.resample(rule="D", on="order_purchase_timestamp").agg({
        "order_id": "nunique",
        "price": "sum"
    })
    orders_df = orders_df.reset_index()
    orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    # Remove outliers above the upper bound because there are outliers in the data
    q1 = orders_df["order_count"].quantile(0.25)
    q3 = orders_df["order_count"].quantile(0.75)
    iqr = q3 - q1
    maximum_bound = q3 + (1.5 * iqr)
    minimum_bound = q1 - (1.5 * iqr)
    lower_bound = orders_df["order_count"] < minimum_bound
    upper_bound = orders_df["order_count"] > maximum_bound
    orders_df.drop(orders_df[upper_bound].index, inplace=True)

    return orders_df

def create_bypayment_type_df(df):
    bypayment_type_df = df.groupby(by="payment_type").customer_id.nunique().reset_index()
    bypayment_type_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bypayment_type_df.sort_values(by="customer_count", ascending=False, inplace=True)
    
    return bypayment_type_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bystate_df.sort_values(by="customer_count", ascending=False, inplace=True)
    
    return bystate_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bycity_df.sort_values(by="customer_count", ascending=False, inplace=True)
    
    return bycity_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # take the last order date
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Load cleaned data
all_df = pd.read_csv("data/main_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Get start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label="Date Range",min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# # Prepare various dataframes
orders_df = create_orders_df(main_df)
bypayment_type_df = create_bypayment_type_df(main_df)
bystate_df = create_bystate_df(main_df)
bycity_df = create_bycity_df(main_df)
rfm_df = create_rfm_df(main_df)


# Plot delivered orders
st.markdown("<h1 style='text-align: center;'>E-Commerce Dashboard</h1>", unsafe_allow_html=True)
st.subheader("Delivered Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(orders_df.revenue.sum(), "BRL", locale="es_CO") 
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(
    orders_df["order_purchase_timestamp"],
    orders_df["order_count"],
    marker="o", 
    linewidth=2,
    color="tab:blue"
)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)

st.pyplot(fig)

# Plot Delivery Time
st.subheader("Delivery Time Performance")

fig, ax = plt.subplots(figsize=(16, 6))
values = [
    main_df['delivery_time_day'].max(),
    main_df['delivery_time_day'].mean(),
    main_df['delivery_time_day'].min()
]
labels = ['Maximum', 'Average', 'Minimum']
bars = ax.bar(labels, values, color=['tab:blue', 'tab:orange', 'tab:green'])
ax.set_title('Delivery Time (Days)', loc='center', fontsize=20)
ax.tick_params(axis='x', labelsize=10, rotation=0)
ax.tick_params(axis='y', labelsize=10)
ax.set_ylim(0, 250)
ax.grid(True, linestyle='--', alpha=0.7)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, fontweight='bold')
st.pyplot(fig)

# Plot customer details
st.subheader("Customer Details")

col1, col2 = st.columns([1, 1])

with col1:
    fig, ax = plt.subplots(figsize=(15, 10))
    colors = ["tab:blue", "tab:blue", "tab:blue", "lightblue", "lightblue", "lightblue", "lightblue", "lightblue", "lightblue", "lightblue"]
    sns.barplot(
        x="customer_count", 
        y="customer_state",
        data=bystate_df.head(10).sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by States", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="y", labelsize=20)
    ax.tick_params(axis="x", labelsize=20)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(11, 10))
    colors = ["tab:blue", "tab:blue", "tab:blue", "lightblue", "lightblue", "lightblue", "lightblue", "lightblue", "lightblue", "lightblue"]
    sns.barplot(
        x="customer_count", 
        y="customer_city",
        data=bycity_df.head(10).sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by Cities", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="y", labelsize=20)
    ax.tick_params(axis="x", labelsize=20)
    st.pyplot(fig)


# Show the most used payment methods in a pie chart
bypayment_type_df.loc[bypayment_type_df["payment_type"].isin(["debit_card", "voucher"]), "payment_type"] = "debit_card & voucher"
bypayment_type_df = bypayment_type_df.groupby("payment_type", as_index=False).sum()
bypayment_type_df.sort_values(by="customer_count", ascending=False, inplace=True)

fig, ax = plt.subplots(figsize=(4, 4))
colors_ = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

wedges, texts, autotexts = ax.pie(
    bypayment_type_df["customer_count"],
    labels=None,
    autopct=lambda p: f"{p:.1f}%\n({int(p * sum(bypayment_type_df['customer_count']) / 100)})",
    colors=colors_[:len(bypayment_type_df)],
    startangle=45,
    textprops={"fontsize": 6},
    radius=1.0
)
ax.set_title("Number of Customer by Payment Type", fontsize=6)

# Add tight and neat legend
ax.legend(
    wedges,
    bypayment_type_df["payment_type"],
    title="Payment Type",
    loc="center left",
    bbox_to_anchor=(1, 0.5),
    fontsize=6,
    title_fontsize=6,
    frameon=False
)

fig.tight_layout()
st.pyplot(fig)

# Best Customer Based on RFM Parameters
st.subheader("Best Customer (Customer ID) Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL", locale="es_CO") 
    st.metric("Average Monetary", value=avg_frequency)

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue"]

    sns.barplot(y="customer_id", x="recency", data=rfm_df.sort_values(by="recency", ascending=True).head(10), palette=colors, ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("By Recency (days)", loc="center", fontsize=50)
    ax.tick_params(axis="y", labelsize=30)
    ax.tick_params(axis="x", labelsize=40)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue"]

    sns.barplot(y="customer_id", x="frequency", data=rfm_df.sort_values(by="frequency", ascending=False).head(10), palette=colors, ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("By Frequency", loc="center", fontsize=50)
    ax.tick_params(axis="y", labelsize=30)
    ax.tick_params(axis="x", labelsize=40)
    st.pyplot(fig)
    
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue", "tab:blue"]

sns.barplot(y="customer_id", x="monetary", data=rfm_df.sort_values(by="monetary", ascending=False).head(10), palette=colors, ax=ax)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("By Monetary", loc="center", fontsize=30)
ax.tick_params(axis="y", labelsize=30)
ax.tick_params(axis="x", labelsize=35)
st.pyplot(fig)

st.caption("Copyright © Azhar Anas 2025")

