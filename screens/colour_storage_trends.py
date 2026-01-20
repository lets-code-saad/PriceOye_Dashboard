import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from filters.colour_and_storage_filters import colour_storage_filter


def colour_storage_trends(FILTERED_DF):

    CLEANED_COLOUR_STORAGE_DF = FILTERED_DF.dropna(subset=["RAM", "ROM"])
    FILTERED_COLOUR_STORAGE_DF = colour_storage_filter(CLEANED_COLOUR_STORAGE_DF)
    unique_variants = FILTERED_COLOUR_STORAGE_DF.drop_duplicates(subset=["variant_id"])

    CLEANED_COLOUR_STORAGE_DF["storage_combination"] = (
        CLEANED_COLOUR_STORAGE_DF["RAM"].astype(str)
        + "GB RAM - "
        + CLEANED_COLOUR_STORAGE_DF["ROM"].astype(str)
        + "GB ROM"
    )
    storage_combinations = (
        CLEANED_COLOUR_STORAGE_DF["storage_combination"].dropna().unique()
    )
    st.sidebar.multiselect(
        "Select Storage Combination",
        options=storage_combinations,
        default=storage_combinations,
        key="selected_storage_combination",
    )

    # 10 Most Common Colors

    kpi_most_common_colors = (
        unique_variants.groupby("color_name", as_index=False)
        .agg(count_color_products=("product_id", "count"))
        .sort_values("count_color_products", ascending=False)
    ).head(10)

    fig_kpi_most_common_colors = px.bar(
        kpi_most_common_colors,
        x="color_name",
        y="count_color_products",
        labels={"color_name": "Colour", "count_color_products": "Variants"},
    )
    fig_kpi_most_common_colors.update_layout(
        title={
            "text": "10 Most Common Colors",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_most_common_colors)

    # Color-wise Availability
    available_colours = FILTERED_COLOUR_STORAGE_DF[
        FILTERED_COLOUR_STORAGE_DF["is_available"] == True
    ]
    kpi_color_wise_avb = (
        available_colours.groupby("color_name", as_index=False)
        .agg(total_avb_colours=("product_id", "count"))
        .sort_values("total_avb_colours", ascending=False)
        .head(10)
    )
    fig_kpi_color_wise_avb = px.bar(
        kpi_color_wise_avb,
        x="total_avb_colours",
        y="color_name",
        orientation="h",
        labels={"color_name": "Colour", "total_avb_colours": "Available Products"},
    )
    fig_kpi_color_wise_avb.update_layout(
        title={
            "text": "Color-wise Availability",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_color_wise_avb, use_container_width=True)

    # Storage Popularity
    unique_storages = FILTERED_COLOUR_STORAGE_DF.dropna(
        subset=["RAM", "ROM"]
    ).drop_duplicates()
    
    kpi_storage_popularity = (
        unique_storages.groupby(["RAM", "ROM"], as_index=False)
        .agg(total_storage_products=("product_id", "count"))
        .sort_values("total_storage_products", ascending=False)
    )
    # CREATING STORAGE COMBINATION COLUMN
    kpi_storage_popularity["storage_combination"] = (
        kpi_storage_popularity["RAM"].astype(str)
        + "GB RAM - "
        + kpi_storage_popularity["ROM"].astype(str)
        + "GB ROM"
    )
    fig_kpi_storage_popularity = px.bar(
        kpi_storage_popularity,
        orientation="h",
        x="total_storage_products",
        y="storage_combination",
        labels={
            "storage_combination": "Storage",
            "total_storage_products": "Total Variants",
        },
        height=550,
    )

    fig_kpi_storage_popularity.update_layout(
        title={
            "text": "Storage Popularity",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_storage_popularity, use_container_width=True)

    # Average Price by Storage
    unique_storages = FILTERED_COLOUR_STORAGE_DF.dropna(
        subset=["RAM", "ROM"]
    ).drop_duplicates()
    kpi_avg_price_by_storage = (
        unique_storages.groupby(["RAM", "ROM"], as_index=False)
        .agg(avg_storage_price=("new_price", "mean"))
        .round(1)
        .sort_values("avg_storage_price", ascending=True)
    )
    # CREATING STORAGE COMBINATION COLUMN
    kpi_avg_price_by_storage["storage_combination"] = (
        kpi_storage_popularity["RAM"].astype(str)
        + "GB RAM - "
        + kpi_storage_popularity["ROM"].astype(str)
        + "GB ROM"
    )
    fig_kpi_avg_price_by_storage = px.bar(
        kpi_avg_price_by_storage,
        orientation="h",
        x="avg_storage_price",
        y="storage_combination",
        labels={"storage_combination": "Storage", "avg_storage_price": "Average Price"},
        height=550,
    )
    fig_kpi_avg_price_by_storage.update_layout(
        title={
            "text": "Average Price by Storage",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_avg_price_by_storage, use_container_width=True)
