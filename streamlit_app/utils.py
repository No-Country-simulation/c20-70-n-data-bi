# Librerias estandar
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import List
import os
import zipfile
# Librearias de 3ros
from sklearn.metrics import accuracy_score, classification_report
from sqlalchemy import create_engine
import joblib
import pandas as pd
import streamlit as st

def calc_pct_n_rank(
    data: pd.DataFrame,
    group_merch_path: str = 'streamlit_app/group_fraud_by_merch.csv',
    group_city_path: str = 'streamlit_app/group_fraud_by_city.csv',
    group_state_path: str = 'streamlit_app/group_fraud_by_state.csv',
    merch_col_name: str = 'merchant',
    city_col_name: str = 'city',
    state_col_name: str = 'state',
    fraud_merch_pct_name: str = 'fraud_merch_pct',
    fraud_city_pct_name: str = 'fraud_city_pct',
    fraud_state_pct_name: str = 'fraud_state_pct',
    fraud_merch_rank_name: str = 'fraud_merch_rank',
    fraud_city_rank_name: str = 'fraud_city_rank',
    fraud_state_rank_name: str = 'fraud_state_rank'
) -> pd.DataFrame:
    """
    Calcula el porcentaje de fraude y el ranking para diferentes grupos (merch, ciudad, estado) y los añade al DataFrame original.

    Parámetros:
    - data: DataFrame principal al que se le añadirán las columnas de porcentaje de fraude y ranking.
    - group_merch_path: Ruta al archivo CSV que contiene los datos de fraude por vendedor.
    - group_city_path: Ruta al archivo CSV que contiene los datos de fraude por ciudad.
    - group_state_path: Ruta al archivo CSV que contiene los datos de fraude por estado.
    - merch_col_name: Nombre de la columna que identifica a los vendedores en los datos de fraude.
    - city_col_name: Nombre de la columna que identifica las ciudades en los datos de fraude.
    - state_col_name: Nombre de la columna que identifica los estados en los datos de fraude.
    - fraud_merch_pct_name: Nombre de la columna que se le asigna al porcentaje de fraude por vendedor.
    - fraud_city_pct_name: Nombre de la columna que se le asigna al porcentaje de fraude por ciudad.
    - fraud_state_pct_name: Nombre de la columna que se le asigna al porcentaje de fraude por estado.
    - fraud_merch_rank_name: Nombre de la columna que se le asigna al ranking de fraude por vendedor.
    - fraud_city_rank_name: Nombre de la columna que se le asigna al ranking de fraude por ciudad.
    - fraud_state_rank_name: Nombre de la columna que se le asigna al ranking de fraude por estado.

    Retorna:
    - DataFrame con las nuevas columnas de porcentaje de fraude y ranking añadidas.
    """
    # Cargar los datos de fraude desde los archivos CSV
    group_fraud_by_merch = pd.read_csv(group_merch_path)
    group_fraud_by_city = pd.read_csv(group_city_path)
    group_fraud_by_state = pd.read_csv(group_state_path)

    # Añadir columnas de porcentaje de fraude y ranking para: vendedor, ciudad y estado
    data = data.merge(
        group_fraud_by_merch[[merch_col_name, fraud_merch_pct_name, fraud_merch_rank_name]], 
        on=merch_col_name, 
        how='left'
    )
    data = data.merge(
        group_fraud_by_city[[city_col_name, fraud_city_pct_name, fraud_city_rank_name]], 
        on=city_col_name, 
        how='left'
    )
    data = data.merge(
        group_fraud_by_state[[state_col_name, fraud_state_pct_name, fraud_state_rank_name]], 
        on=state_col_name, 
        how='left'
    )

    return data

