import streamlit as st
from utils import back_button, next_button, nav
from operations import CLEANING_OPS, OP_MAP

def cleaning_menu():
    back_button("upload")
    st.title("Data Cleaning")
    n_cols = 3
    rows = [CLEANING_OPS[i:i + n_cols] for i in range(0, len(CLEANING_OPS), n_cols)]
    for row in rows:
        cols = st.columns(n_cols)
        for idx, btn in enumerate(row):
            if idx < len(row):
                with cols[idx]:
                    if st.button(btn, key=f"clean_{btn}"):
                        st.session_state.operation_set = btn
                        nav("operation")
    st.markdown("---")
    next_button("Next: Data Transformation", "transform_menu")

def operation_page():
    from utils import enhanced_sanitize_dataframe_for_streamlit, safe_display_dataframe
    df = st.session_state.df.copy()
    op_group = st.session_state.operation_set
    back_button("cleaning_menu")
    st.title(op_group)
    if op_group not in OP_MAP:
        st.error("Operation not found!")
        return
    operations = OP_MAP[op_group]
    st.subheader("Select an operation:")
    for op_label, func in operations.items():
        if st.button(op_label, key=f"op_{op_label}"):
            try:
                with st.spinner(f"Applying {op_label}..."):
                    df_result = func(df)
                    df_result = enhanced_sanitize_dataframe_for_streamlit(df_result)
                    st.session_state.df = df_result
                    st.success(f" Operation '{op_label}' applied successfully!")
                    st.subheader("Updated Data Preview")
                    safe_display_dataframe(df_result.head())
                    if df_result.shape != df.shape:
                        st.info(f"Data shape changed: {df.shape} → {df_result.shape}")
            except Exception as e:
                st.error(f" Error applying operation: {str(e)}")