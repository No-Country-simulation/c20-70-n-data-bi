# Importaciones estándar
import os
import tempfile

# Importaciones de terceros
from catboost import CatBoostClassifier
import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Importaciones locales
from helpers.preprocessing import preprocessing_data
from helpers.utils import catboost_model, extract_zip_to_csv, frauds_per_day, load_data_from_zip

st.title("Página de Análisis")

# Verificar si el acceso ha sido concedido
if not st.session_state.get('access_granted', False):
    st.error("Acceso denegado. Por favor, ingresa el código de acceso en la barra lateral.")
    st.stop()

# Sección desplegable 1: Carga de datos
with st.expander("Carga de archivos"):
    st.subheader("Carga los datos a predecir") 
    success_file, uploaded_file = load_data_from_zip()

# Si el archivo es correcto
if success_file:

    # Crear un archivo temporal para extraer la data.
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extraer el CSV en el archivo temporal
        extracted_files = extract_zip_to_csv(uploaded_file, temp_dir)

        # Extraer la ubicación del archivo
        csv_file_path = os.path.join(temp_dir, extracted_files[0])

        # Leer en pandas
        df = pd.read_csv(csv_file_path)

        # Guardarlo en una variable multipagina
        st.session_state.data = df

    # Si solo hay 1 archivo CSV
    if len(extracted_files) == 1:
        # Eliminar el archivo .zip
        del uploaded_file
        try:
            # Sección desplegable 2: Análisis Exploratorio de los Datos
            with st.expander("Análisis Exploratorio de los Datos"):

                # Previsualización del dataset
                st.subheader("Previsualización de datos")
                st.write("Primeras 5 filas del archivo:")
                st.dataframe(df.head().style.hide(axis="index"))        # Mostrar las primeras 5 filas
                st.write(f"Un total de {df.shape[0]} transacciones.")   # Mostrar la cantidad de transacciones
                
                # Calcular los fraudes por día
                st.subheader("Tendencia de Fraude")
                df_frauds_per_day = frauds_per_day(df)

                # Convertir la columna de fechas en datetime
                df_frauds_per_day['trans_date_trans_time'] = pd.to_datetime(df_frauds_per_day['trans_date_trans_time'])
                df_frauds_per_day.set_index('trans_date_trans_time', inplace=True)

                # Convertir las fechas a formato español
                df_frauds_per_day.index = df_frauds_per_day.index.strftime('%d %B %Y')  # Ejemplo: 01 abril 2019

                # Crear una figura de Plotly para la gráfica de línea
                fig = go.Figure()

                # Añadir una línea con las fechas y el número de fraudes
                fig.add_trace(go.Scatter(
                    x=df_frauds_per_day.index, 
                    y=df_frauds_per_day['total_transacciones'], 
                    mode='lines', 
                    name='Número de Fraudes'
                ))

                # Añadir título y etiquetas a los ejes
                fig.update_layout(
                    title="Número de Fraudes por Día",
                    xaxis_title="Fecha",
                    yaxis_title="Número de Fraudes",
                    template="plotly_white"
                )

                # Configurar el formato de fechas en el eje x
                fig.update_xaxes(
                    tickformat="%d-%b-%Y",  # Formato en día-mes-año (ej. 01-Sep-2022)
                    ticklabelmode="period"   # Muestra las etiquetas de las fechas en modo período
                )

                # Mostrar la gráfica en Streamlit
                st.plotly_chart(fig)
                del df_frauds_per_day
            # Sección desplegable 3: Transformación de datos
            with st.expander("Procesamiento de datos e ingeniería de características"):
                st.subheader("Transformación de datos para el modelo")

                # Crear un objeto temporal de loading data
                msg_transdata_loading = st.empty()
                msg_transdata_loading.write("Espere mientras se procesan los datos y se crean nuevas características...")

                # Procesar los datos
                data_clean = preprocessing_data(df)

                # Eliminar el objeto temporal de loading data
                msg_transdata_loading.empty() 

                # Dividir el conjunto en características y objetivo
                features = data_clean.drop("is_fraud", axis=1)
                target = data_clean["is_fraud"]
                
                # Eliminar la data clean para ahorro de memoria
                del data_clean

                # Escalar las características
                cols_to_scale = ['amt', 'zip', 'city_pop', 'fraud_merch_pct', 'fraud_merch_rank', 
                                    'fraud_city_pct', 'fraud_city_rank', 'fraud_state_pct', 'fraud_state_rank',
                                    'job_encoded', 'trans_day', 'trans_month', 'trans_year', 'trans_hour', 
                                    'trans_weekday', 'age', 'distance_to_merch']
                scaler = joblib.load("streamlit_app/scaler.pkl")                                # Cargar el escalador
                features_scaled = features.copy()                                               # Realizar una copia de las características
                features_scaled[cols_to_scale] = scaler.transform(features[cols_to_scale])      # Realizar la escala para columnas específicas
                features_scaled = pd.DataFrame(features_scaled, columns=features.columns)       # Retransformar en dataframe
                del features
                st.dataframe(features_scaled.head().style.hide(axis="index"))                   # Eliminar el index

            # Sección desplegable 4: Predicciones
            with st.expander("Predicciones de fraude con Catboost"):
                # Crear un objeto temporal para el mensaje de carga
                msg_ML_loading = st.empty()
                
                # Cargar el modelol de machine learning
                msg_ML_loading.write("Aplicando el modelo de Machine Learning...")
                model = CatBoostClassifier()
                model.load_model('streamlit_app/catboost_bestmodel.cbm')
                
                # Aplicar el modelo de machine learning a los datos
                predictions, accuracy, report = catboost_model(features_scaled, target, model)

                del model
                del features_scaled 
                del target 

                # Eliminar el objeto temporal para el mensaje de carga
                msg_ML_loading.empty() 

                # Crear 2 columnas para el reporte de métricas y para la visualización
                col_report, col_predicts, col_model_pct  = st.columns(3)

                # Columna de Reporte de métricas del modelo
                with col_report:
                    st.subheader("Métricas del modelo")
                    st.write(f"Precisión del modelo IA: **{accuracy * 100:.1f}%**")

                    # Mostrar las transacciones seguras y fraudes
                    fraud_trans_cnt = predictions.sum()
                    trans_cnt = predictions.size
                    safety_trans_cnt = trans_cnt - fraud_trans_cnt
                    fraud_trans_pct = (fraud_trans_cnt / trans_cnt) * 100
                    st.write(f"Se detectaron un total de **{fraud_trans_cnt} Fraudes** y **{safety_trans_cnt} Transacciones seguras**.")
                    st.subheader("Reporte de Clasificación")
                    st.dataframe(report)

                with col_predicts:
                    # Mostrar las predicciones en formato CSV
                    st.subheader("Predicciones en formato CSV")
                    st.write("Este dataset contiene 2 columnas:")
                    st.write("- trans_num: indicador del ID de la transacción.")
                    st.write("- is_fraud: indicador de fraude: [0] para una transacción segura y [1] para fraude")
                    predictions_df = pd.DataFrame(predictions, df["trans_num"])
                    predictions_df.columns = ['is_fraud']
                    st.dataframe(predictions_df)
                    # Guardarlo en una variable multipagina
                    st.session_state.predicts = predictions_df
                # Columna de la visualización para el porcentaje de farudes
                with col_model_pct:
                    st.subheader(" Predicciones: Transacciones Seguras vs Fraudes")
                    labels = ['Fraudes', 'Transacciones seguras']
                    values = [fraud_trans_cnt, safety_trans_cnt]
                    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
                    st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Error al procesar el archivo CSV: {e}")

    else:
        st.error("El archivo .zip no contiene un archivo CSV válido o contiene múltiples archivos.")