def catboost_model(
    features_scaled: pd.DataFrame, 
    target: pd.Series, 
    model
) -> tuple:
    """
    Genera predicciones utilizando un modelo CatBoost, evalúa el rendimiento del modelo y devuelve las predicciones, la precisión y un informe detallado de la clasificación.

    Parámetros:
    - features_scaled: DataFrame que contiene las características escaladas para el modelo.
    - target: Serie que contiene las etiquetas reales (verdaderas).
    - model: Modelo entrenado de CatBoost usado para hacer predicciones.

    Retorna:
    - Una tupla con las predicciones, la precisión del modelo y un DataFrame que contiene el informe de clasificación.

    Comportamiento:
    1. Realiza predicciones utilizando el modelo proporcionado.
    2. Calcula la precisión del modelo usando las etiquetas reales.
    3. Genera un informe detallado de clasificación, que incluye precisión, recall y F1-score para cada clase.
    """
    # Hacer predicciones
    predictions = model.predict(features_scaled)

    # Evaluar el modelo
    accuracy = accuracy_score(target, predictions)
    report = classification_report(target, predictions, output_dict=True)

    # Convertir el reporte de clasificación en un DataFrame
    report_df = pd.DataFrame(report).transpose()

    return predictions, accuracy, report_df

def config_sidebar(logo_img_path: str = './streamlit_app/logo.png') -> str:
    """
    Configura la barra lateral de la aplicación Streamlit.

    Parámetros:
    - logo_img_path: Ruta del archivo de imagen del logo que se mostrará en la barra lateral.
    
    Retorna:
    - El código de acceso ingresado por el usuario.
    """
    # Mostrar el logo en la barra lateral
    st.sidebar.image(logo_img_path, use_column_width='auto')

    # Descripción del proyecto en la barra lateral
    st.sidebar.title("Descripción del Proyecto")
    st.sidebar.write("""
    Este proyecto tiene como objetivo realizar predicciones de fraudes en transacciones con tarjeta de crédito y llevar a cabo un Análisis Exploratorio de los Datos.
    \n
    Por favor, ingresa el código de acceso para continuar.
    """)

    # Solicitar el código de acceso
    codigo_acceso = st.sidebar.text_input("Ingresa el código de acceso", type="password")
    
    return codigo_acceso

def datetime_split(
    data: pd.DataFrame, 
    datatime_col_name: str = 'trans_date_trans_time', 
    day_col_name: str = 'trans_day', 
    month_col_name: str = 'trans_month', 
    year_col_name: str = 'trans_year', 
    hour_col_name: str = 'trans_hour', 
    weekday_col_name: str = 'trans_weekday'
) -> pd.DataFrame:
    """
    Divide una columna de datetime en varias columnas que contienen información del día, mes, año, hora y día de la semana.

    Parámetros:
    - data: DataFrame que contiene la columna de tipo datetime.
    - datatime_col_name: Nombre de la columna datetime a dividir. Por defecto 'trans_date_trans_time'.
    - day_col_name: Nombre de la nueva columna que contendrá el día del mes. Por defecto 'trans_day'.
    - month_col_name: Nombre de la nueva columna que contendrá el mes. Por defecto 'trans_month'.
    - year_col_name: Nombre de la nueva columna que contendrá el año. Por defecto 'trans_year'.
    - hour_col_name: Nombre de la nueva columna que contendrá la hora. Por defecto 'trans_hour'.
    - weekday_col_name: Nombre de la nueva columna que contendrá el día de la semana (0=lunes, 6=domingo). Por defecto 'trans_weekday'.

    Retorna:
    - DataFrame con nuevas columnas que contienen el día, mes, año, hora y día de la semana.
    """
    # Transformar la columna a tipo datetime para el procesado
    data[datatime_col_name] = pd.to_datetime(data[datatime_col_name])

    # Crear nuevas columnas para día, mes, año, hora y día de la semana
    data[day_col_name] = data[datatime_col_name].dt.day
    data[month_col_name] = data[datatime_col_name].dt.month
    data[year_col_name] = data[datatime_col_name].dt.year
    data[hour_col_name] = data[datatime_col_name].dt.hour
    data[weekday_col_name] = data[datatime_col_name].dt.weekday

    return data

def db_conn() -> object:
    """
    Crea y retorna una conexión a una base de datos PostgreSQL utilizando las credenciales almacenadas en las variables de entorno.

    Retorna:
    - engine: Un objeto de SQLAlchemy Engine que representa la conexión a la base de datos.

    Comportamiento:
    1. Obtiene las variables de entorno necesarias para la conexión a la base de datos.
    2. Construye una URL de conexión usando estas variables.
    3. Crea y retorna un objeto de SQLAlchemy Engine para conectar con la base de datos PostgreSQL.
    """
    # Obtener las variables de entorno
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    
    # Verificar que todas las variables de entorno están presentes
    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError("Faltan variables de entorno necesarias para la conexión a la base de datos.")
    
    # Crear la URL de conexión
    connection_url = (
        f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )

    # Crear y retornar el engine de SQLAlchemy
    engine = create_engine(connection_url)

    return engine

