import os
import streamlit as st
import pandas as pd
from preprocessing import preprocessing_data
from utils import catboost_model, extract_zip_to_csv, extract_zip_to_model
import tempfile
import joblib
from sklearn.metrics import accuracy_score, classification_report
import plotly.graph_objects as go
from catboost import CatBoostClassifier

# Ajustar el ancho para toda la pantalla 
st.set_page_config(page_title="Detección de Fraude", layout="wide")

# Mostrar la imagen
image_path = "./streamlit_app/logo.png"
st.sidebar.image(image_path, use_column_width='auto')

st.title("Detección de Fraude en Transacciones con Tarjetas de Crédito")

# Descripción del proyecto en la barra lateral
st.sidebar.title("Descripción del Proyecto")
st.sidebar.write("""
Este proyecto tiene como objetivo realizar predicciones de fraudes en transacciones con tarjeta de credito y llevar a cabo un Análisis Exploratorio de los Datos.
                 \n
Por favor, ingresa el código de acceso para continuar.
""")

# Solicitar el código de acceso
codigo_acceso = st.sidebar.text_input("Ingresa el código de acceso", type="password")

# Verificación del código de acceso
if codigo_acceso == "1":
    # Mostrar el mensaje de éxito en la barra lateral
    st.sidebar.success("¡Acceso concedido!")

    # Crear secciones desplegables (subheaders) no anidadas
    with st.expander("Carga de archivos"):
        success_file = False
        st.subheader("Carga tus archivos")    
        # Subir el archivo .zip
        uploaded_file = st.file_uploader("Sube tu archivo CSV en formato .zip", type=["zip"], key="1")
        if uploaded_file is not None:
            st.success("Archivo subido con éxito!")
            success_file = True
        else:
            st.warning("Por favor ingrese un archivo")
    
    if success_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Buscar archivos CSV en el directorio temporal
            extracted_files = extract_zip_to_csv(uploaded_file, temp_dir)

            if len(extracted_files) == 1:
                csv_file_path = os.path.join(temp_dir, extracted_files[0])

                try:
                    # Leer el archivo CSV
                    df = pd.read_csv(csv_file_path)
                    
                    # Expanders independientes
                    with st.expander("Análisis Exploratorio de los Datos"):
                        st.subheader("Previsualización de datos")
                        st.write("Primeras 5 filas del archivo:")
                        st.dataframe(df.head())
                        st.subheader("Top 5 Vendedores/Ciudades/Estados con mas porcentaje de fraudes")

                        # Carga de datasets de con los top en fraude
                        top_5_fraud_merch = pd.read_csv('streamlit_app/top_5_fraud_merch.csv')
                        top_5_fraud_city = pd.read_csv('streamlit_app/top_5_fraud_city.csv')
                        top_5_fraud_state = pd.read_csv('streamlit_app/top_5_fraud_state.csv')

                        # Crear tres columnas para cada top
                        col_top_merch, col_top_city, col_top_state = st.columns(3)

                        # Mostrar dataframes en cada columna
                        with col_top_merch:
                            st.subheader("Vendedores")
                            st.dataframe(top_5_fraud_merch)

                        with col_top_city:
                            st.subheader("Ciudades")
                            st.dataframe(top_5_fraud_city)

                        with col_top_state:
                            st.subheader("Estados")
                            st.dataframe(top_5_fraud_state)

                    with st.expander("Procesamiento de datos e ingeniería de características"):
                        st.write("Procesando los datos y creando nuevas características...")
                        data_clean = preprocessing_data(df)
                        features = data_clean.drop("is_fraud", axis=1)
                        target = data_clean["is_fraud"]
                        
                        # Escalar las características
                        st.write("Escalando los datos...")
                        cols_to_scale = ['amt', 'zip', 'city_pop', 'fraud_merch_pct', 'fraud_merch_rank', 
                                         'fraud_city_pct', 'fraud_city_rank', 'fraud_state_pct', 'fraud_state_rank',
                                         'job_encoded', 'trans_day', 'trans_month', 'trans_year', 'trans_hour', 
                                         'trans_weekday', 'age', 'distance_to_merch']
                        scaler = joblib.load("streamlit_app/scaler.pkl")  # Cargar el escalador
                        features_scaled = features.copy()
                        features_scaled[cols_to_scale] = scaler.transform(features[cols_to_scale])
                        features_scaled = pd.DataFrame(features_scaled, columns=features.columns)
                        st.dataframe(features_scaled.head())

                    with st.expander("Predicciones de fraude con Catboost"):
                        st.write("Aplicando el modelo Catboost para predecir fraudes...")
                        model = CatBoostClassifier()
                        model.load_model('streamlit_app/catboost_bestmodel.cbm')
                        st.write("Modelo cargado.")
                        
                        predictions, accuracy, report = catboost_model(features_scaled, target, model)

                        st.write(f"Exactitud: {accuracy:.2f}")
                        st.write("Informe de clasificación:")
                        st.text(report)

                        # Calcular las transacciones seguras vs fraudes
                        fraud_trans_cnt = predictions.sum()
                        trans_cnt = predictions.size
                        safety_trans_cnt = trans_cnt - fraud_trans_cnt
                        fraud_trans_pct = (fraud_trans_cnt / trans_cnt) * 100
                        
                        st.subheader("Transacciones Seguras vs Fraudes")
                        labels = ['Fraudes', 'Transacciones seguras']
                        values = [fraud_trans_cnt, safety_trans_cnt]
                        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
                        st.plotly_chart(fig)
                        st.write(f"Cantidad de Fraudes: {fraud_trans_cnt}")
                        st.write(f"Cantidad de Transacciones seguras: {safety_trans_cnt}")

                except Exception as e:
                    st.error(f"Error al procesar el archivo CSV: {e}")
            else:
                st.error("El archivo .zip no contiene un archivo CSV válido o contiene múltiples archivos.")
else:
    if codigo_acceso != "":
        st.error("Código incorrecto. Por favor, intenta nuevamente.")
    
    # Bloqueo de contenido si el código es incorrecto
    st.warning("Por favor, ingresa el código de acceso para ver el contenido.")
