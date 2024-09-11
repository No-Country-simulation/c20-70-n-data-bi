# Importaciones estándar
#import os
#import tempfile

# Importaciones de terceros
#from catboost import CatBoostClassifier
#import joblib
#import pandas as pd
#import plotly.graph_objects as go
import streamlit as st

# Importaciones locales
#from streamlit_app.helpers.preprocessing import preprocessing_data
from streamlit_app.helpers.sql_utils import append_new_data_to_db, db_conn
#from streamlit_app.helpers.utils import catboost_model, extract_zip_to_csv, frauds_per_day, load_data_from_zip


st.subheader("Creación de tablas relacionales")

# Verificar si la conexión ya está almacenada en session_state
if 'db_engine' not in st.session_state:
    st.session_state.db_engine = db_conn()

# Usar la conexión almacenada
engine = st.session_state.db_engine

df = st.session_state.data
# Crear la tabla users
users = df[['cc_num', 'zip', 'first', 'last', 'gender', 'street', 'city', 'state', 'job', 'dob']].drop_duplicates()
# Mostrar las primeras 5 filas
st.write("Tabla: Usuarios [primeras 5 filas]")
st.dataframe(users.head())
# Cargar la tabla a la DB
append_new_data_to_db(['cc_num'], 'users', users, engine)
del users

# Crear la tabla transactions
transactions = df[['trans_date_trans_time', 'cc_num', 'merchant', 'category', 'amt', 'lat', 'long', 'trans_num', 'unix_time', 'is_fraud']].drop_duplicates()
# Mostrar las primeras 5 filas
st.write("Tabla: Transacciones [primeras 5 filas]")
st.dataframe(transactions.head())                        
# Cargar la tabla a la DB
append_new_data_to_db(['trans_num'], 'transactions', transactions, engine)
del transactions

col_table_locations, col_table_merchants, col_table_predictions = st.columns([1, 1.25, 1])

with col_table_locations: 
    # Crear la tabla locations
    locations = df[['city', 'state', 'city_pop']].drop_duplicates()
    # Mostrar las primeras 5 filas
    st.write("Tabla: Ubicaciones [primeras 5 filas]")
    st.dataframe(locations.head())
    # Cargar la tabla a la DB
    append_new_data_to_db(['city', 'state'], 'locations', locations, engine)
    del locations

with col_table_merchants:
    # Crear la tabla merchants
    merchants = df[['merchant', 'merch_lat', 'merch_long']].drop_duplicates()
    # Mostrar las primeras 5 filas
    st.write("Tabla: Vendedores [primeras 5 filas]")
    st.dataframe(merchants.head())
    # Cargar la tabla a la DB
    append_new_data_to_db(['merchant'], 'merchants', merchants, engine)
    del merchants
    del df
with col_table_predictions:
    # Mostrar las primeras 5 filas de predictions
    st.write("Tabla: Predicciones [primeras 5 filas]")
    predictions_df = st.session_state.predicts
    st.dataframe(predictions_df.head())
    # Cargar la tabla a la DB
    append_new_data_to_db(['trans_num'], 'predictions', predictions_df.reset_index(), engine)
    predictions_df.to_sql('predictions', engine, if_exists='replace')
    del predictions_df


# Mensaje de éxito
st.success("Las tablas han sido cargadas en la Base de datos.")