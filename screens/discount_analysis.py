import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def discount_analysis(FILTERED_DF):

    # DISCOUNT DISTRIBUTION
    unique_variants = FILTERED_DF.drop_duplicates(subset=["variant_id"])
    discount_values = unique_variants["discount"].dropna()
    fig_kpi_discount_distribution = px.histogram(
        discount_values,
        x="discount",
        labels={"discount", "Discount (%)"},
        nbins=50,
        template="simple_white",
        height=450,
    )
    fig_kpi_discount_distribution.update_layout(
        title={
            "text": "Discount Distribution (%)",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis=dict(showline=False),
        yaxis=dict(showline=False),
    )

    st.plotly_chart(fig_kpi_discount_distribution)

    # TOP DISCOUNTED PRODUCTS
    discounted_products = (
        FILTERED_DF.groupby(["product_id", "product_name"], as_index=False)["discount"]
        .max()
        .sort_values("discount", ascending=False)
        .head(10)
    )
    fig_kpi_top_discounted_products = px.bar(
        discounted_products,
        # orientation="h",    #horizontal
        x="product_name",
        y="discount",
        labels={"product_name": "Product Name", "discount": "Discount (%)"},
    )
    fig_kpi_top_discounted_products.update_layout(
        title={
            "text": "Top Discounted Products",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_top_discounted_products, use_container_width=True)

    # DISCOUNT VS RATINGS
    kpi_discount_vs_ratings = (
        unique_variants.dropna(subset=["discount", "rating"])
        .groupby("product_id")
        .agg(max_discount=("discount", "max"), max_rating=("rating", "max"))
    )
    fig_kpi_discount_vs_ratings = px.scatter(
        kpi_discount_vs_ratings,
        x="max_discount",
        y="max_rating",
        labels={"max_discount": "Discount (%)", "max_rating": "Rating"},
    )
    fig_kpi_discount_vs_ratings.update_layout(
        title={
            "text": "Discount Vs Rating",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_discount_vs_ratings)

    # Average Discount by Category
    kpi_avg_discount_by_category = (
        unique_variants.dropna(subset=["category_name", "discount"])
        .groupby(["category_id", "category_name"], as_index=False)
        .agg(avg_discount=("discount", "mean"))
        .round(0)
        .sort_values("avg_discount", ascending=False)
    )
    fig_kpi_avg_discount_by_category = px.bar(
        kpi_avg_discount_by_category,
        x="category_name",
        y="avg_discount",
        labels={"category_name": "Category", "avg_discount": "Discount (%)"},
    )
    fig_kpi_avg_discount_by_category.update_layout(
        title={
            "text": "Average Discount by Category",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_avg_discount_by_category)
