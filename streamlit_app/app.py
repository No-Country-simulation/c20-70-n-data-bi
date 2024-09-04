import os
import streamlit as st
import pandas as pd
from preprocessing import preprocessing_data
from utils import extract_csv_from_zip

# Ajustar el ancho para toda la pantalla 
st.set_page_config(page_title="Detección de Fraude", layout="wide")

st.title("Detección de Fraude en Transacciones con Tarjetas de Crédito")

# uploaded_file = st.file_uploader("Sube la primera parte del archivo CSV", type=["csv"], key="1")
uploaded_file = st.file_uploader("Sube tu archivo CSV en formato .zip", type=["zip"], key="1")

if uploaded_file is not None:
    st.write("Archivo subido con éxito!")

    # Extraer el archivo .zip
    data = extract_csv_from_zip(uploaded_file)

    # Lista los archivos extraídos
    #extracted_files = os.listdir(temp_dir)

    if data is not None:
        # Mostrar los datos del CSV
        st.dataframe(data.head())
    else:
        st.error("El archivo .zip no contiene un archivo CSV válido o contiene múltiples archivos.")



# if uploaded_file is not None:
#     data = pd.read_csv(uploaded_file)                      # Leer el primer dataframe
#     st.write("Primer archivo cargado con éxito!")
#     st.write("Primeras 5 filas del primer archivo:")
#     st.dataframe(data.head(5), use_container_width=True)     # Mostrar las primeras 3 filas
#     st.write("Procesando datos...")
#     st.write("Primeras 5 filas de los datos procesados: ")
#     # Preprocesar los datos para el modelo
#     data_clean = preprocessing_data(data)

#     # Muestra el DataFrame limpio
#     st.dataframe(data_clean.head())

# Crea 4 columnas para la carga de archivos
# col1_load_data, col2_load_data = st.columns(2)

# Permitir al usuario subir cuatro archivos CSV en columnas separadas
# with col1_load_data:
#     uploaded_file1 = st.file_uploader("Sube la primera parte del archivo CSV", type=["csv"], key="1")
#     if uploaded_file1 is not None:
#         data_pt1 = pd.read_csv(uploaded_file1)                      # Leer el primer dataframe
#         st.write("Primer archivo cargado con éxito!")
#         st.write("Primeras 3 filas del primer archivo:")
#         st.dataframe(data_pt1.head(3), use_container_width=True)     # Mostrar las primeras 3 filas

#     uploaded_file3 = st.file_uploader("Sube la tercera parte del archivo CSV", type=["csv"], key="3")
#     if uploaded_file3 is not None:
#         data_pt3 = pd.read_csv(uploaded_file3)                      # Leer el tercer dataframe
#         st.write("Tercer archivo cargado con éxito!")
#         st.write("Primeras 3 filas del tercer archivo:")
#         st.dataframe(data_pt3.head(3), use_container_width=True)     # Mostrar las primeras 3 filas

# with col2_load_data:
#     uploaded_file2 = st.file_uploader("Sube la segunda parte del archivo CSV", type=["csv"], key="2")
#     if uploaded_file2 is not None:
#         data_pt2 = pd.read_csv(uploaded_file2)                      # Leer el segundo dataframe
#         st.write("Segundo archivo cargado con éxito!")
#         st.write("Primeras 3 filas del segundo archivo:")
#         st.dataframe(data_pt2.head(3), use_container_width=True)     # Moostrar las primeras 3 filas

#     uploaded_file4 = st.file_uploader("Sube la cuarta parte del archivo CSV", type=["csv"], key="4")
#     if uploaded_file4 is not None:
#         data_pt4 = pd.read_csv(uploaded_file4)                      # Leer el cuarto dataframe
#         st.write("Cuarto archivo cargado con éxito!")
#         st.write("Primeras 3 filas del cuarto archivo:")
#         st.dataframe(data_pt4.head(3), use_container_width=True)     # Moostrar las primeras 3 filas


# Verificar si ambos archivos han sido subidos
# if uploaded_file1:
#     st.write("Procesando los datos combinados...")
#     st.write("Mostrar las primeras 5 columnas de los datos procesados:")
#     # Concatenar ambos DataFrames
#     data = pd.concat([data_pt1, data_pt2, data_pt3, data_pt4], axis=0)

#     # Preprocesar los datos para el modelo
#     data_clean = preprocessing_data(data)

#     # Muestra el DataFrame limpio
#     st.dataframe(data_clean.head())