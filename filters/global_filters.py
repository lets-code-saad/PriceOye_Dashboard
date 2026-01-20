import streamlit as st


def global_filter(base_df):
    filtered_df = base_df.copy()

    # RATING FILTER
    min_value, max_value = st.session_state.get("slider_range", (2.0, 5.0))
    filtered_df = filtered_df[
        (filtered_df["rating"] >= min_value) & (filtered_df["rating"] <= max_value)
    ]

    # CATEGORY FILTER
    selected_categories = st.session_state.get("selected_category_names", [])
    if selected_categories:
        filtered_df = filtered_df[filtered_df["category_name"].isin(selected_categories)]
        
        
    return filtered_df
