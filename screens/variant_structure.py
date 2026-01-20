import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def variant_structure(FILTERED_DF):

    # VARIANTS PER PRODUCT
    unique_variants = FILTERED_DF.drop_duplicates(subset=["variant_id"])
    kpi_variants_per_products = unique_variants.groupby(
        ["product_id", "product_name"], as_index=False
    ).agg(no_of_variants=("variant_id", "count"))
    fig_kpi_variants_per_products = px.histogram(
        kpi_variants_per_products,
        x="no_of_variants",
        nbins=50,
        labels={"count": "Products", "no_of_variants": "Variants"},
        template="simple_white",
        height=450,
    )
    fig_kpi_variants_per_products.update_layout(
        title={
            "text": "Variants Per Product",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis=dict(showline=False),
        yaxis=dict(showline=False),
    )
    st.plotly_chart(fig_kpi_variants_per_products)

    # Single vs Multiple Variant Products

    # Adding one more column of variant type
    kpi_variants_per_products["variant_type"] = kpi_variants_per_products[
        "no_of_variants"
    ].apply(lambda x: "Single Variant" if x == 1 else "Multiple Variants")
    
    variant_type_count = kpi_variants_per_products.groupby(
        "variant_type", as_index=False
    ).agg(products_count=("product_id", "count"))

    fig_kpi_single_vs_multiple = px.pie(
        variant_type_count,
        names="variant_type",
        values="products_count",
        labels={"variant_type": "Variant Type", "product_count": "Products"},
        hole=0.4,
    )
    fig_kpi_single_vs_multiple.update_layout(
        title={
            "text": "Single vs Multiple Variant Products",
            "font": {"size": 15, "family": "Uber Move Medium", "color": "darkgrey"},
            # "x": 0.2,
            # "xanchor": "center",
        },
    )

    # Category Contribution to Inventory
    unique_products = FILTERED_DF.dropna(subset=["product_id"]).drop_duplicates(subset=["product_id"])
    kpi_category_contribution = (
        unique_products.groupby(["category_name", "category_id"], as_index=False)
        .agg(total_products=("product_id", "count"))
    )
    fig_kpi_category_contribution = px.pie(
        kpi_category_contribution,
        names="category_name",
        values="total_products",
        labels={"category_name": "Category", "total_products": "Products"},
    )
    fig_kpi_category_contribution.update_layout(
        title={
            "text": "Category Contribution To Inventory",
            "font": {"size": 15, "family": "Uber Move Medium", "color": "darkgrey"},
            # "x": 0.2,
            # "xanchor": "center",
        },
    )
    # Showing them side by side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_kpi_single_vs_multiple, use_container_width=True)
    with col2:
        st.plotly_chart(fig_kpi_category_contribution, use_container_width=True)

    # Average Variants per Category
    variants_per_product = unique_variants.groupby(
        ["category_id", "category_name", "product_id"], as_index=False
    ).agg(variant_count=("variant_id", "count"))

    kpi_avg_variants_per_category = (
        variants_per_product.groupby(["category_id", "category_name"], as_index=False)
        .agg(avg_variants=("variant_count", "mean"))
        .sort_values("avg_variants", ascending=False)
    )

    # CONVERTING AVG TO INTEGER
    kpi_avg_variants_per_category["avg_variants"] = kpi_avg_variants_per_category[
        "avg_variants"
    ].round(0)

    fig_kpi_avg_variants_per_category = px.bar(
        kpi_avg_variants_per_category,
        x="category_name",
        y="avg_variants",
        title="Average Variants per Category",
        labels={"category_name": "Category", "avg_variants": "Average Variants"},
    )
    fig_kpi_avg_variants_per_category.update_layout(
        title={
            "text": "Average Variants per Category",
            "font": {"size": 25, "family": "Uber Move Medium", "color": "darkgrey"},
            "x": 0.5,
            "xanchor": "center",
        },
    )
    st.plotly_chart(fig_kpi_avg_variants_per_category, use_container_width=True)