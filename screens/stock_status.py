import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def stock_status(FILTERED_DF):

    # Availability by Category
    available_variants = FILTERED_DF[FILTERED_DF["is_available"] == True]
    available_unique_variants = available_variants.drop_duplicates(subset=["variant_id"])
    kpi_availibility_by_category = (
        available_unique_variants.groupby("category_name", as_index=False)
        .agg(available_variants_count=("variant_id", "count"))
        .sort_values("available_variants_count", ascending=False)
    )

    fig_kpi_availibility_by_category = px.bar(
        kpi_availibility_by_category,
        x="category_name",
        y="available_variants_count",
        labels={"category_name": "Category", "available_variants_count": "Products"},
    )
    fig_kpi_availibility_by_category.update_layout(
        title={
            "text": "Availability by Category",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_availibility_by_category)

    # Category Stock Balance
    df_copy = FILTERED_DF.copy()
    unique_variants = df_copy.drop_duplicates(subset=["variant_id"])
    kpi_category_in_vs_out_stock = unique_variants.groupby(
        ["category_id", "category_name"], as_index=False
    ).agg(
        in_stock_count=("is_available", lambda x: (x == True).sum()),
        sold_out_count=("is_available", lambda x: (x == False).sum()),
    )

    fig_kpi_category_in_vs_out_stock = go.Figure()
    fig_kpi_category_in_vs_out_stock.add_bar(
        x=kpi_category_in_vs_out_stock["category_name"],
        y=kpi_category_in_vs_out_stock["in_stock_count"],
        name="In Stock",
    )
    fig_kpi_category_in_vs_out_stock.add_bar(
        x=kpi_category_in_vs_out_stock["category_name"],
        y=kpi_category_in_vs_out_stock["sold_out_count"],
        name="Sold Out",
    )
    fig_kpi_category_in_vs_out_stock.update_layout(
        barmode="group",
        title={
            "text": "Category Stock Balance",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Category",
        yaxis_title="Stock Status",
    )

    st.plotly_chart(fig_kpi_category_in_vs_out_stock, use_container_width=True)

    # Top Categories with Low Availability
    sold_out_criteria = 1000
    kpi_low_avb_categories = kpi_category_in_vs_out_stock[
        kpi_category_in_vs_out_stock["sold_out_count"] > sold_out_criteria
    ]
    fig_kpi_low_avb_categories = px.bar(
        kpi_low_avb_categories,
        x="category_name",
        y="sold_out_count",
        labels={"category_name": "Category", "sold_out_count": "Sold Out Products"},
    )
    fig_kpi_low_avb_categories.update_layout(
        title={
            "text": "Top Categories with Low Availability",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_low_avb_categories, use_container_width=True)
