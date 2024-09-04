import streamlit as st
import pandas as pd
from preprocessing import preprocessing_data

# Ajustar el ancho para toda la patnalla 
st.set_page_config(page_title="Detección de Fraude", layout="wide")

st.title("Detección de Fraude en Transacciones con Tarjetas de Crédito")

# Crea dos columnas para la carga de archivos
col1_load_data, col2_load_data = st.columns(2)

# Permitir al usuario subir dos archivos CSV en columnas separadas
with col1_load_data:
    uploaded_file1 = st.file_uploader("Sube la primera parte del archivo CSV", type=["csv"], key="1")
    if uploaded_file1 is not None:
        data_pt1 = pd.read_csv(uploaded_file1)                      # Leer el primer dataframe
        st.write("Primer archivo cargado con éxito!")
        st.write("Primeras 5 filas del primer archivo:")
        st.dataframe(data_pt1.head(), use_container_width=True)     # Mostrar las primeras 5 filas

with col2_load_data:
    uploaded_file2 = st.file_uploader("Sube la segunda parte del archivo CSV", type=["csv"], key="2")
    if uploaded_file2 is not None:
        data_pt2 = pd.read_csv(uploaded_file2)                      # Leer el segundo dataframe
        st.write("Segundo archivo cargado con éxito!")
        st.write("Primeras 5 filas del segundo archivo:")
        st.dataframe(data_pt2.head(), use_container_width=True)     # Moostrar las primeras 5 filas

# Verificar si ambos archivos han sido subidos
if uploaded_file1 is not None and uploaded_file2 is not None:
    st.write("Procesando los datos combinados...")
    st.write("Mostrar las primeras 5 columnas de los datos procesados:")
    # Concatenar ambos DataFrames
    data = pd.concat([data_pt1, data_pt2], axis=0)

    # Preprocesar los datos para el modelo
    data_clean = preprocessing_data(data)

    # Muestra el DataFrame limpio
    st.dataframe(data_clean.head())