import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Sales Dashboard")

# Load data directly from dexa.xlsx
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('data.xlsx', parse_dates=['INVOICE_DATE', 'FULL_DATE'])
    except FileNotFoundError:
        st.error("Could not find dexa.xlsx in the app directory. Please ensure the file is present.")
        st.stop()
    return df

# Load dataframe
df = load_data()

# Sidebar filters
date_range = st.sidebar.date_input(
    "Invoice Date Range",
    [df['INVOICE_DATE'].min(), df['INVOICE_DATE'].max()]
)
channels = st.sidebar.multiselect(
    "Channel Group",
    options=df['CHANNEL_GRUP'].unique(),
    default=df['CHANNEL_GRUP'].unique()
)
customers = st.sidebar.multiselect(
    "Customer",
    options=df['CUSTOMER_NAME'].unique(),
    default=df['CUSTOMER_NAME'].unique()
)
line_sales_filter = st.sidebar.multiselect(
    "Line Sales",
    options=df['LINE_SALES'].unique(),
    default=df['LINE_SALES'].unique()
)
products = st.sidebar.multiselect(
    "Product Code",
    options=df['PRODUCT_CODE'].unique(),
    default=df['PRODUCT_CODE'].unique()
)

# Apply filters
df_filtered = df[
    (df['INVOICE_DATE'] >= pd.to_datetime(date_range[0])) &
    (df['INVOICE_DATE'] <= pd.to_datetime(date_range[1])) &
    (df['CHANNEL_GRUP'].isin(channels)) &
    (df['PRODUCT_CODE'].isin(products)) &
    (df['CUSTOMER_NAME'].isin(customers)) &
    (df['LINE_SALES'].isin(line_sales_filter))
]

# KPIs
total_sales = df_filtered['Amount'].sum()
total_qty = df_filtered['QTY'].sum()
avg_price = df_filtered['PRICE'].mean()
trans_count = df_filtered['TRX_ID'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales (Mio)", f"{total_sales/1e6:,.2f}")
col2.metric("Total Quantity", f"{total_qty:,.0f}")
col3.metric("Average Price", f"{avg_price:,.0f}")
col4.metric("Transactions", f"{trans_count}")

st.markdown("---")

# Sales breakdown side by side
st.subheader("Sales Breakdown")
sales_col1, sales_col2 = st.columns(2)
with sales_col1:
    st.subheader("Sales by Channel")
    chan_agg = df_filtered.groupby('CHANNEL_GRUP').agg({'Amount': 'sum'}).reset_index()
    fig_channel = px.bar(chan_agg, x='CHANNEL_GRUP', y='Amount', title='Sales by Channel')
    st.plotly_chart(fig_channel, use_container_width=True)
with sales_col2:
    st.subheader("Sales by Customer")
    cust_agg = df_filtered.groupby('CUSTOMER_NAME').agg({'Amount': 'sum'}).reset_index()
    fig_cust = px.bar(cust_agg, x='CUSTOMER_NAME', y='Amount', title='Sales by Customer')
    st.plotly_chart(fig_cust, use_container_width=True)

# Top breakdown side by side
st.subheader("Top Performers")
top_col1, top_col2 = st.columns(2)
with top_col1:
    st.subheader("Top 5 Products")
    prod_agg = df_filtered.groupby('PRODUCT_CODE').agg({'Amount': 'sum'}).reset_index()
    prod_top = prod_agg.sort_values('Amount', ascending=False).head(5)
    fig_prod = px.bar(prod_top, x='PRODUCT_CODE', y='Amount', title='Top 5 Products by Sales')
    st.plotly_chart(fig_prod, use_container_width=True)
with top_col2:
    st.subheader("Top 5 Line Sales")
    line_agg = df_filtered.groupby('LINE_SALES').agg({'Amount': 'sum'}).reset_index()
    line_top = line_agg.sort_values('Amount', ascending=False).head(5)
    fig_line = px.bar(line_top, x='LINE_SALES', y='Amount', title='Top 5 Line Sales by Amount')
    st.plotly_chart(fig_line, use_container_width=True)

# Time series chart
st.subheader("Sales Over Time")
time_agg = df_filtered.groupby('INVOICE_DATE').agg({'Amount': 'sum'}).reset_index()
fig_time = px.line(time_agg, x='INVOICE_DATE', y='Amount', title='Daily Sales')
fig_time.update_layout(xaxis=dict(tickformat="%Y-%m-%d"))
st.plotly_chart(fig_time, use_container_width=True)

# Detailed data view
with st.expander("Show detailed data table"):
    st.dataframe(df_filtered.reset_index(drop=True))

st.markdown("---")
st.info("Use the filters to drill down into specific channels, products, dates, customers, and line sales.")