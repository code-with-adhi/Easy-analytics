import streamlit as st
from utils import back_button, next_button, nav
from operations import TRANSFORM_OPS

def transform_menu():
    back_button("cleaning_menu")
    st.title("Data Transformation")
    n_cols = 3
    rows = [TRANSFORM_OPS[i:i + n_cols] for i in range(0, len(TRANSFORM_OPS), n_cols)]
    for row in rows:
        cols = st.columns(n_cols)
        for idx, btn in enumerate(row):
            if idx < len(row):
                with cols[idx]:
                    if st.button(btn, key=f"trans_{btn}"):
                        st.session_state.operation_set = btn
                        nav("operation")
    st.markdown("---")
    next_button("Next: Data Visualization", "visualize")