import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.db import database_connection
from filters.global_filters import global_filter
from screens.colour_storage_trends import colour_storage_trends
from screens.discount_analysis import discount_analysis
from screens.price_analysis import price_analysis
from screens.stock_status import stock_status
from screens.variant_structure import variant_structure


# DATABASE CONNECTION
try:
    conn = database_connection()
except Exception as e:
    conn = None
    st.warning("Database disabled in cloud demo")

st.set_page_config(page_title="Priceoye Dashboard")


query = """
SELECT p.product_id,c.category_id,variant_id, p.name As product_name, c.name As category_name, clr.name As color_name, v.old_price, v.new_price,v.discount, v.rating, v.is_available, s.RAM, s.ROM FROM variant v
JOIN product p ON p.product_id = v.product_id
JOIN category c ON c.category_id = p.category_id
JOIN colour clr ON clr.product_id = p.product_id
JOIN storage s ON s.product_id = p.product_id
"""


# BASE DATAFRAME
DF_BASE = pd.read_sql(query, conn)
# FILTERED DATAFRAME
FILTERED_DF = global_filter(DF_BASE)


# sidebar
st.sidebar.image(
    r"D:\data_science\Python\Streamlit Projects\Priceoye Analyzer\logo\Priceoye_logo.png",
    caption="PriceOye",
)
# PAGE NAVIGATION
page = st.selectbox(
    label="Select Page",
    options=[
        "Price Analysis",
        "Discount Analysis",
        "Availability & Stock Status",
        "Variant Structure",
        "Color & Storage Trends",
    ],
)

# RATING RANGE FILTER
filter_rating_value = st.sidebar.slider(
    "Rating Range",
    min_value=1.0,
    max_value=5.0,
    value=(1.0, 5.0),
    step=0.1,
    key="slider_range",
)
# CATEGORY FILTER
category_names = DF_BASE["category_name"].dropna().unique()
filter_category_name = st.sidebar.multiselect(
    "Select Category",
    options=category_names,
    default=category_names,
    key="selected_category_names",
)


if page == "Price Analysis":
    price_analysis(FILTERED_DF)
elif page == "Discount Analysis":
    discount_analysis(FILTERED_DF)
elif page == "Availability & Stock Status":
    stock_status(FILTERED_DF)
elif page == "Variant Structure":
    variant_structure(FILTERED_DF)
elif page == "Color & Storage Trends":
    colour_storage_trends(FILTERED_DF)
