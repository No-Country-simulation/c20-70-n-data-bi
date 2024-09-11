# Importaciones estándar
# import os
# import tempfile

# Importaciones de terceros
# from catboost import CatBoostClassifier
# import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Importaciones locales
# from streamlit_app.helpers.preprocessing import preprocessing_data
# from streamlit_app.helpers.sql_utils import append_new_data_to_db, db_conn
from helpers.utils import config_sidebar # extract_zip_to_csv, frauds_per_day, load_data_from_zip

# Ajustar el ancho para toda la pantalla 
st.set_page_config(page_title="Detección de Fraude", layout="wide")

# Configurar la barra lateral
codigo_acceso = config_sidebar()

# Verificación del código de acceso
if codigo_acceso == "1234":

    # Mostrar mensaje si el acceso es concedido
    # if st.session_state.access_granted:
    #     st.markdown("### Páginas disponibles:")
    #     st.markdown("- [Página 1](pagina1)")

    # Título de la página
    st.title("Detección de Fraude en Transacciones con Tarjetas de Crédito")

    # Obtener los datos de la DB
    n_transactions = 1852394
    n_frauds = 9651
    n_users = 999

    # Carga de datasets con el top 5 de fraudes
    top_5_fraud_merch = pd.read_csv('streamlit_app/top_5_fraud_merch.csv')
    top_5_fraud_city = pd.read_csv('streamlit_app/top_5_fraud_city.csv')
    top_5_fraud_state = pd.read_csv('streamlit_app/top_5_fraud_state.csv')

    # Renombrar columnas
    top_5_fraud_merch.columns = ['Vendedor', 'Fraude [%]', 'Fraudes [#]']
    top_5_fraud_city.columns = ['Ciudad', 'Fraude [%]', 'Fraudes [#]']
    top_5_fraud_state.columns = ['Estado', 'Fraude [%]', 'Fraudes [#]']

    # Crear tres columnas para cada top
    col_metrics, col_top_merch, col_top_city, col_top_state = st.columns([0.9, 2.5, 2, 2])

    # Mostrar dataframes en cada columna
    with col_metrics:
        st.subheader("Métricas")
        st.markdown(f'<p style="font-size:18px;">No. de Transacciones: <span style="color:green;">{n_transactions}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:18px;">No. de Fraudes: <span style="color:red;">{n_frauds}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:18px;">No. de Usuarios:<br> <span style="color:white;">{n_users}</span></p>', unsafe_allow_html=True)

    with col_top_merch:
        st.subheader("Vendedores con Fraude")
        st.dataframe(top_5_fraud_merch.set_index(top_5_fraud_merch.columns[0]))

    with col_top_city:
        st.subheader("Ciudades con Fraude")
        st.dataframe(top_5_fraud_city.set_index(top_5_fraud_city.columns[0]))

    with col_top_state:
        st.subheader("Estados con Fraude")
        st.dataframe(top_5_fraud_state.set_index(top_5_fraud_state.columns[0]))
    
    # # Extraer de la DB los fraudes por día
    # query_frauds_per_week = """
    # SELECT
    #     trans_date_trans_time,
    #     is_fraud
    # FROM
    #     public.transactions
    # WHERE
    #     is_fraud = 1;
    # """
    # global_frauds_per_day = pd.read_sql(query_frauds_per_week, db_conn())
    # global_frauds_per_day['trans_date_trans_time'] = pd.to_datetime(global_frauds_per_day['trans_date_trans_time'])
    # global_frauds_per_day.set_index('trans_date_trans_time', inplace=True)
    # global_frauds_per_day = global_frauds_per_day.resample('D').size().reset_index(name='total_transacciones')
    # global_frauds_per_day.set_index('trans_date_trans_time', inplace=True)

    # global_frauds_per_day.to_csv('./streamlit_app/global_frauds_per_day.csv')

    # # Convertir las fechas a formato español
    # global_frauds_per_day.index = global_frauds_per_day.index.strftime('%d %B %Y')  # Ejemplo: 01 abril 2019
    global_frauds_per_day = pd.read_csv('./streamlit_app/global_frauds_per_day.csv', index_col='trans_date_trans_time')
    #print(global_frauds_per_day.head())
    #global_frauds_per_day.set_index('trans_date_trans_time', inplace=True)
    #global_frauds_per_day.to_csv('./streamlit_app/global_frauds_per_day.csv', index=False)

    # Crear una figura de Plotly para la gráfica de línea
    fig = go.Figure()

    # Añadir una línea con las fechas y el número de fraudes
    fig.add_trace(go.Scatter(
        x=global_frauds_per_day.index, 
        y=global_frauds_per_day['total_transacciones'], 
        mode='lines', 
        #name='Número de Fraudes'
    ))

    # Añadir título y etiquetas a los ejes
    fig.update_layout(
        title="Línea Temporal de Fraudes por día",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Fraudes",
        template="plotly_white"
    )

    # Configurar el formato de fechas en el eje x
    fig.update_xaxes(
        tickformat="%d-%b-%Y",  # Formato en día-mes-año (ej. 01-Sep-2022)
        ticklabelmode="period"   # Muestra las etiquetas de las fechas en modo período
    )

    # Mostrar la gráfica en Streamlit
    st.plotly_chart(fig)
    del global_frauds_per_day
    # Mostrar el mensaje de éxito en la barra lateral
    #st.sidebar.success("¡Acceso concedido!")

    # # Sección desplegable 1: Carga de datos
    # with st.expander("Carga de archivos"):
    #     st.subheader("Carga los datos a predecir") 
    #     success_file, uploaded_file = load_data_from_zip()
    
    # # Verificar si la conexión ya está almacenada en session_state
    # if 'db_engine' not in st.session_state:
    #     st.session_state.db_engine = db_conn()

    # # Usar la conexión almacenada
    # engine = st.session_state.db_engine

