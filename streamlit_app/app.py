import os
import streamlit as st
import pandas as pd
from preprocessing import preprocessing_data
from utils import catboost_model, extract_zip_to_csv, extract_zip_to_model
import tempfile
import joblib
from sklearn.metrics import accuracy_score, classification_report
import plotly.graph_objects as go

# Ajustar el ancho para toda la pantalla 
st.set_page_config(page_title="Detección de Fraude", layout="wide")

st.title("Detección de Fraude en Transacciones con Tarjetas de Crédito")

# Subir el archivo .zip
uploaded_file = st.file_uploader("Sube tu archivo CSV en formato .zip", type=["zip"], key="1")

# Si el archivo no esta vacío continua...
if uploaded_file is not None:
    st.write("Archivo subido con éxito!")
    
    # Crear un archivo temporal para guardar el archivo
    with tempfile.TemporaryDirectory() as temp_dir:
        # Buscar archivos CSV en el directorio temporal
        extracted_files = extract_zip_to_csv(uploaded_file, temp_dir)

        if len(extracted_files) == 1:
            csv_file_path = os.path.join(temp_dir, extracted_files[0])

            # Leer el archivo CSV completo (o parte del mismo si es muy grande)
            try:
                # Cargar el dataframe
                df = pd.read_csv(csv_file_path)
                
                # Mostrar solo las primeras 5 filas del archivo CSV
                st.subheader("Prevista del archivo")
                st.write("Mostrando las primeras 5 filas del archivo:")
                st.dataframe(df.head())

                # Procesar los datos y mostrar las primeras 5 filas
                st.subheader("Procesamiento de datos, ingenieria de características y preparación de datos")
                st.write("Procesando los datos...")
                st.write("Creando nuevas características...")
                data_clean = preprocessing_data(df)

                # Dividir el dataset en características y target
                features = data_clean.drop("is_fraud", axis=1)
                target = data_clean["is_fraud"]

                # Escalar las características
                cols_to_scale=['amt', 'zip', 'city_pop', 'fraud_merch_pct', 'fraud_merch_rank', 
                               'fraud_city_pct', 'fraud_city_rank', 'fraud_state_pct', 'fraud_state_rank',
                               'job_encoded', 'trans_day', 'trans_month', 'trans_year', 'trans_hour', 
                               'trans_weekday', 'age', 'distance_to_merch']
                st.write("Escalando los datos...")
                scaler = joblib.load("streamlit_app/scaler.pkl") # Cargar el escalador de datos éstandar
                features_scaled = features.copy()
                features_scaled[cols_to_scale] = scaler.transform(features[cols_to_scale])

                # Convertir a DataFrame después de escalar
                features_scaled = pd.DataFrame(features_scaled, columns=features.columns)

                # Muestra el DataFrame limpio
                st.write("Mostrando las primeras 5 filas del archivo procesado:")
                st.dataframe(features_scaled.head())

                # Aplicar el modelo Catboost
                st.subheader("Predicciones de fraude con Catboost")
                model = extract_zip_to_model("streamlit_app/catboost_model_2.zip", "catboost_model_2.cbm")        # Extraer el modelo.zip

                predictions, accuracy, report = catboost_model(features_scaled, target, model)

                # Calcular las predicciones seguras y las de fraude
                fraud_trans_cnt = predictions.sum()
                trans_cnt = predictions.size
                safety_trans_cnt = trans_cnt - fraud_trans_cnt
                fraud_trans_pct = (fraud_trans_cnt / trans_cnt) * 100
                print(f'Cantidad de fraudes: {fraud_trans_cnt}')
                print(f'Cantidad de transacciones: {trans_cnt}')
                print(f'Porcentaje de fraudes {fraud_trans_pct:.2f}%')
                
                st.subheader("Transaccionoes Seguras vs Fraudes")
                # Datos para el gráfico de dona
                labels = ['Fraudes', 'Transacciones seguras']
                values = [fraud_trans_cnt, safety_trans_cnt]

                # Crear gráfico de dona usando Plotly
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
                # Mostrar gráfico
                st.plotly_chart(fig)

                # Mostrar los valores contados
                st.write(f"Cantidad de Fraudes: {fraud_trans_cnt}")
                st.write(f"Cantidad de Transacciones seguras: {safety_trans_cnt}")

            except Exception as e:
                st.error(f"Error al procesar el archivo CSV: {e}")
        else:
            st.error("El archivo .zip no contiene un archivo CSV válido o contiene múltiples archivos.")