def dob_to_age(
    data: pd.DataFrame, 
    dob_col_name: str = 'dob', 
    age_col_name: str = 'age'
) -> pd.DataFrame:
    """
    Convierte una columna de fechas de nacimiento (DOB=date of birth) en una columna de edades en años.

    Parámetros:
    - data: DataFrame que contiene una columna con fechas de nacimiento.
    - dob_col_name: Nombre de la columna que contiene las fechas de nacimiento (por defecto 'dob').
    - age_col_name: Nombre de la nueva columna donde se almacenarán las edades calculadas (por defecto 'age').

    Retorna:
    - DataFrame con una nueva columna que contiene las edades en años.
    """
    
    # Transformar la columna de fechas de nacimiento a tipo datetime, ignorando valores inválidos
    data[dob_col_name] = pd.to_datetime(data[dob_col_name], errors='coerce')

    # Obtener la fecha actual
    actual_date = pd.to_datetime(datetime.now().date())

    # Calcular la edad en años para los registros válidos
    data[age_col_name] = ((actual_date - data[dob_col_name]).dt.days / 365.25).astype('int')

    return data

def extract_zip_to_csv(uploaded_file, temp_dir: str) -> list:
    """
    Extrae un archivo ZIP subido, busca archivos CSV dentro y devuelve una lista de sus nombres.

    Parámetros:
    - uploaded_file: El archivo ZIP subido (por ejemplo, a través de una interfaz web).
    - temp_dir: Directorio temporal donde se guardará y extraerá el contenido del archivo ZIP.

    Retorna:
    - Una lista con los nombres de los archivos CSV extraídos.

    Comportamiento:
    1. Guarda el archivo ZIP en el directorio temporal.
    2. Descomprime el archivo ZIP en el mismo directorio.
    3. Busca y retorna todos los archivos con extensión .csv encontrados.
    """
    # Definir la ruta temporal donde se guardará el archivo zip
    zip_path = os.path.join(temp_dir, "temp.zip")

    # Guardar el archivo zip subido en el directorio temporal
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    # Descomprimir el archivo zip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Buscar todos los archivos CSV extraídos
    extracted_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]

    return extracted_files