#     # Si el archivo es correcto
#     if success_file:

#         # Crear un archivo temporal para extraer la data.
#         with tempfile.TemporaryDirectory() as temp_dir:
#             # Extraer el CSV en el archivo temporal
#             extracted_files = extract_zip_to_csv(uploaded_file, temp_dir)

#             # Extraer la ubicación del archivo
#             csv_file_path = os.path.join(temp_dir, extracted_files[0])

#             # Leer en pandas
#             df = pd.read_csv(csv_file_path)

#         # Extraer el CSV en el directorio actual
#         #extracted_files = extract_zip_to_csv(uploaded_file)

#         # Si solo hay 1 archivo CSV
#         if len(extracted_files) == 1:
#             # Obtener la ubicación del archivo
#             #csv_file_path = os.path.join(os.getcwd(), extracted_files[0])
#             del uploaded_file
#             try:
#                 # Sección desplegable 2: Análisis Exploratorio de los Datos
#                 with st.expander("Análisis Exploratorio de los Datos"):
#                     # Leer el archivo CSV
#                     #df = pd.read_csv(csv_file_path)

#                     # Previsualización del dataset
#                     st.subheader("Previsualización de datos")
#                     st.write("Primeras 5 filas del archivo:")
#                     st.dataframe(df.head().style.hide(axis="index"))        # Mostrar las primeras 5 filas
#                     st.write(f"Un total de {df.shape[0]} transacciones.")   # Mostrar la cantidad de transacciones

#                     # # Mostrar los porcentajes de fraude
#                     # st.subheader("Top 5 de Porcentajes de Fraude mas Altos")

#                     # # Carga de datasets con el top 5 de fraudes
#                     # top_5_fraud_merch = pd.read_csv('streamlit_app/top_5_fraud_merch.csv')
#                     # top_5_fraud_city = pd.read_csv('streamlit_app/top_5_fraud_city.csv')
#                     # top_5_fraud_state = pd.read_csv('streamlit_app/top_5_fraud_state.csv')

#                     # # Renombrar columnas
#                     # top_5_fraud_merch.columns = ['Vendedor', 'Fraude [%]', 'Fraudes [#]']
#                     # top_5_fraud_city.columns = ['Ciudad', 'Fraude [%]', 'Fraudes [#]']
#                     # top_5_fraud_state.columns = ['Estado', 'Fraude [%]', 'Fraudes [#]']

#                     # # Crear tres columnas para cada top
#                     # col_top_merch, col_top_city, col_top_state = st.columns(3)

#                     # # Mostrar dataframes en cada columna
#                     # with col_top_merch:
#                     #     st.subheader("Vendedores")
#                     #     st.dataframe(top_5_fraud_merch.set_index(top_5_fraud_merch.columns[0]))

#                     # with col_top_city:
#                     #     st.subheader("Ciudades")
#                     #     st.dataframe(top_5_fraud_city.set_index(top_5_fraud_city.columns[0]))

#                     # with col_top_state:
#                     #     st.subheader("Estados")
#                     #     st.dataframe(top_5_fraud_state.set_index(top_5_fraud_state.columns[0]))
                    
#                     # Calcular los fraudes por día
#                     st.subheader("Tendencia de Fraude")
#                     df_frauds_per_day = frauds_per_day(df)

