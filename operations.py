import pandas as pd
import streamlit as st
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from utils import enhanced_sanitize_dataframe_for_streamlit

def handle_missing_values(df, method):
    """Handle missing values with Arrow-compatible output"""
    if method == "isnull":
        result = df.isnull()
    elif method == "isnull_sum":
        result = pd.DataFrame(df.isnull().sum(), columns=['Missing_Count'])
    elif method == "notnull":
        result = df.notnull()
    else:
        result = df
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

def remove_missing_values(df, method='default', **kwargs):
    """Remove missing values with different strategies"""
    if method == 'default':
        result = df.dropna()
    elif method == 'axis1':
        result = df.dropna(axis=1)
    elif method == 'all':
        result = df.dropna(how='all')
    elif method == 'thresh':
        result = df.dropna(thresh=kwargs.get('thresh', 2))
    else:
        result = df
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

def fill_missing_values(df, method='zero', value=None):
    """Fill missing values with Arrow-compatible types"""
    if method == 'zero':
        result = df.fillna(0)
    elif method == 'ffill':
        result = df.ffill()
    elif method == 'bfill':
        result = df.bfill()
    elif method == 'mean':
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        result = df.copy()
        for col in numeric_cols:
            result[col] = result[col].fillna(result[col].mean())
    elif method == 'unknown':
        result = df.fillna("Unknown")
    else:
        result = df
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

def string_operations(df, operation):
    """Perform string operations on object columns"""
    result = df.copy()
    string_cols = df.select_dtypes(include=['object']).columns
    
    if operation == 'lower':
        for col in string_cols:
            result[col] = result[col].astype(str).str.lower()
    elif operation == 'upper':
        for col in string_cols:
            result[col] = result[col].astype(str).str.upper()
    elif operation == 'strip':
        for col in string_cols:
            result[col] = result[col].astype(str).str.strip()
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

def data_type_operations(df, operation):
    """Perform data type conversions"""
    result = df.copy()
    
    if operation == 'fix_numeric':
        for col in result.columns:
            if result[col].dtype == 'object':
                try:
                    numeric_col = pd.to_numeric(result[col], errors='ignore')
                    if not numeric_col.equals(result[col]):
                        result[col] = numeric_col
                except:
                    pass
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

def categorical_operations(df, operation):
    """Handle categorical data operations"""
    result = df.copy()
    
    if operation == 'to_category':
        string_cols = result.select_dtypes(include=['object']).columns
        for col in string_cols:
            result[col] = result[col].astype('category')
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

def math_transformations(df, operation):
    """Apply mathematical transformations"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if operation == 'log':
        result = numeric_df.apply(lambda x: np.log(x + 1))
    elif operation == 'sqrt':
        result = numeric_df.apply(lambda x: np.sqrt(x.abs()))
    elif operation == 'square':
        result = numeric_df ** 2
    else:
        result = numeric_df
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

def scaling_operations(df, method):
    """Apply feature scaling"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        st.warning("No numeric columns found for scaling.")
        return enhanced_sanitize_dataframe_for_streamlit(df)
    
    if method == 'minmax':
        scaler = MinMaxScaler()
    else:  # standardscaler
        scaler = StandardScaler()
    
    scaled_data = scaler.fit_transform(numeric_df)
    result = pd.DataFrame(scaled_data, columns=numeric_df.columns, index=numeric_df.index)
    
    return enhanced_sanitize_dataframe_for_streamlit(result)

CLEANING_OPS = [
    "Handling Missing Values", "Removing Missing Values", "Filling Missing Values",
    "Removing Duplicates", "Renaming Columns", "Fixing Data Types",
    "String Cleaning", "Handling Categorical Data", "Replacing Values"
]

TRANSFORM_OPS = [
    "Mathematical Transformations", "Feature Scaling", "Encoding Categorical Variables",
    "Discretization Binning", "Datetime Transformation", "Column Operations",
    "String Transformations"
]

