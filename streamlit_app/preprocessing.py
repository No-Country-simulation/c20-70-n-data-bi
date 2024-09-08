import pandas as pd
from utils import calc_pct_n_rank, datetime_split, dob_to_age, haversine_distance, job_encoder, ohe_data

def preprocessing_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesa un DataFrame realizando varias transformaciones de datos.

    Parámetros:
    - data: DataFrame que contiene datos a procesar.

    Retorna:
    - DataFrame preprocesado con características transformadas y columnas redundantes eliminadas.
    """
    
    # Calcular el porcentaje y rango de fraude de los vendedores, ciudades y estados.
    data = calc_pct_n_rank(data)

    # Transformar la profesión en números basados en la frecuencia.
    data = job_encoder(data)

    # Dividir la columna de fecha/hora en columnas separadas para día del mes, mes, año, hora y día de la semana.
    data = datetime_split(data)

    # Transformar la fecha de nacimiento en edad.
    data = dob_to_age(data)

    # Crear una nueva columna con la distancia entre el vendedor y el comprador.
    data["distance_to_merch"] = data.apply(
        lambda row: haversine_distance(row['lat'], row['long'], row['merch_lat'], row['merch_long']), axis=1
    )

    # Convertir las columnas categóricas usando One Hot Encoding.
    data_ohe = ohe_data(data)

    # Eliminar columnas redundantes o con poca información para el modelo.
    columns_to_drop = [
        'Unnamed: 0', 'cc_num', 'first', 'last', 'street', 'unix_time', 'trans_num',
        'merchant', 'city', 'state', 'job', 'trans_date_trans_time',
        'dob', 'lat', 'long', 'merch_lat', 'merch_long', 'category', 'gender'
    ]
    data_ohe.drop(columns=columns_to_drop, axis=1, inplace=True)
    
    return data_ohe