#                     # Convertir la columna de fechas en datetime
#                     df_frauds_per_day['trans_date_trans_time'] = pd.to_datetime(df_frauds_per_day['trans_date_trans_time'])
#                     df_frauds_per_day.set_index('trans_date_trans_time', inplace=True)

#                     # Convertir las fechas a formato español
#                     df_frauds_per_day.index = df_frauds_per_day.index.strftime('%d %B %Y')  # Ejemplo: 01 abril 2019

#                     # Crear una figura de Plotly para la gráfica de línea
#                     fig = go.Figure()

#                     # Añadir una línea con las fechas y el número de fraudes
#                     fig.add_trace(go.Scatter(
#                         x=df_frauds_per_day.index, 
#                         y=df_frauds_per_day['total_transacciones'], 
#                         mode='lines', 
#                         name='Número de Fraudes'
#                     ))

#                     # Añadir título y etiquetas a los ejes
#                     fig.update_layout(
#                         title="Número de Fraudes por Día",
#                         xaxis_title="Fecha",
#                         yaxis_title="Número de Fraudes",
#                         template="plotly_white"
#                     )

#                     # Configurar el formato de fechas en el eje x
#                     fig.update_xaxes(
#                         tickformat="%d-%b-%Y",  # Formato en día-mes-año (ej. 01-Sep-2022)
#                         ticklabelmode="period"   # Muestra las etiquetas de las fechas en modo período
#                     )

#                     # Mostrar la gráfica en Streamlit
#                     st.plotly_chart(fig)
#                     del df_frauds_per_day
#                 # Sección desplegable 3: Transformación de datos
#                 with st.expander("Procesamiento de datos e ingeniería de características"):
#                     st.subheader("Transformación de datos para el modelo")

#                     # Crear un objeto temporal de loading data
#                     msg_transdata_loading = st.empty()
#                     msg_transdata_loading.write("Espere mientras se procesan los datos y se crean nuevas características...")

#                     # Procesar los datos
#                     data_clean = preprocessing_data(df)

#                     # Eliminar el objeto temporal de loading data
#                     msg_transdata_loading.empty() 

#                     # Dividir el conjunto en características y objetivo
#                     features = data_clean.drop("is_fraud", axis=1)
#                     target = data_clean["is_fraud"]
                    
#                     # Eliminar la data clean para ahorro de memoria
#                     del data_clean

#                     # Escalar las características
#                     cols_to_scale = ['amt', 'zip', 'city_pop', 'fraud_merch_pct', 'fraud_merch_rank', 
#                                         'fraud_city_pct', 'fraud_city_rank', 'fraud_state_pct', 'fraud_state_rank',
#                                         'job_encoded', 'trans_day', 'trans_month', 'trans_year', 'trans_hour', 
#                                         'trans_weekday', 'age', 'distance_to_merch']
#                     scaler = joblib.load("streamlit_app/scaler.pkl")                                # Cargar el escalador
#                     features_scaled = features.copy()                                               # Realizar una copia de las características
#                     features_scaled[cols_to_scale] = scaler.transform(features[cols_to_scale])      # Realizar la escala para columnas específicas
#                     features_scaled = pd.DataFrame(features_scaled, columns=features.columns)       # Retransformar en dataframe
#                     del features
#                     st.dataframe(features_scaled.head().style.hide(axis="index"))                   # Eliminar el index

#                 # Sección desplegable 4: Predicciones
#                 with st.expander("Predicciones de fraude con Catboost"):
#                     # Crear un objeto temporal para el mensaje de carga
#                     msg_ML_loading = st.empty()
                    
#                     # Cargar el modelol de machine learning
#                     msg_ML_loading.write("Aplicando el modelo de Machine Learning...")
#                     model = CatBoostClassifier()
#                     model.load_model('streamlit_app/catboost_bestmodel.cbm')
                    
#                     # Aplicar el modelo de machine learning a los datos
#                     predictions, accuracy, report = catboost_model(features_scaled, target, model)

#                     del model
#                     del features_scaled 
#                     del target 

#                     # Eliminar el objeto temporal para el mensaje de carga
#                     msg_ML_loading.empty() 

#                     # Crear 2 columnas para el reporte de métricas y para la visualización
#                     col_report, col_predicts, col_model_pct  = st.columns(3)

#                     # Columna de Reporte de métricas del modelo
#                     with col_report:
#                         st.subheader("Métricas del modelo")
#                         st.write(f"Precisión del modelo IA: **{accuracy * 100:.1f}%**")