def frauds_per_day(
    data: pd.DataFrame, 
    datatime_col_name: str = 'trans_date_trans_time',
    fraud_col_name: str = 'is_fraud',
    total_trans_col_name: str = 'total_transacciones'
) -> pd.DataFrame:
    """
    Calcula el número de fraudes por día a partir de una columna de fechas y devuelve un DataFrame con los totales por día.

    Parámetros:
    - data: DataFrame que contiene las transacciones, incluyendo una columna con la fecha y una columna de fraude.
    - datatime_col_name: Nombre de la columna que contiene la fecha de la transacción, en formato datetime.
    - fraud_col_name: Nombre de la columna que contiene el flag del fraude, 0 o 1. 
    - total_tran_col_name: Nombre de la columna que contendrá el total de transacciones. 


    Retorna:
    - DataFrame con el total de transacciones fraudulentas por día.
    """
    # Asegurarse de que la columna de fechas esté en formato datetime
    data[datatime_col_name] = pd.to_datetime(data[datatime_col_name])

    # Filtrar solo las transacciones que son fraudes
    data_frauds = data[data[fraud_col_name] == 1][[datatime_col_name, fraud_col_name]].copy()

    # Establecer la columna de fechas como índice
    data_frauds.set_index(datatime_col_name, inplace=True)

    # Agrupar por día y contar el número de fraudes
    frauds_per_day = data_frauds.resample('D').size().reset_index(name=total_trans_col_name)

    return frauds_per_day

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia en línea recta entre dos puntos en la superficie de la Tierra,
    utilizando la fórmula del Haversine.

    Parámetros:
    - lat1: Latitud del primer punto en grados.
    - lon1: Longitud del primer punto en grados.
    - lat2: Latitud del segundo punto en grados.
    - lon2: Longitud del segundo punto en grados.

    Retorna:
    - La distancia entre los dos puntos en kilómetros.
    """
    # Radio de la Tierra en kilómetros
    R = 6371.0

    # Convertir grados a radianes
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Diferencias de coordenadas
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Fórmula del Haversine
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distancia final en kilómetros
    distance = R * c

    return distance

def job_encoder(data: pd.DataFrame, job_freq_path: str = 'streamlit_app/job_freq.csv') -> pd.DataFrame:
    """
    Codifica la columna de trabajos en el DataFrame original utilizando la frecuencia de profesiones de un archivo CSV.

    Parámetros:
    - data: DataFrame principal al que se le añadirá la columna codificada de trabajos.
    - job_freq_path: Ruta al archivo CSV que contiene la frecuencia de las profesiones y sus proporciones.

    Retorna:
    - DataFrame con una nueva columna 'job_encoded' basada en la proporción de cada trabajo.
    """
    # Cargar el DataFrame con la frecuencia de las profesiones
    job_freq = pd.read_csv(job_freq_path)

    # Unir el DataFrame de frecuencias con el DataFrame original
    data = data.merge(job_freq, on='job', how='left')

    # Renombrar la columna 'proportion' a 'job_encoded'
    data.rename(columns={'proportion': 'job_encoded'}, inplace=True)

    return data

def load_data_from_zip(key: str = '1') -> tuple:
    """
    Carga un archivo .zip subido por el usuario y verifica si se ha subido con éxito.

    Parámetros:
    - key: Clave única para el widget de carga de archivos en Streamlit.

    Retorna:
    - success_file: Booleano que indica si el archivo fue subido con éxito.
    - uploaded_file: El archivo .zip subido por el usuario, o None si no se subió ningún archivo.
    """
    # Crear el objeto de carga del archivo tipo .zip
    uploaded_file = st.file_uploader("Sube tu archivo CSV en formato .zip", type=["zip"], key=key)
    
    success_file = False

    # Si el archivo no está vacío, continua
    if uploaded_file is not None:
        st.success("Archivo subido con éxito!")
        success_file = True
    else:
        st.warning("Por favor ingrese un archivo")

    return success_file, uploaded_file

def ohe_data(data, ohe_path='streamlit_app/onehotencoder.pkl', cols_to_transform=['category', 'gender']):
    # One Hot Encoding para las categorias sin orden 
    encoder = joblib.load(ohe_path) # Cargar el codificador desde el archivo
    data_ohe = encoder.transform(data[cols_to_transform])
    return data_ohe

def ohe_data(
    data: pd.DataFrame,
    ohe_path: str = 'streamlit_app/onehotencoder.pkl',
    cols_to_transform: List[str] = ['category', 'gender']
) -> pd.DataFrame:
    """
    Aplica One Hot Encoding a las columnas especificadas de un DataFrame utilizando un codificador previamente entrenado.

    Parámetros:
    - data: DataFrame que contiene las columnas que se desean transformar.
    - ohe_path: Ruta al archivo que contiene el codificador One Hot Encoder entrenado.
    - cols_to_transform: Lista de nombres de columnas a las que se aplicará el One Hot Encoding.

    Retorna:
    - DataFrame con las columnas transformadas mediante One Hot Encoding.
    """
    # Cargar el codificador One Hot Encoder desde el archivo
    encoder = joblib.load(ohe_path)
    
    # Aplicar One Hot Encoding a las columnas especificadas
    data_ohe = encoder.transform(data[cols_to_transform])

    # Reconstruir el dataframe
    col_names = ['category_food_dining', 'category_gas_transport',
       'category_grocery_net', 'category_grocery_pos',
       'category_health_fitness', 'category_home', 'category_kids_pets',
       'category_misc_net', 'category_misc_pos', 'category_personal_care',
       'category_shopping_net', 'category_shopping_pos', 'category_travel',
       'gender_M']
    data_ohe = pd.DataFrame(data_ohe, columns=col_names)
    data_ohe = pd.concat([data, data_ohe], axis=1)
    
    return data_ohe