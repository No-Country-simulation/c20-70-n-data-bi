import pandas as pd
from utils import assign_sector, datetime_split, dob_to_age, haversine_distance
import joblib

def preprocessing_data(data):

   # Carga de dataframes
   group_fraud_by_merch = pd.read_csv('streamlit_app/group_fraud_by_merch.csv')
   group_fraud_by_city = pd.read_csv('streamlit_app/group_fraud_by_city.csv')
   group_fraud_by_state = pd.read_csv('streamlit_app/group_fraud_by_state.csv')
   job_freq = pd.read_csv('streamlit_app/job_freq.csv')

   # Añadir columnas de porcentaje de fraude y ranking para: vendedor, ciudad y estado
   data = data.merge(group_fraud_by_merch[['merchant', 'fraud_merch_pct', 'fraud_merch_rank']], on='merchant',how='left')  
   data = data.merge(group_fraud_by_city[['city', 'fraud_city_pct', 'fraud_city_rank']], on='city',how='left') 
   data = data.merge(group_fraud_by_state[['state', 'fraud_state_pct', 'fraud_state_rank']], on='state',how='left') 

   # Aplicar la función de reemplazo de profesiones por sector (Para visualización) y realizar un encoded por la frecuencia (para el modelo)
   data['job_sector'] = data['job'].apply(assign_sector)

   # Unirlo con el df original
   data = data.merge(job_freq, on='job',how='left')
   data.rename(columns={'proportion': 'job_encoded'}, inplace=True) # Renombrar la columna

   # Dividir la columna de la fecha/hora en columnas separadas para: día del mes, mes, año, hora, día de la semana. 
   data = datetime_split(data, 'trans_date_trans_time', 'trans_day', 'trans_month', 'trans_year', 'trans_hour', 'trans_weekday')

   # Transformar la fecha de nacimiento en edad
   data = dob_to_age(data, 'dob', 'age')

   # Crear una nueva columna con la distancia entre el vendedor y el comprador
   data["distance_to_merch"] = data.apply(lambda row: haversine_distance(row['lat'], row['long'], row['merch_lat'], row['merch_long']), axis=1)

   # One Hot Encoding para las categorias sin orden 
   encoder = joblib.load('streamlit_app/onehotencoder.pkl') # Cargar el codificador desde el archivo
   #data_ohe = pd.get_dummies(data, columns=['category', 'gender'], drop_first=True)
   data_ohe = encoder.transform(data[['category', 'gender']])
   # Reconstruir el dataframe
   col_names = ['category_food_dining', 'category_gas_transport',
       'category_grocery_net', 'category_grocery_pos',
       'category_health_fitness', 'category_home', 'category_kids_pets',
       'category_misc_net', 'category_misc_pos', 'category_personal_care',
       'category_shopping_net', 'category_shopping_pos', 'category_travel',
       'gender_M']
   data_ohe = pd.DataFrame(data_ohe, columns=col_names)
   data_ohe = pd.concat([data, data_ohe], axis=1)

   # Eliminar columnas redundantes o con poca información para el modelo
   data_ohe.drop(columns=['Unnamed: 0', 'cc_num', 'first', 'last', 'street', 'unix_time', 'trans_num',
                           'merchant', 'city', 'state', 'job', 'job_sector', 'trans_date_trans_time', 
                           'dob', 'lat', 'long', 'merch_lat', 'merch_long', 'category', 'gender'], axis=1, inplace=True)

   return data_ohe