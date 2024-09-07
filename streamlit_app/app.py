import os
import streamlit as st
import pandas as pd
from preprocessing import preprocessing_data
from utils import catboost_model, extract_zip_to_csv, frauds_per_day
import tempfile
import joblib
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
                        # Motrar 5 filas del dataset cargado
                        st.subheader("Previsualización de datos")
                        st.write("Primeras 5 filas del archivo:")
                        st.dataframe(df.head().style.hide(axis="index"))
                        # Mostrar la cantidad de transacciones
                        st.write(f"Un total de {df.shape[0]} transacciones.")

                        st.subheader("Top 5 de Porcentajes de Fraude mas Altos")
                        # Carga de datasets de con los top en fraude
                        top_5_fraud_merch = pd.read_csv('streamlit_app/top_5_fraud_merch.csv')
                        top_5_fraud_city = pd.read_csv('streamlit_app/top_5_fraud_city.csv')
                        top_5_fraud_state = pd.read_csv('streamlit_app/top_5_fraud_state.csv')

                        # Renombrar columnas
                        top_5_fraud_merch.columns = ['Vendedor', 'Fraude [%]', 'Fraudes [#]']
                        top_5_fraud_city.columns = ['Ciudad', 'Fraude [%]', 'Fraudes [#]']
                        top_5_fraud_state.columns = ['Estado', 'Fraude [%]', 'Fraudes [#]']

                        # Crear tres columnas para cada top
                        col_top_merch, col_top_city, col_top_state = st.columns(3)

                        # Mostrar dataframes en cada columna
                        with col_top_merch:
                            st.subheader("Vendedores")
                            st.dataframe(top_5_fraud_merch.set_index(top_5_fraud_merch.columns[0]))

                        with col_top_city:
                            st.subheader("Ciudades")
                            st.dataframe(top_5_fraud_city.set_index(top_5_fraud_city.columns[0]))

                        with col_top_state:
                            st.subheader("Estados")
                            st.dataframe(top_5_fraud_state.set_index(top_5_fraud_state.columns[0]))
                        
                        # Calcular los fraudes por día
                        st.subheader("Tendencia de Fraude")
                        df_frauds_per_day = frauds_per_day(df, 'trans_date_trans_time')

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
                        st.dataframe(features_scaled.head().style.hide(axis="index"))

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