OP_MAP = {
    "Handling Missing Values": {
        "Show Missing Values (.isnull())": lambda df: handle_missing_values(df, "isnull"),
        "Count Missing Values (.isnull().sum())": lambda df: handle_missing_values(df, "isnull_sum"),
        "Show Non-Missing (.notnull())": lambda df: handle_missing_values(df, "notnull"),
    },
    "Removing Missing Values": {
        "Drop All Missing (.dropna())": lambda df: remove_missing_values(df, 'default'),
        "Drop Empty Columns (.dropna(axis=1))": lambda df: remove_missing_values(df, 'axis1'),
        "Drop All-Missing Rows (.dropna(how='all'))": lambda df: remove_missing_values(df, 'all'),
        "Drop if <2 Values (.dropna(thresh=2))": lambda df: remove_missing_values(df, 'thresh', thresh=2),
    },
    "Filling Missing Values": {
        "Fill with 0 (.fillna(0))": lambda df: fill_missing_values(df, 'zero'),
        "Forward Fill (.ffill())": lambda df: fill_missing_values(df, 'ffill'),
        "Backward Fill (.bfill())": lambda df: fill_missing_values(df, 'bfill'),
        "Fill with Mean": lambda df: fill_missing_values(df, 'mean'),
        "Fill with 'Unknown'": lambda df: fill_missing_values(df, 'unknown'),
    },
    "Removing Duplicates": {
        "Show Duplicates (.duplicated())": lambda df: enhanced_sanitize_dataframe_for_streamlit(df[df.duplicated()]),
        "Remove Duplicates (.drop_duplicates())": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.drop_duplicates()),
    },
    "Renaming Columns": {
        "View Current Column Names": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.DataFrame(list(df.columns), columns=['Column_Names'])),
        "Lowercase Column Names": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.rename(columns={col: col.lower() for col in df.columns})),
        "Remove Spaces from Columns": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.rename(columns={col: col.replace(' ', '_') for col in df.columns})),
    },
    "Fixing Data Types": {
        "Auto-Fix Numeric Types": lambda df: data_type_operations(df, 'fix_numeric'),
        "View Data Types": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.DataFrame(df.dtypes, columns=['Data_Type'])),
    },
    "String Cleaning": {
        "Convert to Lowercase": lambda df: string_operations(df, 'lower'),
        "Convert to Uppercase": lambda df: string_operations(df, 'upper'),
        "Strip Whitespace": lambda df: string_operations(df, 'strip'),
    },
    "Handling Categorical Data": {
        "Convert to Category": lambda df: categorical_operations(df, 'to_category'),
        "View Unique Values": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.DataFrame([f"{col}: {df[col].nunique()} unique" for col in df.columns], columns=['Unique_Counts'])),
    },
    "Replacing Values": {
        "Replace Zero with NaN": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.replace(0, np.nan)),
        "Replace Negative with NaN": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.applymap(lambda x: np.nan if (isinstance(x, (int, float)) and x < 0) else x)),
    },
    "Mathematical Transformations": {
        "Log Transform": lambda df: math_transformations(df, 'log'),
        "Square Root Transform": lambda df: math_transformations(df, 'sqrt'),
        "Square Transform": lambda df: math_transformations(df, 'square'),
    },
    "Feature Scaling": {
        "Min-Max Scaling": lambda df: scaling_operations(df, 'minmax'),
        "Standard Scaling (Z-score)": lambda df: scaling_operations(df, 'standard'),
    },
    "Encoding Categorical Variables": {
        "Label Encoding": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.select_dtypes(include=['object', 'category']).apply(lambda x: pd.Categorical(x).codes)),
        "One-Hot Encoding": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.get_dummies(df, prefix_sep='_')),
    },
    "Discretization Binning": {
        "Equal-Width Binning": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.select_dtypes(include=[np.number]).apply(lambda x: pd.cut(x, bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']))),
        "Quantile Binning": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.select_dtypes(include=[np.number]).apply(lambda x: pd.qcut(x, q=4, labels=['Q1', 'Q2', 'Q3', 'Q4']))),
    },
    "Column Operations": {
        "Add Row Index": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.reset_index()),
        "Remove Index": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.reset_index(drop=True)),
    },
    "String Transformations": {
        "Extract String Length": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.select_dtypes(include=['object']).apply(lambda x: x.astype(str).str.len())),
        "Extract First Character": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.select_dtypes(include=['object']).apply(lambda x: x.astype(str).str[0])),
    },
    "Datetime Transformation": {
        "Parse Dates": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.select_dtypes(include=['object']).apply(pd.to_datetime, errors='ignore')),
        "Extract Date Components": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.select_dtypes(include=['datetime64']).apply(lambda x: pd.DataFrame({'year': x.dt.year, 'month': x.dt.month, 'day': x.dt.day}))),
    }
}
