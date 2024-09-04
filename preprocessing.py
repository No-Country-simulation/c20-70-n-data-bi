import pandas as pd
from utils import assign_sector, datetime_split, dob_to_age, fraud_pct_by_column, haversine_distance

def preprocessing_data(data):
    # Añadir columnas de porcentaje de fraude y ranking para: vendedor, ciudad y estado
    data = fraud_pct_by_column(data, 'merchant', 'is_fraud', 'fraud_merch_pct', 'fraud_merch_rank')
    data = fraud_pct_by_column(data, 'city', 'is_fraud', 'fraud_city_pct', 'fraud_city_rank')
    data = fraud_pct_by_column(data, 'state', 'is_fraud', 'fraud_state_pct', 'fraud_state_rank')

    # Aplicar la función de reemplazo de profesiones por sector (Para visualización) y realizar un encoded por la frecuencia (para el modelo)
    data['job_sector'] = data['job'].apply(assign_sector)
    job_freq = data['job'].value_counts(normalize=True)
    data['job_encoded'] = data['job'].map(job_freq)

    # Dividir la columna de la fecha/hora en columnas separadas para: día del mes, mes, año, hora, día de la semana. 
    data = datetime_split(data, 'trans_date_trans_time', 'trans_day', 'trans_month', 'trans_year', 'trans_hour', 'trans_weekday')

    # Transformar la fecha de nacimiento en edad
    data = dob_to_age(data, 'dob', 'age')

    # Crear una nueva columna con la distancia entre el vendedor y el comprador
    data["distance_to_merch"] = data.apply(lambda row: haversine_distance(row['lat'], row['long'], row['merch_lat'], row['merch_long']), axis=1)

    # One Hot Encoding para las categorias sin orden 
    data_ohe = pd.get_dummies(data, columns=['category', 'gender'], drop_first=True)

    # Eliminar columnas redundantes o con poca información para el modelo
    data_ohe.drop(columns=['Unnamed: 0', 'cc_num', 'first', 'last', 'street', 'unix_time', 'trans_num',
                           'merchant', 'city', 'state', 'job', 'job_sector', 'trans_date_trans_time', 
                           'dob', 'lat', 'long', 'merch_lat', 'merch_long'], axis=1, inplace=True)

    return data_ohe