import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def price_analysis(FILTERED_DF):

    # CARD KPIS
    
    # TOTAL PRODUCTS
    total_products = FILTERED_DF["product_id"].nunique()
    # TOTAL VARIANTS
    total_variants = FILTERED_DF["variant_id"].nunique()
    # TOTAL DISCOUNTED PRODUCTS
    total_discounted_variants = FILTERED_DF[FILTERED_DF["discount"] > 0]["variant_id"].nunique()
    # Total Categories
    total_categories = FILTERED_DF["category_name"].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products", f"{total_products:,}")
    with col2:
        st.metric("Total Variants", f"{total_variants:,}")
    with col3:
        st.metric("Discounted Variants", f"{total_discounted_variants:,}")
    with col4:
        st.metric("Total Categories", f"{total_categories:,}")

    
    # AVERAGE PRICE BY CATEGORY
    unique_products = FILTERED_DF.drop_duplicates(subset=["product_id"])
    kpi_avg_price_category = (
        unique_products.groupby("category_name", as_index=False)
        .agg(average_price=("new_price", "mean"))
        .sort_values("average_price", ascending=False)
    )

    fig_kpi_avg_price_category = px.bar(
        kpi_avg_price_category,
        x="category_name",
        y="average_price",
        labels={"category_name": "Category", "average_price": "Average Price"},
    )
    fig_kpi_avg_price_category.update_layout(
        title={
            "text": "Average Price By Category",
            "font": {"size": 25, "color": "darkgrey", "family": "Uber Move Medium"},
            "x": 0.5,
            "xanchor": "center",
        },
    )

    st.plotly_chart(fig_kpi_avg_price_category, use_container_width=True)

    # PRICE DISTRIBUTION
    products_price = FILTERED_DF.groupby("product_id").agg(
        product_price=("new_price", "min")
    )

    fig_kpi_price_distribution = px.histogram(
        products_price,
        x="product_price",
        labels={"product_price": "Price (PKR)"},
        nbins=50,
        template="simple_white",
        height=500,
        width=900,
    )
    fig_kpi_price_distribution.update_layout(
        title={
            "text": "Price Distribution",
            "font": {"size": 25, "color": "darkgrey", "family": "Uber Move Medium"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    fig_kpi_price_distribution.update_xaxes(showline=False)
    fig_kpi_price_distribution.update_yaxes(showline=False)

    st.plotly_chart(fig_kpi_price_distribution, use_container_width=True)

    # Avg Old Price vs New Price By Category
    compare_avg_old_new_price = (
        unique_products.groupby("category_name", as_index=False)
        .agg(avg_old_price=("old_price", "mean"), avg_new_price=("new_price", "mean"))
        .sort_values(["avg_old_price", "avg_new_price"], ascending=False)
    )

    fig = go.Figure()
    fig.add_bar(
        x=compare_avg_old_new_price["category_name"],
        y=compare_avg_old_new_price["avg_old_price"],
        name="Old Price",
    )
    fig.add_bar(
        x=compare_avg_old_new_price["category_name"],
        y=compare_avg_old_new_price["avg_new_price"],
        name="New Price",
    )
    fig.update_layout(
        barmode="group",
        title={
            "text": "Avg Old Price vs New Price By Category",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Category",
        yaxis_title="Average Price (PKR)",
    )
    st.plotly_chart(fig, use_container_width=True)