#                         # Mostrar las transacciones seguras y fraudes
#                         fraud_trans_cnt = predictions.sum()
#                         trans_cnt = predictions.size
#                         safety_trans_cnt = trans_cnt - fraud_trans_cnt
#                         fraud_trans_pct = (fraud_trans_cnt / trans_cnt) * 100
#                         st.write(f"Se detectaron un total de **{fraud_trans_cnt} Fraudes** y **{safety_trans_cnt} Transacciones seguras**.")
#                         st.subheader("Reporte de Clasificación")
#                         st.dataframe(report)

#                     with col_predicts:
#                         # Mostrar las predicciones en formato CSV
#                         st.subheader("Predicciones en formato CSV")
#                         st.write("Este dataset contiene 2 columnas:")
#                         st.write("- trans_num: indicador del ID de la transacción.")
#                         st.write("- is_fraud: indicador de fraude: [0] para una transacción segura y [1] para fraude")
#                         predictions_df = pd.DataFrame(predictions, df["trans_num"])
#                         predictions_df.columns = ['is_fraud']
#                         st.dataframe(predictions_df)

#                     # Columna de la visualización para el porcentaje de farudes
#                     with col_model_pct:
#                         st.subheader(" Predicciones: Transacciones Seguras vs Fraudes")
#                         labels = ['Fraudes', 'Transacciones seguras']
#                         values = [fraud_trans_cnt, safety_trans_cnt]
#                         fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
#                         st.plotly_chart(fig)
                        


#                 # Sección desplegable 5: Carga a la base de datos
#                 with st.expander("Carga a la base de datos PostgreSQL"): 
#                     # Cargar la conexión a la DB
#                     #engine = db_conn()

#                     st.subheader("Creación de tablas relacionales")
                    
#                     # Crear la tabla users
#                     users = df[['cc_num', 'zip', 'first', 'last', 'gender', 'street', 'city', 'state', 'job', 'dob']].drop_duplicates()
#                     # Mostrar las primeras 5 filas
#                     st.write("Tabla: Usuarios [primeras 5 filas]")
#                     st.dataframe(users.head())
#                     # Cargar la tabla a la DB
#                     append_new_data_to_db(['cc_num'], 'users', users, engine)
#                     del users

#                     # Crear la tabla transactions
#                     transactions = df[['trans_date_trans_time', 'cc_num', 'merchant', 'category', 'amt', 'lat', 'long', 'trans_num', 'unix_time', 'is_fraud']].drop_duplicates()
#                     # Mostrar las primeras 5 filas
#                     st.write("Tabla: Transacciones [primeras 5 filas]")
#                     st.dataframe(transactions.head())                        
#                     # Cargar la tabla a la DB
#                     append_new_data_to_db(['trans_num'], 'transactions', transactions, engine)
#                     del transactions

#                     col_table_locations, col_table_merchants, col_table_predictions = st.columns([1, 1.25, 1])

#                     with col_table_locations: 
#                         # Crear la tabla locations
#                         locations = df[['city', 'state', 'city_pop']].drop_duplicates()
#                         # Mostrar las primeras 5 filas
#                         st.write("Tabla: Ubicaciones [primeras 5 filas]")
#                         st.dataframe(locations.head())
#                         # Cargar la tabla a la DB
#                         append_new_data_to_db(['city', 'state'], 'locations', locations, engine)
#                         del locations

#                     with col_table_merchants:
#                         # Crear la tabla merchants
#                         merchants = df[['merchant', 'merch_lat', 'merch_long']].drop_duplicates()
#                         # Mostrar las primeras 5 filas
#                         st.write("Tabla: Vendedores [primeras 5 filas]")
#                         st.dataframe(merchants.head())
#                         # Cargar la tabla a la DB
#                         append_new_data_to_db(['merchant'], 'merchants', merchants, engine)
#                         del merchants
#                         del df
#                     with col_table_predictions:
#                         # Mostrar las primeras 5 filas de predictions
#                         st.write("Tabla: Predicciones [primeras 5 filas]")
#                         st.dataframe(predictions_df.head())
#                         # Cargar la tabla a la DB
#                         append_new_data_to_db(['trans_num'], 'predictions', predictions_df.reset_index(), engine)
#                         predictions_df.to_sql('predictions', engine, if_exists='replace')
#                         del predictions_df
                    

#                     # Mensaje de éxito
#                     st.success("Las tablas han sido cargadas en la Base de datos.")

#             except Exception as e:
#                 st.error(f"Error al procesar el archivo CSV: {e}")

#         else:
#             st.error("El archivo .zip no contiene un archivo CSV válido o contiene múltiples archivos.")
                
# else:
#     if codigo_acceso != "":
#         st.error("Código incorrecto. Por favor, intenta nuevamente.")
    
#     # Bloqueo de contenido si el código es incorrecto
#     st.warning("Por favor, ingresa el código de acceso para ver el contenido.")
